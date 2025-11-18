"""
SkillBridge - Sistema de Recomendação de Carreira com ML
FIAP Global Solution 2025
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
import json

# Configurar paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTROLLER_DIR = os.path.join(BASE_DIR, 'controller')
sys.path.insert(0, CONTROLLER_DIR)

app = Flask(__name__, 
            template_folder=CONTROLLER_DIR,
            static_folder=BASE_DIR)

# Variável global para o preditor
predictor = None

# Tentar carregar o preditor
try:
    from ml_predictor import MLPredictor
    predictor = MLPredictor()
    print("✅ Preditor carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar preditor: {e}")
    predictor = None


@app.route('/')
def index():
    """Página inicial - formulário"""
    return render_template('dashboard.html')


@app.route('/status-modelos', methods=['GET'])
def status_modelos():
    """Endpoint para verificar se os modelos estão treinados"""
    if predictor is None:
        return jsonify({
            'modelos_treinados': False,
            'mensagem': 'Preditor não carregado'
        })
    
    # Verificar se tem modelos carregados
    modelos_ok = (
        len(predictor.clf_models) > 0 and 
        len(predictor.reg_models) > 0
    )
    
    return jsonify({
        'modelos_treinados': modelos_ok,
        'num_modelos_clf': len(predictor.clf_models),
        'num_modelos_reg': len(predictor.reg_models),
        'modelos_clf': list(predictor.clf_models.keys()),
        'modelos_reg': list(predictor.reg_models.keys())
    })


@app.route('/analisar-perfil', methods=['POST'])
def analisar_perfil():
    """Endpoint principal - recebe dados do formulário e retorna predições ML"""
    try:
        # Verificar se preditor está disponível
        if predictor is None:
            return jsonify({
                'success': False,
                'message': 'Modelos ML não carregados. Execute: python controller/treinar_via_api.py'
            }), 500
        
        # Receber dados do formulário
        dados = request.get_json()
        
        print("\n" + "="*70)
        print("📝 Dados recebidos do formulário:")
        print(json.dumps(dados, indent=2, ensure_ascii=False))
        print("="*70)
        
        # Fazer predições ML
        predicoes = predictor.prever(dados)
        
        # Buscar cursos recomendados
        from database import firebase_db
        
        area_recomendada = predicoes['recomendacao_final']['area_recomendada']
        habilidades = dados.get('habilidades_atuais_hard', [])
        
        cursos = firebase_db.buscar_cursos_filtrados(
            area_interesse=area_recomendada,
            habilidades=habilidades
        )
        
        # Limitar a 10 cursos
        cursos_top = cursos[:10] if cursos else []
        
        # Montar resposta completa
        resposta = {
            'success': True,
            'perfil': {
                'profissao_atual': dados.get('profissao_atual'),
                'anos_experiencia': dados.get('anos_experiencia'),
                'objetivo_principal': dados.get('objetivo_principal'),
                'tempo_disponivel_estudo': dados.get('tempo_disponivel_estudo'),
                'num_habilidades': len(habilidades),
                'nivel_atual': _definir_nivel(dados.get('anos_experiencia', 0))
            },
            'predicoes': predicoes,
            'cursos_recomendados': cursos_top,
            'resultados_treinamento': predictor.resultados_treinamento
        }
        
        print("\n✅ Análise concluída com sucesso!")
        print(f"   🎯 Área recomendada: {area_recomendada}")
        print(f"   📊 Score: {predicoes['recomendacao_final']['score_adequacao']:.2f}")
        print(f"   📚 Cursos encontrados: {len(cursos_top)}")
        
        return jsonify(resposta)
        
    except Exception as e:
        print(f"\n❌ Erro ao analisar perfil: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'message': f'Erro ao processar análise: {str(e)}'
        }), 500


@app.route('/resultados')
def resultados():
    """Página de resultados - mostra as predições ML"""
    try:
        # Dados viriam do localStorage do navegador
        # Mas para o servidor renderizar, precisamos passar dados dummy ou redirecionar
        return render_template('resultados_ml.html', dados={
            'perfil': {},
            'predicoes': {
                'classificacao': {},
                'regressao': {},
                'recomendacao_final': {}
            },
            'cursos_recomendados': [],
            'resultados_treinamento': {}
        })
    except Exception as e:
        return f"Erro ao carregar página de resultados: {e}", 500


@app.route('/visualizations/<path:filename>')
def serve_visualization(filename):
    """Servir visualizações geradas"""
    viz_dir = os.path.join(BASE_DIR, 'visualizations')
    return send_from_directory(viz_dir, filename)


def _definir_nivel(anos_exp):
    """Define o nível profissional baseado nos anos de experiência"""
    anos_exp = int(anos_exp)
    if anos_exp < 3:
        return 'Júnior'
    elif anos_exp < 7:
        return 'Pleno'
    else:
        return 'Sênior'


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎓 SKILLBRIDGE iniciado!")
    print("Acesse: http://localhost:5000")
    print("="*70)
    
    # Usar use_reloader=False para evitar reinicializações durante requisições
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True  # Mantém hot reload, mas pode ser definido como False em produção
    )
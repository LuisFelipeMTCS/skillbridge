"""
Sistema SkillBridge - Recomendação de Carreira com Machine Learning
FIAP Global Solution 2025 - Futuro do Trabalho

Aplicação Flask reformulada para:
✔ Enviar dados diretamente ao template resultados_ml.html
✔ Remover endpoints obsoletos
✔ Fluxo mais simples e funcional
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import sys
from datetime import datetime

# -------------------------------------------------------------------
# CONFIGURAÇÕES DE DIRETÓRIOS
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTROLLER_DIR = os.path.join(BASE_DIR, 'controller')
sys.path.insert(0, CONTROLLER_DIR)

DATA_FOLDER = os.path.join(BASE_DIR, 'data')
MODELS_FOLDER = os.path.join(BASE_DIR, 'models')

from ml_predictor import MLPredictor


# -------------------------------------------------------------------
# INICIALIZA FLASK
# -------------------------------------------------------------------
app = Flask(__name__, template_folder=CONTROLLER_DIR)

predictor = None


# -------------------------------------------------------------------
# FUNÇÃO PARA CARREGAR PREDITOR
# -------------------------------------------------------------------
def carregar_preditor():
    """Carrega os modelos ML caso existam"""
    global predictor

    if predictor is not None:
        return

    if not os.path.exists(MODELS_FOLDER):
        print("⚠️ Modelos ainda não foram treinados.")
        return

    try:
        predictor = MLPredictor()
        print("✅ Preditor carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar preditor: {e}")
        predictor = None


# -------------------------------------------------------------------
# PAGINA PRINCIPAL
# -------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('dashboard.html')


# -------------------------------------------------------------------
# PROCESSAR FORMULÁRIO E RENDERIZAR RESULTADOS
# -------------------------------------------------------------------
@app.route('/analisar-perfil', methods=['POST'])
def analisar_perfil():
    try:
        # Carregar preditor
        if predictor is None:
            carregar_preditor()

        if predictor is None:
            return render_template(
                "resultados_ml.html",
                dados={'erro': 'Modelos não foram treinados. Execute "Treinar Modelos".'}
            )

        # Obter dados do front-end
        formulario = request.json

        print("\n" + "="*70)
        print("📝 Dados recebidos do formulário:")
        print(json.dumps(formulario, indent=2, ensure_ascii=False))
        print("="*70)

        # Predição
        predicoes = predictor.prever(formulario)
        resultados_treinamento = predictor.obter_resultados_treinamento()

        area_recomendada = predicoes['recomendacao_final']['area_recomendada']
        cursos_recomendados = obter_cursos_por_area(area_recomendada)

        dados_resposta = {
            'perfil': {
                'profissao_atual': formulario.get('profissao_atual', '-'),
                'anos_experiencia': formulario.get('anos_experiencia', 0),
                'nivel_atual': determinar_nivel(int(formulario.get('anos_experiencia', 0))),
                'objetivo_principal': formulario.get('objetivo_principal', '-'),
                'tempo_disponivel_estudo': formulario.get('tempo_disponivel_estudo', '-'),
                'num_habilidades': len(formulario.get('habilidades_atuais_hard', []))
            },
            'predicoes': predicoes,
            'resultados_treinamento': resultados_treinamento,
            'cursos_recomendados': cursos_recomendados[:10]
        }

        print(f"\n🎯 Área Recomendada: {area_recomendada}")
        print(f"📊 Score: {predicoes['recomendacao_final']['score_adequacao']:.2f}")
        print("="*70 + "\n")

        # AQUI ESTÁ A CORREÇÃO PRINCIPAL:
        return render_template("resultados_ml.html", dados=dados_resposta)

    except Exception as e:
        print(f"❌ Erro ao analisar perfil: {e}")
        return render_template("resultados_ml.html", dados={'erro': str(e)})


# -------------------------------------------------------------------
# TREINAR MODELOS
# -------------------------------------------------------------------
@app.route('/treinar-modelos', methods=['POST'])
def treinar_modelos():
    try:
        print("\n🚀 Iniciando treinamento dos modelos ML...\n")

        from data_generator import DataGenerator
        from ml_models import MLModels

        generator = DataGenerator()
        df = generator.gerar_dataset(n_amostras=1000)

        os.makedirs(DATA_FOLDER, exist_ok=True)
        dataset_path = os.path.join(DATA_FOLDER, 'dataset_profissionais.csv')
        generator.salvar_dataset(df, dataset_path)

        ml = MLModels(dataset_path)
        ml.carregar_dados()
        dados_proc = ml.preprocessar_dados()
        ml.treinar_modelos_classificacao(dados_proc)
        ml.treinar_modelos_regressao(dados_proc)

        os.makedirs(MODELS_FOLDER, exist_ok=True)
        ml.salvar_modelos(MODELS_FOLDER)

        visual_dir = os.path.join(BASE_DIR, 'visualizations')
        os.makedirs(visual_dir, exist_ok=True)
        ml.gerar_visualizacoes(visual_dir)

        # Recarregar preditor
        global predictor
        predictor = None
        carregar_preditor()

        print("✅ Treinamento concluído!")
        return jsonify({'success': True, 'message': 'Modelos treinados com sucesso!'})

    except Exception as e:
        print(f"❌ Erro ao treinar modelos: {e}")
        return jsonify({'success': False, 'message': str(e)})


# -------------------------------------------------------------------
# FILTRAR CURSOS
# -------------------------------------------------------------------
def obter_cursos_por_area(area):
    try:
        cursos_path = os.path.join(DATA_FOLDER, 'cursos_alura.json')

        if not os.path.exists(cursos_path):
            return []

        with open(cursos_path, 'r', encoding='utf-8') as f:
            todos_cursos = json.load(f)

        keywords_por_area = {
            'Desenvolvimento Web': ['web', 'html', 'css', 'javascript', 'react'],
            'Data Science': ['data', 'dados', 'python', 'machine learning'],
            'DevOps': ['devops', 'docker', 'kubernetes'],
            'Mobile': ['mobile', 'android', 'ios'],
            'UX/UI Design': ['ux', 'ui', 'design', 'figma'],
            'Segurança da Informação': ['segurança', 'security'],
            'Cloud Computing': ['cloud', 'aws', 'azure'],
            'Inteligência Artificial': ['ia', 'ai', 'deep learning']
        }

        keywords = keywords_por_area.get(area, [])

        cursos_filtrados = []
        for curso in todos_cursos:
            texto = f"{curso.get('titulo', '')} {curso.get('aprendizado', '')} {curso.get('publico_alvo', '')}".lower()
            if any(kw in texto for kw in keywords):
                curso['area'] = area
                cursos_filtrados.append(curso)

        return cursos_filtrados

    except:
        return []


# -------------------------------------------------------------------
# DETERMINAR NÍVEL COM BASE NA EXPERIÊNCIA
# -------------------------------------------------------------------
def determinar_nivel(anos_exp):
    if anos_exp < 3:
        return 'Júnior'
    elif anos_exp < 7:
        return 'Pleno'
    return 'Sênior'


# -------------------------------------------------------------------
# RUN
# -------------------------------------------------------------------
if __name__ == '__main__':
    carregar_preditor()

    print("\n🎓 SKILLBRIDGE iniciado!")
    print("Acesse: http://localhost:5000")
    print("="*70)

    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, jsonify
import json
import os
import sys
from datetime import datetime

# ✅ ADICIONAR O DIRETÓRIO SRC AO PATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'controller'))

# ✅ AGORA OS IMPORTS FUNCIONAM
from gpt_recommender import montar_input, recommender
from save_pdf import salvar_pdf_organizado

app = Flask(__name__, template_folder='../controller')

# Configurações
DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')

@app.route('/')
def index():
    """Renderiza a página principal com o formulário"""
    return render_template('dashboard.html')

@app.route('/gerar-plano', methods=['POST'])
def gerar_plano():
    """Recebe os dados do formulário e gera o plano de carreira em PDF"""
    try:
        # Receber dados do formulário
        formulario = request.json
        
        print("📝 Dados recebidos do formulário:")
        print(json.dumps(formulario, indent=2, ensure_ascii=False))
        
        # Verificar se o arquivo de cursos existe
        cursos_path = os.path.join(DATA_FOLDER, 'cursos_alura.json')
        if not os.path.exists(cursos_path):
            return jsonify({
                'success': False,
                'message': 'Arquivo de cursos não encontrado. Execute primeiro o scraper.'
            }), 400
        
        # Montar input para o recomendador
        input_data = montar_input(formulario)
        
        print("\n🤖 Gerando recomendações com IA...")
        
        # Gerar recomendações
        texto_plano = recommender(input_data)
        
        print("\n📄 Gerando PDF...")
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        profissao = formulario.get('profissao_atual', 'Profissional').replace(' ', '_')
        nome_arquivo = f"Plano_Carreira_{profissao}_{timestamp}.pdf"
        
        # Salvar PDF
        caminho_pdf = salvar_pdf_organizado(texto_plano, nome_arquivo)
        
        return jsonify({
            'success': True,
            'message': 'Plano de carreira gerado com sucesso!',
            'arquivo': nome_arquivo,
            'caminho': caminho_pdf
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar plano: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar plano: {str(e)}'
        }), 500

@app.route('/cursos-disponiveis')
def cursos_disponiveis():
    """Retorna a lista de cursos disponíveis"""
    try:
        cursos_path = os.path.join(DATA_FOLDER, 'cursos_alura.json')
        with open(cursos_path, 'r', encoding='utf-8') as f:
            cursos = json.load(f)
        return jsonify({'success': True, 'cursos': cursos, 'total': len(cursos)})
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'message': 'Arquivo de cursos não encontrado. Execute o scraper primeiro.'
        }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/executar-scraper', methods=['POST'])
def executar_scraper():
    """Executa o scraper para coletar cursos da Alura"""
    try:
        # Importar o scraper
        scraper_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, scraper_path)
        import alura_scraper
        
        print("🔍 Iniciando scraper da Alura...")
        alura_scraper.extrair_todos_detalhes()
        
        return jsonify({
            'success': True,
            'message': 'Cursos coletados com sucesso!'
        })
        
    except Exception as e:
        print(f"❌ Erro ao executar scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro ao executar scraper: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Iniciando Sistema de Recomendação de Carreira - Alura")
    print("=" * 60)
    print("📱 Acesse: http://localhost:5000")
    print("=" * 60)
    print(f"📂 Pasta src: {os.path.join(os.path.dirname(__file__), '..', 'src')}")
    print(f"📂 Pasta data: {DATA_FOLDER}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
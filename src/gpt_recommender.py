import google.generativeai as genai
import json
import os
import os
from dotenv import load_dotenv  # ✅ ADICIONAR ESTA LINHA

# ✅ CARREGAR VARIÁVEIS DE AMBIENTE DO ARQUIVO .env
load_dotenv()
def montar_input(formulario):
    """Transforma os dados do formulário em input_data para o recommender"""
    
    input_data = {
        "profissao": formulario.get("profissao_atual"),
        "anos_experiencia": formulario.get("anos_experiencia"),
        "nivel": formulario.get("nivel_atual"),
        "habilidades_atuais": formulario.get("habilidades_atuais_hard", []),
        "disponibilidade_estudo": formulario.get("tempo_disponivel_estudo"),
    }
    
    objetivo_principal = formulario.get("objetivo_principal")
    
    if objetivo_principal == "Atualizar Carreira":
        input_data["area_interesse"] = formulario.get("area_especializacao_desejada")
        input_data["objetivo"] = formulario.get("objetivo_curto_prazo")
    elif objetivo_principal == "Realocar Carreira":
        input_data["area_interesse"] = formulario.get("nova_area_interesse")
        input_data["objetivo"] = "Realocacao de Carreira"
        input_data["soft_skills_transferiveis"] = formulario.get("habilidades_transferiveis_soft", [])
        input_data["motivacao_realocacao"] = formulario.get("motivacao_realocacao", [])
        input_data["experiencia_nao_tech"] = formulario.get("experiencia_nao_tech_relevante", "")
        input_data["faixa_salarial_desejada"] = formulario.get("faixa_salarial_desejada")
    
    return input_data

def recommender(input_data):
    """Gera um plano de ação completo (VERSÃO RÁPIDA)"""
    
    # Carregar cursos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cursos_path = os.path.join(script_dir, '..', 'data', 'cursos_alura.json')
    
    try:
        with open(cursos_path, "r", encoding="utf-8") as f:
            cursos = json.load(f)
    except FileNotFoundError:
        return "Erro: Base de dados de cursos nao encontrada."
    
    # Filtrar cursos relevantes
    area_interesse = input_data.get("area_interesse", "").lower()
    habilidades = [h.lower() for h in input_data.get("habilidades_atuais", [])]
    
    cursos_relevantes = []
    for curso in cursos:
        titulo = curso.get("titulo", "").lower()
        aprendizado = curso.get("aprendizado", "").lower()
        publico = curso.get("publico_alvo", "").lower()
        
        if area_interesse and area_interesse in (titulo + aprendizado + publico):
            cursos_relevantes.append(curso)
        elif any(skill in (titulo + aprendizado) for skill in habilidades):
            cursos_relevantes.append(curso)
    
    if not cursos_relevantes:
        cursos_relevantes = cursos[:30]
    
    # ✅ LIMITAR A 20 CURSOS PARA VELOCIDADE
    cursos_relevantes = cursos_relevantes[:20]
    
    API_KEY = os.getenv("GEMINI_API_KEY")
    
    try:
        genai.configure(api_key=API_KEY)
        
        # ✅ PROMPT MAIS CONCISO
        cursos_texto = "\n".join([
            f"{i+1}. {curso.get('titulo', 'Sem titulo')} - {curso.get('url', 'N/A')}"
            for i, curso in enumerate(cursos_relevantes[:15])
        ])
        
        prompt = f"""Crie um plano de carreira CONCISO para:
            Profissional: {input_data.get('profissao')} ({input_data.get('nivel')})
            Habilidades: {', '.join(input_data.get('habilidades_atuais', []))}
            Objetivo: {input_data.get('area_interesse')}

            Cursos disponiveis:
            {cursos_texto}

            ESTRUTURA (seja DIRETO e OBJETIVO):

            1. INTRODUCAO
            [2 paragrafos breves]

            2. PERFIL DO PROFISSIONAL
            - Funcao: {input_data.get('profissao')}
            - Nivel: {input_data.get('nivel')}
            - Habilidades: {', '.join(input_data.get('habilidades_atuais', []))}
            - Objetivo: {input_data.get('objetivo')}

            3. CURSOS RECOMENDADOS
            Selecione os 8 melhores cursos da lista. Para cada:
            1. [Nome do curso]:
            URL: [link exato]
            Aprendizado: [top 3 skills em 1 linha]

            4. LINHA DE CARREIRA PERSONALIZADA
            6 etapas numeradas (cada uma com 4 linhas max):
            1. [Nome do curso]
            Habilidades: [lista]
            Duracao: [tempo]
            Relevancia: [1 frase]

            5. PLANO DE ACAO FINAL
            - Ordem de execucao (lista simples)
            - 3 projetos praticos (1 linha cada)
            - Dicas de portfolio (3 itens)
            - 2 certificacoes extras
            - Dicas para entrevistas (3 itens)

            REGRAS:
            - Sem acentos
            - Use URLs reais da lista
            - Maximo 2 linhas por item
            - Seja direto e pratico"""
        
        # ✅ USAR MODELO MAIS RÁPIDO
        model = genai.GenerativeModel("gemini-2.0-flash")  # Mais rápido que 2.5
        
        print(f"🚀 Usando modelo rápido: gemini-2.0-flash")
        response = model.generate_content(prompt)
        print(f"✅ Resposta gerada com sucesso!")
        
        return response.text
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return f"Erro ao gerar recomendacoes: {str(e)}"
import requests
from lxml import html
import json
import os

BASE_URL = "https://www.alura.com.br"
LISTA_CURSOS_URL = f"{BASE_URL}/cursos-online-tecnologia"


def extrair_links_alura(url=LISTA_CURSOS_URL):
    response = requests.get(url)
    response.raise_for_status()

    tree = html.fromstring(response.content)
    links = tree.xpath('//a[contains(@class, "card-curso")]/@href')
    links_completos = [BASE_URL + link for link in set(links)]
    return links_completos


def extrair_detalhes_curso(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        titulo = tree.xpath('string(//h1[contains(@class, "curso-banner-course-title")])').strip()

        aprendizado = tree.xpath('//ul[@class="course-list"]/li/text()')
        aprendizado_texto = " | ".join([a.strip() for a in aprendizado if a.strip()])

        publico_alvo = tree.xpath('string(//p[contains(@class, "couse-text--target-audience")])').strip()

        return {
            "titulo": titulo,
            "url": url,
            "aprendizado": aprendizado_texto,
            "publico_alvo": publico_alvo
        }

    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return None


def salvar_json(dados, caminho_arquivo=None):
    if caminho_arquivo is None:
        # Caminho relativo ao script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(script_dir, '..', 'data', 'cursos_alura.json')
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
    
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def extrair_todos_detalhes():
    print("🔍 Extraindo links de cursos...")
    links = extrair_links_alura()
    print(f"Total de cursos encontrados: {len(links)}")

    cursos_detalhados = []
    for i, link in enumerate(links, 1):
        print(f"[{i}/{len(links)}] Extraindo: {link}")
        detalhes = extrair_detalhes_curso(link)
        if detalhes:
            cursos_detalhados.append(detalhes)

    print("\n📦 JSON FINAL:")
    print(json.dumps(cursos_detalhados, indent=4, ensure_ascii=False))

    salvar_json(cursos_detalhados)
    print("\n💾 Arquivo 'cursos_alura.json' salvo com sucesso!")


if __name__ == "__main__":
    extrair_todos_detalhes()
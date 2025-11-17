import requests
from lxml import html
from database import firebase_db

BASE_URL = "https://www.alura.com.br"
LISTA_CURSOS_URL = f"{BASE_URL}/cursos-online-tecnologia"


def extrair_links_alura(url=LISTA_CURSOS_URL):
    """Extrai links dos cursos"""
    response = requests.get(url)
    response.raise_for_status()

    tree = html.fromstring(response.content)
    links = tree.xpath('//a[contains(@class, "card-curso")]/@href')
    links_completos = [BASE_URL + link for link in set(links)]
    return links_completos


def extrair_detalhes_curso(url):
    """Extrai detalhes de um curso"""
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
        print(f"⚠️  Erro ao processar {url}: {e}")
        return None


def extrair_todos_detalhes():
    """Extrai todos os cursos e salva no Firebase"""
    print("=" * 60)
    print("🔍 SCRAPER DE CURSOS DA ALURA → FIREBASE")
    print("=" * 60)
    
    print("\n📋 Extraindo links de cursos...")
    links = extrair_links_alura()
    print(f"✅ {len(links)} cursos encontrados")

    print("\n🔄 Extraindo detalhes dos cursos...")
    cursos_detalhados = []
    # for i, link in enumerate(links[:10], 1):
    for i, link in enumerate(links, 1):
        print(f"   [{i}/{len(links)}] {link}")
        detalhes = extrair_detalhes_curso(link)
        if detalhes:
            cursos_detalhados.append(detalhes)

    print(f"\n📊 Total coletado: {len(cursos_detalhados)} cursos")

    print("\n🔥 Salvando no Firebase Firestore...")
    sucesso = firebase_db.inserir_cursos(cursos_detalhados)
    
    if sucesso:
        print("\n" + "=" * 60)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"📌 {len(cursos_detalhados)} cursos disponíveis no Firebase")
    else:
        print("\n❌ Falha ao salvar no Firebase")


if __name__ == "__main__":
    extrair_todos_detalhes()
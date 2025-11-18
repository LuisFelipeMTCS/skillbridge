"""
Script de Setup Completo - SkillBridge
Verifica estrutura, instala dependências e treina modelos
"""

import os
import sys
import subprocess

print("="*70)
print("🎓 SKILLBRIDGE - SETUP COMPLETO")
print("FIAP Global Solution 2025")
print("="*70)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PASSO 1: Verificar Estrutura
print("\n📋 PASSO 1/4: Verificando estrutura de arquivos...")

arquivos_criticos = {
    'controller/data_generator.py': '⭐ Gerador de dados',
    'controller/ml_models.py': '⭐ Modelos ML',
    'controller/ml_predictor.py': '⭐ Preditor',
    'controller/dashboard.html': '⭐ Dashboard',
    'controller/resultados_ml.html': '⭐ Página de resultados',
    'app/main.py': '✅ Servidor Flask',
    'data/cursos_alura.json': '✅ Base de cursos'
}

arquivos_faltando = []
for arquivo, desc in arquivos_criticos.items():
    caminho = os.path.join(BASE_DIR, arquivo)
    if os.path.exists(caminho):
        print(f"   ✅ {desc}")
    else:
        print(f"   ❌ {desc} - FALTANDO: {arquivo}")
        arquivos_faltando.append(arquivo)

if arquivos_faltando:
    print("\n" + "="*70)
    print("❌ ARQUIVOS FALTANDO!")
    print("="*70)
    print("\n📥 Você precisa baixar dos outputs e copiar:")
    for arquivo in arquivos_faltando:
        if arquivo.startswith('controller/'):
            print(f"   - {arquivo.split('/')[-1]} → pasta controller/")
    print("\n💡 Depois de copiar, execute este script novamente.")
    print("="*70)
    input("\n⏸️ Pressione ENTER para sair...")
    sys.exit(1)

print("\n✅ Todos os arquivos necessários estão presentes!")

# PASSO 2: Verificar Dependências
print("\n" + "="*70)
print("📦 PASSO 2/4: Verificando dependências Python...")
print("="*70)

dependencias = [
    'pandas',
    'numpy',
    'sklearn',
    'matplotlib',
    'seaborn',
    'flask'
]

deps_faltando = []
for dep in dependencias:
    nome_import = 'sklearn' if dep == 'sklearn' else dep
    try:
        __import__(nome_import)
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} não instalado")
        deps_faltando.append(dep)

if deps_faltando:
    print("\n⚠️ Dependências faltando!")
    print("\n💡 Instalar agora? (s/n)")
    
    resposta = input(">>> ").strip().lower()
    
    if resposta == 's':
        print("\n🔄 Instalando dependências...")
        
        # Mapear nomes de pacotes
        pacotes_pip = {
            'sklearn': 'scikit-learn'
        }
        
        for dep in deps_faltando:
            pacote = pacotes_pip.get(dep, dep)
            print(f"\n   Instalando {pacote}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pacote])
                print(f"   ✅ {pacote} instalado")
            except subprocess.CalledProcessError:
                print(f"   ❌ Erro ao instalar {pacote}")
        
        print("\n✅ Instalação concluída!")
    else:
        print("\n⚠️ Instale as dependências manualmente:")
        print("   pip install pandas numpy scikit-learn matplotlib seaborn flask")
        print("\n💡 Depois execute este script novamente.")
        input("\n⏸️ Pressione ENTER para sair...")
        sys.exit(1)
else:
    print("\n✅ Todas as dependências estão instaladas!")

# PASSO 3: Verificar se modelos já existem
print("\n" + "="*70)
print("🤖 PASSO 3/4: Verificando modelos ML...")
print("="*70)

models_folder = os.path.join(BASE_DIR, 'models')
modelo_exemplo = os.path.join(models_folder, 'clf_RandomForest.pkl')

if os.path.exists(modelo_exemplo):
    print("\n✅ Modelos já estão treinados!")
    print("\n💡 Deseja retreinar? (s/n)")
    resposta = input(">>> ").strip().lower()
    
    if resposta != 's':
        print("\n⏩ Pulando treinamento...")
        print("\n" + "="*70)
        print("✅ SETUP CONCLUÍDO!")
        print("="*70)
        print("\n💡 Próximos passos:")
        print("   1. python app/main.py")
        print("   2. Acesse: http://localhost:5000")
        print("="*70)
        input("\n⏸️ Pressione ENTER para sair...")
        sys.exit(0)

print("\n🚀 Iniciando treinamento dos modelos...")
print("⏳ Isso pode levar 1-2 minutos...")

# Treinar modelos
try:
    # Adicionar controller ao path
    controller_dir = os.path.join(BASE_DIR, 'controller')
    sys.path.insert(0, controller_dir)
    
    from data_generator import DataGenerator
    from ml_models import MLModels
    
    # Criar pastas
    data_folder = os.path.join(BASE_DIR, 'data')
    viz_folder = os.path.join(BASE_DIR, 'visualizations')
    
    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(models_folder, exist_ok=True)
    os.makedirs(viz_folder, exist_ok=True)
    
    # Gerar dataset
    print("\n   📊 Gerando dataset (1000 amostras)...")
    generator = DataGenerator()
    df = generator.gerar_dataset(n_amostras=1000)
    dataset_path = os.path.join(data_folder, 'dataset_profissionais.csv')
    generator.salvar_dataset(df, dataset_path)
    
    # Treinar modelos
    print("   🤖 Treinando modelos de classificação...")
    ml = MLModels(dataset_path)
    ml.carregar_dados()
    dados = ml.preprocessar_dados()
    ml.treinar_modelos_classificacao(dados)
    
    print("   📈 Treinando modelos de regressão...")
    ml.treinar_modelos_regressao(dados)
    
    # Salvar
    print("   💾 Salvando modelos...")
    ml.salvar_modelos(models_folder)
    
    print("   📊 Gerando visualizações...")
    ml.gerar_visualizacoes(viz_folder)
    
    print("\n✅ Treinamento concluído!")
    
except Exception as e:
    print(f"\n❌ Erro no treinamento: {e}")
    import traceback
    traceback.print_exc()
    input("\n⏸️ Pressione ENTER para sair...")
    sys.exit(1)

# PASSO 4: Resumo Final
print("\n" + "="*70)
print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
print("="*70)

print("\n📊 RESUMO:")
print(f"   ✅ Dataset: 1000 amostras")
print(f"   ✅ Modelos treinados: 4")
print(f"      - Random Forest Classifier")
print(f"      - Gradient Boosting Classifier")
print(f"      - Random Forest Regressor")
print(f"      - Linear Regression")
print(f"   ✅ Visualizações: 4 gráficos")

print("\n📁 ESTRUTURA CRIADA:")
print(f"   data/dataset_profissionais.csv")
print(f"   models/*.pkl (4 modelos + encoders)")
print(f"   visualizations/*.png (4 gráficos)")

print("\n" + "="*70)
print("🚀 PRÓXIMOS PASSOS:")
print("="*70)
print("\n1️⃣ INICIAR O SERVIDOR:")
print("   python app/main.py")
print("\n2️⃣ ACESSAR NO NAVEGADOR:")
print("   http://localhost:5000")
print("\n3️⃣ TESTAR O SISTEMA:")
print("   - Preencha o formulário")
print("   - Veja as predições dos 4 modelos ML")
print("   - Explore os cursos recomendados")

print("\n" + "="*70)
print("💡 DICA: Mantenha esta janela aberta como referência!")
print("="*70)

input("\n✅ Pressione ENTER para finalizar...")
"""
Script Standalone para Treinamento de Modelos ML
Execute este script DIRETAMENTE - não precisa do servidor rodando
"""

import os
import sys

# Configurar paths
# Configurar paths
# O script está em controller/, então subimos um nível (..) para chegar na raiz (skillbridge/)
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CONTROLLER_DIR = os.path.join(BASE_DIR, 'controller')

# Adiciona o diretório 'controller' ao path do Python para que os módulos internos sejam importados
sys.path.insert(0, CONTROLLER_DIR)

print("="*70)
print("🚀 TREINAMENTO DE MODELOS ML - SKILLBRIDGE")
print("FIAP Global Solution 2025 - Futuro do Trabalho")
print("="*70)

# Verificar se arquivos existem
arquivos_necessarios = [
    ('controller/data_generator.py', 'Gerador de dados'),
    ('controller/ml_models.py', 'Modelos de ML')
]

print("\n📋 Verificando arquivos necessários...")
todos_ok = True
for arquivo, descricao in arquivos_necessarios:
    caminho = os.path.join(BASE_DIR, arquivo)
    if os.path.exists(caminho):
        print(f"   ✅ {descricao}")
    else:
        print(f"   ❌ {descricao} não encontrado em: {arquivo}")
        todos_ok = False

if not todos_ok:
    print("\n❌ Arquivos faltando! Certifique-se de ter copiado:")
    print("   - data_generator.py → controller/")
    print("   - ml_models.py → controller/")
    sys.exit(1)

print("\n✅ Todos os arquivos encontrados!")

# Importar módulos
try:
    print("\n📦 Importando módulos...")
    from data_generator import DataGenerator
    from ml_models import MLModels
    print("   ✅ Imports OK")
except ImportError as e:
    print(f"\n❌ Erro ao importar módulos: {e}")
    print("\n💡 Instale as dependências:")
    print("   pip install pandas numpy scikit-learn matplotlib seaborn")
    sys.exit(1)

# Criar pastas necessárias
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
MODELS_FOLDER = os.path.join(BASE_DIR, 'models')
VIZ_FOLDER = os.path.join(BASE_DIR, 'visualizations')

print("\n📁 Criando estrutura de pastas...")
for folder, nome in [(DATA_FOLDER, 'data'), (MODELS_FOLDER, 'models'), (VIZ_FOLDER, 'visualizations')]:
    os.makedirs(folder, exist_ok=True)
    print(f"   ✅ {nome}/")

# ETAPA 1: Gerar Dataset
print("\n" + "="*70)
print("📊 ETAPA 1/4: GERANDO DATASET SINTÉTICO")
print("="*70)

try:
    generator = DataGenerator()
    print("\n🔄 Gerando 1000 amostras de profissionais...")
    df = generator.gerar_dataset(n_amostras=1000)
    
    dataset_path = os.path.join(DATA_FOLDER, 'dataset_profissionais.csv')
    generator.salvar_dataset(df, dataset_path)
    
    print(f"\n✅ Dataset gerado com sucesso!")
    print(f"   📊 Shape: {df.shape}")
    print(f"   📁 Salvo em: {dataset_path}")
    
except Exception as e:
    print(f"\n❌ Erro ao gerar dataset: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ETAPA 2: Carregar e Preprocessar
print("\n" + "="*70)
print("🔧 ETAPA 2/4: PRÉ-PROCESSAMENTO DOS DADOS")
print("="*70)

try:
    ml = MLModels(dataset_path)
    print("\n📂 Carregando dataset...")
    ml.carregar_dados()
    
    print("🔄 Preprocessando dados...")
    dados = ml.preprocessar_dados()
    
    print("\n✅ Pré-processamento concluído!")
    
except Exception as e:
    print(f"\n❌ Erro no pré-processamento: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ETAPA 3: Treinar Modelos
print("\n" + "="*70)
print("🤖 ETAPA 3/4: TREINAMENTO DOS MODELOS")
print("="*70)

try:
    print("\n📊 Treinando modelos de CLASSIFICAÇÃO...")
    print("   (Random Forest + Gradient Boosting)")
    ml.treinar_modelos_classificacao(dados)
    
    print("\n📈 Treinando modelos de REGRESSÃO...")
    print("   (Random Forest + Linear Regression)")
    ml.treinar_modelos_regressao(dados)
    
    print("\n✅ Todos os modelos treinados!")
    
except Exception as e:
    print(f"\n❌ Erro no treinamento: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ETAPA 4: Salvar e Visualizar
print("\n" + "="*70)
print("💾 ETAPA 4/4: SALVANDO MODELOS E GERANDO VISUALIZAÇÕES")
print("="*70)

try:
    print("\n💾 Salvando modelos...")
    ml.salvar_modelos(MODELS_FOLDER)
    
    print("\n📊 Gerando visualizações...")
    ml.gerar_visualizacoes(VIZ_FOLDER)
    
    print("\n✅ Tudo salvo com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro ao salvar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# RESUMO FINAL
print("\n" + "="*70)
print("🎉 TREINAMENTO CONCLUÍDO COM SUCESSO!")
print("="*70)

print("\n📊 RESUMO:")
print(f"   ✅ Dataset: {df.shape[0]} amostras, {df.shape[1]} features")
print(f"   ✅ Modelos treinados: 4")
print(f"   ✅ Visualizações geradas: 4")

print("\n📁 ARQUIVOS GERADOS:")
print(f"   📂 {DATA_FOLDER}/")
print(f"      └── dataset_profissionais.csv")
print(f"   📂 {MODELS_FOLDER}/")
print(f"      ├── clf_RandomForest.pkl")
print(f"      ├── clf_GradientBoosting.pkl")
print(f"      ├── reg_RandomForest.pkl")
print(f"      ├── reg_LinearRegression.pkl")
print(f"      ├── label_encoders.pkl")
print(f"      ├── scaler.pkl")
print(f"      └── resultados.json")
print(f"   📂 {VIZ_FOLDER}/")
print(f"      ├── feature_importance_clf.png")
print(f"      ├── confusion_matrix_rf.png")
print(f"      ├── comparacao_clf.png")
print(f"      └── comparacao_reg.png")

# Verificar resultados
resultados_path = os.path.join(MODELS_FOLDER, 'resultados.json')
if os.path.exists(resultados_path):
    import json
    with open(resultados_path, 'r', encoding='utf-8') as f:
        resultados = json.load(f)
    
    print("\n📈 MÉTRICAS DOS MODELOS:")
    
    print("\n   🎯 CLASSIFICAÇÃO (Prever Área de Carreira):")
    for nome, metricas in resultados['classificacao'].items():
        if nome != 'feature_importance':
            print(f"      {nome}:")
            print(f"         Accuracy: {metricas['accuracy']*100:.1f}%")
            print(f"         F1-Score: {metricas['f1_score']*100:.1f}%")
    
    print("\n   📊 REGRESSÃO (Score de Adequação):")
    for nome, metricas in resultados['regressao'].items():
        print(f"      {nome}:")
        print(f"         RMSE: {metricas['rmse']:.2f}")
        print(f"         R² Score: {metricas['r2_score']*100:.1f}%")

print("\n" + "="*70)
print("💡 PRÓXIMOS PASSOS:")
print("="*70)
print("   1. Inicie o servidor: python app/main.py")
print("   2. Acesse: http://localhost:5000")
print("   3. Preencha o formulário")
print("   4. Veja as predições ML!")
print("="*70)
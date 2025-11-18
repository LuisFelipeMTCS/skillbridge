"""
Módulo de Modelos de Machine Learning
Sistema de Recomendação de Carreira - FIAP Global Solution 2025

Este módulo implementa e treina modelos de ML para:
1. Classificação: Prever a melhor área de carreira
2. Regressão: Prever o score de adequação do profissional

Modelos implementados:
- Classificação: Random Forest e Gradient Boosting
- Regressão: Random Forest Regressor e Linear Regression
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score
)
import pickle
import os
import json


class MLModels:
    """Classe para treinamento e avaliação de modelos de Machine Learning"""
    
    def __init__(self, dataset_path='data/dataset_profissionais.csv'):
        """
        Inicializa a classe com o dataset
        
        Args:
            dataset_path (str): Caminho para o dataset CSV
        """
        self.dataset_path = dataset_path
        self.df = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
        # Modelos
        self.clf_models = {}
        self.reg_models = {}
        
        # Resultados
        self.resultados = {
            'classificacao': {},
            'regressao': {}
        }
    
    def carregar_dados(self):
        """Carrega o dataset do arquivo CSV"""
        print("📂 Carregando dataset...")
        self.df = pd.read_csv(self.dataset_path)
        print(f"✅ Dataset carregado: {self.df.shape}")
        print(f"\n📊 Primeiras linhas:\n{self.df.head()}")
        return self.df
    
    def preprocessar_dados(self):
        """
        Preprocessa os dados para ML:
        - Codifica variáveis categóricas
        - Separa features e target
        - Divide em treino e teste
        """
        print("\n🔧 Preprocessando dados...")
        
        # Criar cópia do dataframe
        df_processed = self.df.copy()
        
        # Codificar variáveis categóricas
        categoricas = ['profissao_atual', 'nivel_atual', 'objetivo_principal']
        
        for col in categoricas:
            le = LabelEncoder()
            df_processed[col + '_encoded'] = le.fit_transform(df_processed[col])
            self.label_encoders[col] = le
        
        # Codificar a área de interesse (target para classificação)
        le_target = LabelEncoder()
        df_processed['area_interesse_encoded'] = le_target.fit_transform(df_processed['area_interesse'])
        self.label_encoders['area_interesse'] = le_target
        
        # Features para os modelos
        feature_cols = [
            'profissao_atual_encoded',
            'anos_experiencia',
            'nivel_atual_encoded',
            'objetivo_principal_encoded',
            'tempo_disponivel_estudo',
            'num_habilidades',
            'motivacao'
        ]
        
        X = df_processed[feature_cols]
        
        # Target para classificação (área de interesse)
        y_clf = df_processed['area_interesse_encoded']
        
        # Target para regressão (score de adequação)
        y_reg = df_processed['score_adequacao']
        
        # Dividir em treino e teste (80/20)
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
            X, y_clf, test_size=0.2, random_state=42, stratify=y_clf
        )
        
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
            X, y_reg, test_size=0.2, random_state=42
        )
        
        # Escalonar features para modelos lineares
        X_train_reg_scaled = self.scaler.fit_transform(X_train_reg)
        X_test_reg_scaled = self.scaler.transform(X_test_reg)
        
        print(f"✅ Dados preprocessados")
        print(f"   - Features: {feature_cols}")
        print(f"   - Treino classificação: {X_train_clf.shape}")
        print(f"   - Teste classificação: {X_test_clf.shape}")
        print(f"   - Treino regressão: {X_train_reg.shape}")
        print(f"   - Teste regressão: {X_test_reg.shape}")
        
        return {
            'X_train_clf': X_train_clf,
            'X_test_clf': X_test_clf,
            'y_train_clf': y_train_clf,
            'y_test_clf': y_test_clf,
            'X_train_reg': X_train_reg,
            'X_test_reg': X_test_reg,
            'X_train_reg_scaled': X_train_reg_scaled,
            'X_test_reg_scaled': X_test_reg_scaled,
            'y_train_reg': y_train_reg,
            'y_test_reg': y_test_reg,
            'feature_cols': feature_cols
        }
    
    def treinar_modelos_classificacao(self, dados):
        """
        Treina modelos de classificação
        
        Modelos:
        1. Random Forest Classifier
        2. Gradient Boosting Classifier
        """
        print("\n" + "="*70)
        print("🎯 TREINANDO MODELOS DE CLASSIFICAÇÃO")
        print("="*70)
        
        X_train = dados['X_train_clf']
        X_test = dados['X_test_clf']
        y_train = dados['y_train_clf']
        y_test = dados['y_test_clf']
        
        # 1. Random Forest Classifier
        print("\n📊 Modelo 1: Random Forest Classifier")
        rf_clf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_clf.fit(X_train, y_train)
        y_pred_rf = rf_clf.predict(X_test)
        
        # Validação cruzada
        cv_scores_rf = cross_val_score(rf_clf, X_train, y_train, cv=5, scoring='accuracy')
        
        # Métricas
        acc_rf = accuracy_score(y_test, y_pred_rf)
        prec_rf = precision_score(y_test, y_pred_rf, average='weighted')
        rec_rf = recall_score(y_test, y_pred_rf, average='weighted')
        f1_rf = f1_score(y_test, y_pred_rf, average='weighted')
        
        print(f"   ✓ Accuracy: {acc_rf:.4f}")
        print(f"   ✓ Precision: {prec_rf:.4f}")
        print(f"   ✓ Recall: {rec_rf:.4f}")
        print(f"   ✓ F1-Score: {f1_rf:.4f}")
        print(f"   ✓ CV Score: {cv_scores_rf.mean():.4f} (+/- {cv_scores_rf.std():.4f})")
        
        self.clf_models['RandomForest'] = rf_clf
        self.resultados['classificacao']['RandomForest'] = {
            'accuracy': acc_rf,
            'precision': prec_rf,
            'recall': rec_rf,
            'f1_score': f1_rf,
            'cv_scores': cv_scores_rf.tolist(),
            'cv_mean': cv_scores_rf.mean(),
            'cv_std': cv_scores_rf.std(),
            'confusion_matrix': confusion_matrix(y_test, y_pred_rf).tolist(),
            'y_test': y_test.tolist(),
            'y_pred': y_pred_rf.tolist()
        }
        
        # 2. Gradient Boosting Classifier
        print("\n📊 Modelo 2: Gradient Boosting Classifier")
        gb_clf = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        gb_clf.fit(X_train, y_train)
        y_pred_gb = gb_clf.predict(X_test)
        
        # Validação cruzada
        cv_scores_gb = cross_val_score(gb_clf, X_train, y_train, cv=5, scoring='accuracy')
        
        # Métricas
        acc_gb = accuracy_score(y_test, y_pred_gb)
        prec_gb = precision_score(y_test, y_pred_gb, average='weighted')
        rec_gb = recall_score(y_test, y_pred_gb, average='weighted')
        f1_gb = f1_score(y_test, y_pred_gb, average='weighted')
        
        print(f"   ✓ Accuracy: {acc_gb:.4f}")
        print(f"   ✓ Precision: {prec_gb:.4f}")
        print(f"   ✓ Recall: {rec_gb:.4f}")
        print(f"   ✓ F1-Score: {f1_gb:.4f}")
        print(f"   ✓ CV Score: {cv_scores_gb.mean():.4f} (+/- {cv_scores_gb.std():.4f})")
        
        self.clf_models['GradientBoosting'] = gb_clf
        self.resultados['classificacao']['GradientBoosting'] = {
            'accuracy': acc_gb,
            'precision': prec_gb,
            'recall': rec_gb,
            'f1_score': f1_gb,
            'cv_scores': cv_scores_gb.tolist(),
            'cv_mean': cv_scores_gb.mean(),
            'cv_std': cv_scores_gb.std(),
            'confusion_matrix': confusion_matrix(y_test, y_pred_gb).tolist(),
            'y_test': y_test.tolist(),
            'y_pred': y_pred_gb.tolist()
        }
        
        # Importância das features (usando Random Forest)
        feature_importance = pd.DataFrame({
            'feature': dados['feature_cols'],
            'importance': rf_clf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.resultados['classificacao']['feature_importance'] = feature_importance.to_dict('records')
        
        print("\n✅ Modelos de classificação treinados com sucesso!")
    
    def treinar_modelos_regressao(self, dados):
        """
        Treina modelos de regressão
        
        Modelos:
        1. Random Forest Regressor
        2. Linear Regression
        """
        print("\n" + "="*70)
        print("📈 TREINANDO MODELOS DE REGRESSÃO")
        print("="*70)
        
        X_train = dados['X_train_reg']
        X_test = dados['X_test_reg']
        X_train_scaled = dados['X_train_reg_scaled']
        X_test_scaled = dados['X_test_reg_scaled']
        y_train = dados['y_train_reg']
        y_test = dados['y_test_reg']
        
        # 1. Random Forest Regressor
        print("\n📊 Modelo 1: Random Forest Regressor")
        rf_reg = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_reg.fit(X_train, y_train)
        y_pred_rf = rf_reg.predict(X_test)
        
        # Validação cruzada
        cv_scores_rf = cross_val_score(rf_reg, X_train, y_train, cv=5, scoring='r2')
        
        # Métricas
        rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
        mae_rf = mean_absolute_error(y_test, y_pred_rf)
        r2_rf = r2_score(y_test, y_pred_rf)
        
        print(f"   ✓ RMSE: {rmse_rf:.4f}")
        print(f"   ✓ MAE: {mae_rf:.4f}")
        print(f"   ✓ R² Score: {r2_rf:.4f}")
        print(f"   ✓ CV R² Score: {cv_scores_rf.mean():.4f} (+/- {cv_scores_rf.std():.4f})")
        
        self.reg_models['RandomForest'] = rf_reg
        self.resultados['regressao']['RandomForest'] = {
            'rmse': rmse_rf,
            'mae': mae_rf,
            'r2_score': r2_rf,
            'cv_scores': cv_scores_rf.tolist(),
            'cv_mean': cv_scores_rf.mean(),
            'cv_std': cv_scores_rf.std(),
            'y_test': y_test.tolist(),
            'y_pred': y_pred_rf.tolist()
        }
        
        # 2. Linear Regression
        print("\n📊 Modelo 2: Linear Regression")
        lr_reg = LinearRegression()
        lr_reg.fit(X_train_scaled, y_train)
        y_pred_lr = lr_reg.predict(X_test_scaled)
        
        # Validação cruzada
        cv_scores_lr = cross_val_score(
            LinearRegression(), 
            X_train_scaled, 
            y_train, 
            cv=5, 
            scoring='r2'
        )
        
        # Métricas
        rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
        mae_lr = mean_absolute_error(y_test, y_pred_lr)
        r2_lr = r2_score(y_test, y_pred_lr)
        
        print(f"   ✓ RMSE: {rmse_lr:.4f}")
        print(f"   ✓ MAE: {mae_lr:.4f}")
        print(f"   ✓ R² Score: {r2_lr:.4f}")
        print(f"   ✓ CV R² Score: {cv_scores_lr.mean():.4f} (+/- {cv_scores_lr.std():.4f})")
        
        self.reg_models['LinearRegression'] = lr_reg
        self.resultados['regressao']['LinearRegression'] = {
            'rmse': rmse_lr,
            'mae': mae_lr,
            'r2_score': r2_lr,
            'cv_scores': cv_scores_lr.tolist(),
            'cv_mean': cv_scores_lr.mean(),
            'cv_std': cv_scores_lr.std(),
            'y_test': y_test.tolist(),
            'y_pred': y_pred_lr.tolist()
        }
        
        print("\n✅ Modelos de regressão treinados com sucesso!")
    
    def salvar_modelos(self, output_dir='models'):
        """Salva os modelos treinados em arquivos pickle"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Salvar modelos de classificação
        for nome, modelo in self.clf_models.items():
            caminho = os.path.join(output_dir, f'clf_{nome}.pkl')
            with open(caminho, 'wb') as f:
                pickle.dump(modelo, f)
            print(f"✅ Modelo salvo: {caminho}")
        
        # Salvar modelos de regressão
        for nome, modelo in self.reg_models.items():
            caminho = os.path.join(output_dir, f'reg_{nome}.pkl')
            with open(caminho, 'wb') as f:
                pickle.dump(modelo, f)
            print(f"✅ Modelo salvo: {caminho}")
        
        # Salvar label encoders e scaler
        with open(os.path.join(output_dir, 'label_encoders.pkl'), 'wb') as f:
            pickle.dump(self.label_encoders, f)
        
        with open(os.path.join(output_dir, 'scaler.pkl'), 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Salvar resultados em JSON
        with open(os.path.join(output_dir, 'resultados.json'), 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Todos os modelos e artefatos salvos em: {output_dir}")
    
    def gerar_visualizacoes(self, output_dir='visualizations'):
        """Gera visualizações dos resultados dos modelos"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Importância das features (Classificação)
        if 'feature_importance' in self.resultados['classificacao']:
            plt.figure(figsize=(10, 6))
            feat_imp = pd.DataFrame(self.resultados['classificacao']['feature_importance'])
            sns.barplot(data=feat_imp, x='importance', y='feature')
            plt.title('Importância das Features - Classificação')
            plt.xlabel('Importância')
            plt.ylabel('Feature')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'feature_importance_clf.png'), dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ Visualização salva: feature_importance_clf.png")
        
        # 2. Matriz de confusão - Random Forest
        if 'RandomForest' in self.resultados['classificacao']:
            cm = np.array(self.resultados['classificacao']['RandomForest']['confusion_matrix'])
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title('Matriz de Confusão - Random Forest Classifier')
            plt.ylabel('Valor Real')
            plt.xlabel('Valor Predito')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'confusion_matrix_rf.png'), dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ Visualização salva: confusion_matrix_rf.png")
        
        # 3. Comparação de modelos de classificação
        plt.figure(figsize=(12, 6))
        modelos = list(self.resultados['classificacao'].keys())
        modelos = [m for m in modelos if m != 'feature_importance']
        
        metricas = ['accuracy', 'precision', 'recall', 'f1_score']
        x = np.arange(len(modelos))
        width = 0.2
        
        for i, metrica in enumerate(metricas):
            valores = [self.resultados['classificacao'][m][metrica] for m in modelos]
            plt.bar(x + i*width, valores, width, label=metrica.capitalize())
        
        plt.xlabel('Modelos')
        plt.ylabel('Score')
        plt.title('Comparação de Métricas - Modelos de Classificação')
        plt.xticks(x + width*1.5, modelos)
        plt.legend()
        plt.ylim([0, 1])
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'comparacao_clf.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Visualização salva: comparacao_clf.png")
        
        # 4. Comparação de modelos de regressão
        plt.figure(figsize=(12, 6))
        modelos = list(self.resultados['regressao'].keys())
        
        x = np.arange(len(modelos))
        width = 0.25
        
        rmse_vals = [self.resultados['regressao'][m]['rmse'] for m in modelos]
        mae_vals = [self.resultados['regressao'][m]['mae'] for m in modelos]
        r2_vals = [self.resultados['regressao'][m]['r2_score'] for m in modelos]
        
        plt.subplot(1, 2, 1)
        plt.bar(x - width, rmse_vals, width, label='RMSE')
        plt.bar(x, mae_vals, width, label='MAE')
        plt.xlabel('Modelos')
        plt.ylabel('Erro')
        plt.title('Métricas de Erro - Regressão')
        plt.xticks(x, modelos, rotation=45)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.bar(x, r2_vals, width, label='R² Score', color='green')
        plt.xlabel('Modelos')
        plt.ylabel('R² Score')
        plt.title('R² Score - Regressão')
        plt.xticks(x, modelos, rotation=45)
        plt.ylim([0, 1])
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'comparacao_reg.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Visualização salva: comparacao_reg.png")
        
        print(f"\n✅ Todas as visualizações salvas em: {output_dir}")


def main():
    """Função principal para treinar todos os modelos"""
    print("="*70)
    print("TREINAMENTO DE MODELOS ML - SKILLBRIDGE")
    print("Sistema de Recomendação de Carreira - FIAP Global Solution 2025")
    print("="*70)
    
    # Inicializar
    ml = MLModels('data/dataset_profissionais.csv')
    
    # Carregar dados
    ml.carregar_dados()
    
    # Preprocessar
    dados = ml.preprocessar_dados()
    
    # Treinar modelos de classificação
    ml.treinar_modelos_classificacao(dados)
    
    # Treinar modelos de regressão
    ml.treinar_modelos_regressao(dados)
    
    # Salvar modelos
    ml.salvar_modelos('models')
    
    # Gerar visualizações
    ml.gerar_visualizacoes('visualizations')
    
    print("\n" + "="*70)
    print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("="*70)


if __name__ == "__main__":
    main()
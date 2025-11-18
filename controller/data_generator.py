"""
Gerador de Dados Sintéticos para Treinamento de Modelos ML
Sistema de Recomendação de Carreira - FIAP Global Solution 2025

Este módulo gera um dataset sintético de profissionais com suas características
e áreas de carreira recomendadas para treinar modelos de Machine Learning.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

# Configurar seed para reprodutibilidade
np.random.seed(42)

class DataGenerator:
    """Classe para gerar dados sintéticos de profissionais e suas carreiras"""
    
    def __init__(self):
        self.areas_carreira = [
            'Desenvolvimento Web',
            'Data Science',
            'DevOps',
            'Mobile',
            'UX/UI Design',
            'Segurança da Informação',
            'Cloud Computing',
            'Inteligência Artificial'
        ]
        
        self.profissoes_atuais = [
            'Desenvolvedor', 'Analista de Sistemas', 'QA Tester', 
            'Suporte Técnico', 'Designer', 'Gerente de Projetos',
            'Analista de Dados', 'DBA', 'Administrador de Redes'
        ]
        
        self.niveis = ['Júnior', 'Pleno', 'Sênior']
        
        self.habilidades_tecnicas = {
            'Desenvolvimento Web': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Python', 'Java'],
            'Data Science': ['Python', 'R', 'SQL', 'Machine Learning', 'Estatística', 'Pandas', 'NumPy'],
            'DevOps': ['Docker', 'Kubernetes', 'CI/CD', 'Linux', 'AWS', 'Terraform', 'Git'],
            'Mobile': ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Android', 'iOS'],
            'UX/UI Design': ['Figma', 'Adobe XD', 'Sketch', 'Design Thinking', 'Prototipagem'],
            'Segurança da Informação': ['Pentest', 'OWASP', 'Criptografia', 'Firewall', 'SIEM'],
            'Cloud Computing': ['AWS', 'Azure', 'GCP', 'Serverless', 'Containers'],
            'Inteligência Artificial': ['Python', 'TensorFlow', 'PyTorch', 'NLP', 'Computer Vision']
        }
    
    def gerar_dataset(self, n_amostras=1000):
        """
        Gera um dataset sintético de profissionais
        
        Args:
            n_amostras (int): Número de amostras a gerar
            
        Returns:
            pd.DataFrame: Dataset gerado
        """
        dados = []
        
        for i in range(n_amostras):
            # Características do profissional
            anos_exp = np.random.randint(0, 21)
            nivel = self._definir_nivel(anos_exp)
            profissao_atual = np.random.choice(self.profissoes_atuais)
            
            # Objetivo (60% quer realocar, 40% quer atualizar)
            objetivo = np.random.choice(['Realocar Carreira', 'Atualizar Carreira'], p=[0.6, 0.4])
            
            # Área de interesse (depende do objetivo e background)
            area_interesse = self._definir_area_interesse(profissao_atual, objetivo)
            
            # Tempo disponível para estudo (horas/semana)
            tempo_estudo = np.random.choice([5, 10, 15, 20, 25, 30], p=[0.1, 0.2, 0.3, 0.25, 0.1, 0.05])
            
            # Habilidades atuais (baseadas na área de interesse)
            num_habilidades = np.random.randint(2, 6)
            habilidades = np.random.choice(
                self.habilidades_tecnicas.get(area_interesse, ['Python', 'SQL']),
                size=min(num_habilidades, len(self.habilidades_tecnicas.get(area_interesse, []))),
                replace=False
            ).tolist()
            
            # Motivação (0-10)
            motivacao = np.random.randint(5, 11)
            
            # Score de adequação (variável alvo para regressão)
            # Calculado com base em múltiplos fatores
            score_adequacao = self._calcular_score_adequacao(
                anos_exp, nivel, tempo_estudo, len(habilidades), motivacao, objetivo
            )
            
            # Adicionar ruído realista
            score_adequacao += np.random.normal(0, 5)
            score_adequacao = np.clip(score_adequacao, 0, 100)
            
            dados.append({
                'profissao_atual': profissao_atual,
                'anos_experiencia': anos_exp,
                'nivel_atual': nivel,
                'objetivo_principal': objetivo,
                'area_interesse': area_interesse,
                'tempo_disponivel_estudo': tempo_estudo,
                'num_habilidades': len(habilidades),
                'habilidades_atuais': ','.join(habilidades),
                'motivacao': motivacao,
                'score_adequacao': round(score_adequacao, 2)
            })
        
        df = pd.DataFrame(dados)
        return df
    
    def _definir_nivel(self, anos_exp):
        """Define o nível profissional baseado nos anos de experiência"""
        if anos_exp < 3:
            return 'Júnior'
        elif anos_exp < 7:
            return 'Pleno'
        else:
            return 'Sênior'
    
    def _definir_area_interesse(self, profissao_atual, objetivo):
        """Define a área de interesse baseada na profissão atual e objetivo"""
        mapeamento_afinidade = {
            'Desenvolvedor': ['Desenvolvimento Web', 'Mobile', 'DevOps'],
            'Analista de Sistemas': ['Desenvolvimento Web', 'Data Science', 'Cloud Computing'],
            'QA Tester': ['DevOps', 'Desenvolvimento Web', 'Segurança da Informação'],
            'Suporte Técnico': ['DevOps', 'Cloud Computing', 'Segurança da Informação'],
            'Designer': ['UX/UI Design', 'Desenvolvimento Web', 'Mobile'],
            'Gerente de Projetos': ['DevOps', 'Cloud Computing', 'Data Science'],
            'Analista de Dados': ['Data Science', 'Inteligência Artificial', 'Cloud Computing'],
            'DBA': ['Data Science', 'Cloud Computing', 'DevOps'],
            'Administrador de Redes': ['DevOps', 'Cloud Computing', 'Segurança da Informação']
        }
        
        areas_afins = mapeamento_afinidade.get(profissao_atual, self.areas_carreira)
        
        if objetivo == 'Realocar Carreira':
            # Maior chance de escolher áreas diferentes
            return np.random.choice(self.areas_carreira)
        else:
            # Maior chance de escolher áreas afins
            return np.random.choice(areas_afins)
    
    def _calcular_score_adequacao(self, anos_exp, nivel, tempo_estudo, num_habilidades, motivacao, objetivo):
        """
        Calcula o score de adequação do profissional para a área escolhida
        
        Fatores considerados:
        - Experiência profissional
        - Tempo disponível para estudo
        - Número de habilidades relevantes
        - Motivação
        - Alinhamento do objetivo
        """
        score = 50  # Base
        
        # Experiência (peso 20%)
        if nivel == 'Júnior':
            score += 5
        elif nivel == 'Pleno':
            score += 15
        else:  # Sênior
            score += 20
        
        # Tempo de estudo (peso 25%)
        score += (tempo_estudo / 30) * 25
        
        # Habilidades (peso 20%)
        score += (num_habilidades / 7) * 20
        
        # Motivação (peso 20%)
        score += (motivacao / 10) * 20
        
        # Objetivo (peso 15%)
        if objetivo == 'Atualizar Carreira':
            score += 15  # Atualizar é geralmente mais fácil que realocar
        else:
            score += 5
        
        return score
    
    def salvar_dataset(self, df, caminho='data/dataset_profissionais.csv'):
        """Salva o dataset em arquivo CSV"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        df.to_csv(caminho, index=False, encoding='utf-8')
        print(f"✅ Dataset salvo em: {caminho}")
        print(f"📊 Total de amostras: {len(df)}")
        return caminho


def main():
    """Função principal para gerar e salvar o dataset"""
    print("=" * 70)
    print("GERADOR DE DADOS SINTÉTICOS - SKILLBRIDGE")
    print("Sistema de Recomendação de Carreira - FIAP Global Solution 2025")
    print("=" * 70)
    
    generator = DataGenerator()
    
    # Gerar dataset com 1000 amostras
    print("\n🔄 Gerando dataset sintético...")
    df = generator.gerar_dataset(n_amostras=1000)
    
    # Mostrar informações do dataset
    print("\n📋 Informações do Dataset:")
    print(f"   - Forma: {df.shape}")
    print(f"   - Colunas: {list(df.columns)}")
    
    print("\n📊 Estatísticas Descritivas:")
    print(df.describe())
    
    print("\n🎯 Distribuição por Área de Interesse:")
    print(df['area_interesse'].value_counts())
    
    print("\n🎯 Distribuição por Objetivo:")
    print(df['objetivo_principal'].value_counts())
    
    # Salvar dataset
    caminho = generator.salvar_dataset(df, 'data/dataset_profissionais.csv')
    
    print("\n" + "=" * 70)
    print("✅ Dataset gerado com sucesso!")
    print("=" * 70)


if __name__ == "__main__":
    main()
"""
Módulo de Predição ML ajustado com paths absolutos e tratamento seguro
"""

import pickle
import os
import numpy as np
import json


class MLPredictor:
    """Classe para fazer predições usando os modelos treinados"""

    def __init__(self, models_dir=None):
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = models_dir if models_dir else os.path.join(self.BASE_DIR, "models")


        # Estruturas internas
        self.clf_models = {}
        self.reg_models = {}
        self.label_encoders = {}
        self.scaler = None
        self.resultados_treinamento = {}

        self._carregar_modelos()

    def _carregar_modelos(self):
        print("📂 Carregando modelos treinados...")

        # Carregar classificação
        for nome in ["RandomForest", "GradientBoosting"]:
            path = os.path.join(self.models_dir, f"clf_{nome}.pkl")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.clf_models[nome] = pickle.load(f)
                print(f"   ✓ {nome} (Classificação)")

        # Carregar regressão
        for nome in ["RandomForest", "LinearRegression"]:
            path = os.path.join(self.models_dir, f"reg_{nome}.pkl")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.reg_models[nome] = pickle.load(f)
                print(f"   ✓ {nome} (Regressão)")

        # Carregar encoders
        enc_path = os.path.join(self.models_dir, "label_encoders.pkl")
        if os.path.exists(enc_path):
            with open(enc_path, "rb") as f:
                self.label_encoders = pickle.load(f)
            print("   ✓ Label Encoders")

        # Carregar scaler
        scaler_path = os.path.join(self.models_dir, "scaler.pkl")
        if os.path.exists(scaler_path):
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            print("   ✓ Scaler")

        # Carregar resultados
        resultados_path = os.path.join(self.models_dir, "resultados.json")
        if os.path.exists(resultados_path):
            with open(resultados_path, "r", encoding="utf-8") as f:
                self.resultados_treinamento = json.load(f)
            print("   ✓ Resultados de Treinamento")

        print("✅ Modelos carregados!\n")

    def _safe_encode(self, encoder, value):
        """Evita erro caso o valor não esteja no encoder"""
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        else:
            return 0  # fallback seguro

    def preparar_input(self, formulario):

        prof = formulario.get('profissao_atual', 'Desenvolvedor')
        prof_encoded = self._safe_encode(self.label_encoders['profissao_atual'], prof)

        anos_exp = int(formulario.get("anos_experiencia", 3))

        if anos_exp < 3:
            nivel = "Júnior"
        elif anos_exp < 7:
            nivel = "Pleno"
        else:
            nivel = "Sênior"

        nivel_encoded = self._safe_encode(self.label_encoders['nivel_atual'], nivel)

        objetivo = formulario.get("objetivo_principal", "Atualizar Carreira")
        objetivo_encoded = self._safe_encode(self.label_encoders['objetivo_principal'], objetivo)

        tempo_estudo = formulario.get("tempo_disponivel_estudo", "10")
        tempo_estudo = int(tempo_estudo.split()[0])

        habilidades = formulario.get("habilidades_atuais_hard", [])
        if isinstance(habilidades, str):
            habilidades = [h.strip() for h in habilidades.split(",")]
        num_habilidades = len(habilidades)

        motivacao = 8

        features = np.array([[
            prof_encoded,
            anos_exp,
            nivel_encoded,
            objetivo_encoded,
            tempo_estudo,
            num_habilidades,
            motivacao
        ]])

        return features

    def prever(self, formulario):

        print("🔮 Fazendo predições...")

        X = self.preparar_input(formulario)
        X_scaled = self.scaler.transform(X) if self.scaler else X

        resultados = {"classificacao": {}, "regressao": {}, "recomendacao_final": {}}

        # Classificação
        for nome, modelo in self.clf_models.items():

            pred_encoded = modelo.predict(X)[0]
            pred_proba = modelo.predict_proba(X)[0]

            area_pred = self.label_encoders["area_interesse"].inverse_transform([pred_encoded])[0]

            top_idx = np.argsort(pred_proba)[-3:][::-1]
            top_areas = [{
                "area": self.label_encoders["area_interesse"].inverse_transform([i])[0],
                "probabilidade": float(pred_proba[i]),
                "percentual": f"{pred_proba[i] * 100:.1f}%"
            } for i in top_idx]

            resultados["classificacao"][nome] = {
                "area_prevista": area_pred,
                "confianca": float(pred_proba.max()),
                "top_3_areas": top_areas
            }

        # Regressão
        for nome, modelo in self.reg_models.items():

            pred_score = modelo.predict(X_scaled)[0]
            pred_score = float(np.clip(pred_score, 0, 100))

            resultados["regressao"][nome] = {
                "score_adequacao": pred_score,
                "nivel_adequacao": self._classificar_score(pred_score)
            }

        # Consolidação final
        from collections import Counter

        areas = [r["area_prevista"] for r in resultados["classificacao"].values()]
        area_final = Counter(areas).most_common(1)[0][0]

        scores = [r["score_adequacao"] for r in resultados["regressao"].values()]
        score_final = float(np.mean(scores))

        resultados["recomendacao_final"] = {
            "area_recomendada": area_final,
            "score_adequacao": score_final,
            "nivel_adequacao": self._classificar_score(score_final),
            "consenso_modelos": areas.count(area_final)
        }

        return resultados

    def _classificar_score(self, score):
        if score >= 80:
            return "Excelente"
        if score >= 65:
            return "Muito Bom"
        if score >= 50:
            return "Bom"
        if score >= 35:
            return "Regular"
        return "Baixo"


# ====== EXECUÇÃO DE TESTE OPCIONAL ======
if __name__ == "__main__":
    predictor = MLPredictor()
    print("TESTE OK")

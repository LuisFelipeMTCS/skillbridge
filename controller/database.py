import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseDB:
    """Gerenciador de conexão com Firebase Firestore"""
    
    _instance = None
    COLLECTION_NAME = 'alura'  # ✅ Nome da coleção definido aqui
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseDB, cls).__new__(cls)
            cls._instance.db = None
            cls._instance.app = None
            cls._instance._initialized = False
        return cls._instance
    
    def connect(self):
        """Conectar ao Firestore"""
        try:
            # Verificar se já foi inicializado
            if self._initialized and self.db:
                return True
            
            # Verificar se já existe app Firebase
            if not firebase_admin._apps:
                # ✅ PASSO 1: Carregar credenciais
                cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase-credentials.json")
                
                if not os.path.exists(cred_path):
                    print(f"❌ Arquivo não encontrado: {cred_path}")
                    print(f"📂 Diretório atual: {os.getcwd()}")
                    return False
                
                # ✅ PASSO 2: Inicializar Firebase App
                print(f"🔥 Inicializando Firebase com: {cred_path}")
                cred = credentials.Certificate(cred_path)
                self.app = firebase_admin.initialize_app(cred)
                print("✅ Firebase App inicializado!")
            
            # ✅ PASSO 3: Obter cliente Firestore
            self.db = firestore.client()
            self._initialized = True
            print(f"✅ Conectado ao Firestore! Usando coleção: '{self.COLLECTION_NAME}'")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def inserir_cursos(self, cursos):
        """Inserir cursos no Firestore"""
        try:
            if not self.connect():
                return False
            
            # ✅ Usar o nome da coleção definido
            collection_ref = self.db.collection(self.COLLECTION_NAME)
            
            # Limpar coleção
            print(f"🗑️  Limpando coleção '{self.COLLECTION_NAME}'...")
            docs = collection_ref.limit(500).stream()
            batch = self.db.batch()
            count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                count += 1
                if count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()
            
            if count > 0:
                batch.commit()
                print(f"   Removidos {count} cursos antigos")
            
            # Inserir novos
            print(f"💾 Inserindo {len(cursos)} cursos na coleção '{self.COLLECTION_NAME}'...")
            batch = self.db.batch()
            count = 0
            
            for curso in cursos:
                doc_ref = collection_ref.document()
                batch.set(doc_ref, curso)
                count += 1
                
                if count % 500 == 0:
                    batch.commit()
                    print(f"   ✓ {count}/{len(cursos)} salvos...")
                    batch = self.db.batch()
            
            # Commit final
            if count % 500 != 0:
                batch.commit()
            
            print(f"✅ {len(cursos)} cursos salvos com sucesso na coleção '{self.COLLECTION_NAME}'!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inserir: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def buscar_cursos(self, limite=None):
        """Buscar todos os cursos"""
        try:
            if not self.connect():
                return []
            
            # ✅ Usar o nome da coleção definido
            collection_ref = self.db.collection(self.COLLECTION_NAME)
            
            if limite:
                docs = collection_ref.limit(limite).stream()
            else:
                docs = collection_ref.stream()
            
            cursos = []
            for doc in docs:
                curso = doc.to_dict()
                cursos.append(curso)
            
            print(f"✅ {len(cursos)} cursos carregados da coleção '{self.COLLECTION_NAME}'")
            return cursos
            
        except Exception as e:
            print(f"❌ Erro ao buscar: {e}")
            return []
    
    def buscar_cursos_filtrados(self, area_interesse=None, habilidades=None):
        """Buscar cursos filtrados"""
        try:
            cursos = self.buscar_cursos()
            
            if not cursos:
                return []
            
            area_lower = area_interesse.lower() if area_interesse else ""
            habilidades_lower = [h.lower() for h in habilidades] if habilidades else []
            
            cursos_relevantes = []
            
            for curso in cursos:
                titulo = curso.get("titulo", "").lower()
                aprendizado = curso.get("aprendizado", "").lower()
                publico = curso.get("publico_alvo", "").lower()
                texto_completo = titulo + aprendizado + publico
                
                if area_lower and area_lower in texto_completo:
                    cursos_relevantes.append(curso)
                elif any(skill in texto_completo for skill in habilidades_lower):
                    cursos_relevantes.append(curso)
            
            return cursos_relevantes if cursos_relevantes else cursos[:50]
            
        except Exception as e:
            print(f"❌ Erro ao filtrar: {e}")
            return []
    
    def contar_cursos(self):
        """Contar total de cursos"""
        try:
            if not self.connect():
                return 0
            
            # ✅ Usar o nome da coleção definido
            docs = self.db.collection(self.COLLECTION_NAME).stream()
            count = sum(1 for _ in docs)
            return count
            
        except Exception as e:
            print(f"❌ Erro ao contar: {e}")
            return 0

# Instância global
firebase_db = FirebaseDB()
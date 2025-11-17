# 🚀 Sistema de Recomendação de Carreira Alura com IA

Sistema inteligente que recomenda cursos da Alura baseado no perfil profissional e objetivos de carreira do usuário, gerando um plano personalizado em PDF usando IA Gemini.

## 📋 Funcionalidades

- ✅ Scraper automatizado de cursos da Alura
- ✅ Formulário interativo para coleta de dados do profissional
- ✅ Recomendações personalizadas com IA (Gemini)
- ✅ Geração de PDF organizado e profissional
- ✅ Interface web moderna e responsiva
- ✅ Suporte para realocação ou atualização de carreira

## 🛠️ Tecnologias

- **Backend**: Flask (Python)
- **Scraping**: requests + lxml
- **IA**: Google Gemini API
- **PDF**: FPDF
- **Frontend**: HTML/CSS/JavaScript

## 📁 Estrutura do Projeto
```
projeto_alura/
├── data/
│   └── cursos_alura.json          # Dados dos cursos (gerado)
├── templates/
│   └── dashboard.html              # Interface do usuário
├── alura_scraper.py                # Coleta cursos da Alura
├── gpt_recommender.py              # Gera recomendações com IA
├── save_pdf.py                     # Cria PDF formatado
├── main.py                         # Servidor Flask
├── requirements.txt                # Dependências
└── README.md                       # Este arquivo
```

## 🚀 Como Usar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar API Gemini

Obtenha sua chave em: https://makersuite.google.com/app/apikey

Opção 1 - Variável de ambiente (recomendado):
```bash
export GEMINI_API_KEY="sua_chave_aqui"
```

Opção 2 - Direto no código (gpt_recommender.py linha 34):
```python
API_KEY = "sua_chave_aqui"
```

### 3. Executar o Scraper (opcional)

Se você já tem o arquivo `cursos_alura.json`, pule esta etapa.
```bash
python alura_scraper.py
```

Isso criará o arquivo `data/cursos_alura.json` com todos os cursos.

### 4. Iniciar o Sistema
```bash
python main.py
```

### 5. Acessar a Interface

Abra seu navegador em: `http://localhost:5000`

## 📝 Como Funciona

### Fluxo do Sistema:

1. **Coleta de Dados** (alura_scraper.py)
   - Scraper acessa site da Alura
   - Extrai título, URL, aprendizado e público-alvo
   - Salva em JSON

2. **Interface Web** (dashboard.html)
   - Usuário preenche formulário
   - Escolhe: Atualizar ou Realocar carreira
   - Informa habilidades, experiência, objetivos

3. **Processamento IA** (gpt_recommender.py)
   - Recebe dados do formulário
   - Filtra cursos relevantes
   - Gemini gera plano personalizado

4. **Geração PDF** (save_pdf.py)
   - Formata texto da IA
   - Cria PDF estruturado
   - Salva na pasta Downloads

## 🎯 Exemplo de Uso
```python
# Exemplo de dados enviados pelo formulário:
formulario = {
    "objetivo_principal": "Realocar Carreira",
    "profissao_atual": "QA Tester",
    "anos_experiencia": 5,
    "nivel_atual": "Pleno",
    "nova_area_interesse": "Automação de Testes",
    "habilidades_atuais_hard": ["Selenium", "SQL"],
    "tempo_disponivel_estudo": "20 horas/semana"
}

# O sistema gera um PDF com:
# - Análise do perfil
# - 10+ cursos recomendados
# - Linha de carreira passo a passo
# - Plano de ação prático
```

## ⚙️ Configurações Avançadas

### Alterar Porta do Servidor

Em `main.py`, linha final:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Mude 5000 para outra porta
```

### Mudar Pasta de Salvamento do PDF

Em `save_pdf.py`, linha 43:
```python
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
# Altere para: downloads_path = "/seu/caminho/personalizado"
```

## 🐛 Solução de Problemas

### Erro: "Arquivo de cursos não encontrado"
- Execute primeiro: `python alura_scraper.py`
- Verifique se existe: `data/cursos_alura.json`

### Erro na API Gemini
- Verifique se configurou a chave corretamente
- Teste a chave em: https://makersuite.google.com/

### PDF não salva
- Verifique permissões da pasta Downloads
- Veja os logs no terminal para erros específicos

## 📦 Dependências

- `flask`: Servidor web
- `requests`: HTTP requests
- `lxml`: Parse HTML
- `google-generativeai`: API Gemini
- `fpdf`: Geração de PDF

## 🔒 Segurança

⚠️ **IMPORTANTE**: Nunca commite sua chave da API no GitHub!

Use `.gitignore`:
```
.env
*.pkl
__pycache__/
data/cursos_alura.json
```

## 📄 Licença

Projeto educacional - Uso livre

## 👨‍💻 Autor

Criado com ❤️ para ajudar profissionais a planejarem suas carreiras

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas!

---

**Dúvidas?** Abra uma issue ou entre em contato!
```

---

## 🎯 **COMO CONECTAR TUDO - PASSO A PASSO**

### **1. Organizar os Arquivos**
```
projeto_alura/
├── data/                          ← Criar esta pasta
│   └── cursos_alura.json         ← Copiar seu arquivo aqui
├── templates/                     ← Criar esta pasta
│   └── dashboard.html            ← Criar arquivo novo acima
├── alura_scraper.py              ← Já existe
├── gpt_recommender.py            ← Substituir pelo ajustado acima
├── save_pdf.py                   ← Já existe
├── main.py                       ← Criar arquivo novo acima
├── requirements.txt              ← Substituir pelo acima
└── README.md                     ← Criar arquivo acima
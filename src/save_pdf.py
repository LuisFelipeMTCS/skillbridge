from fpdf import FPDF
import os
import re

class PDF_Profissional(FPDF):
    def header(self):
        """Cabeçalho personalizado"""
        # Logo ou título
        self.set_font('Arial', 'B', 20)
        self.set_text_color(67, 97, 238)  # Azul
        self.cell(0, 15, 'PLANO DE CARREIRA ALURA', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """Rodapé personalizado"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def titulo_secao(self, titulo):
        """Título de seção estilizado"""
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(67, 97, 238)  # Azul
        self.set_text_color(255, 255, 255)  # Branco
        self.cell(0, 12, f'  {titulo}', 0, 1, 'L', True)
        self.ln(4)
        self.set_text_color(0, 0, 0)  # Voltar para preto

    def subtitulo(self, texto):
        """Subtítulo"""
        self.set_font('Arial', 'B', 13)
        self.set_text_color(67, 97, 238)
        self.cell(0, 8, texto, 0, 1, 'L')
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def paragrafo(self, texto):
        """Parágrafo normal"""
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, texto)
        self.ln(2)

    def item_lista(self, texto):
        """Item de lista com bullet"""
        self.set_font('Arial', '', 11)
        self.cell(8)  # Indentação
        self.set_font('Arial', 'B', 11)
        self.cell(5, 6, chr(149), 0, 0)  # Bullet point
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, texto)

    def curso_destaque(self, numero, titulo, url, aprendizado):
        """Card de curso destacado"""
        # Fundo cinza claro
        self.set_fill_color(245, 245, 245)
        self.rect(self.get_x(), self.get_y(), 190, 2, 'F')
        
        # Número do curso
        self.set_font('Arial', 'B', 12)
        self.set_text_color(67, 97, 238)
        self.cell(0, 7, f'{numero}. {titulo}', 0, 1, 'L')
        
        # URL
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(8)
        self.cell(0, 5, f'Link: {url[:70]}...', 0, 1, 'L')
        
        # Aprendizado
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(8)
        self.multi_cell(0, 5, f'{aprendizado}')
        self.ln(3)
        self.set_text_color(0, 0, 0)

def limpar_texto(texto):
    """Remove caracteres problemáticos"""
    substituicoes = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E',
        'Í': 'I', 'Ó': 'O', 'Õ': 'O', 'Ô': 'O',
        'Ú': 'U', 'Ç': 'C',
        '"': '"', '"': '"', ''': "'", ''': "'",
        '–': '-', '—': '-',
    }
    
    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)
    
    return texto.encode('ascii', 'ignore').decode('ascii')

def processar_conteudo(texto):
    """Processa e estrutura o texto da IA"""
    texto = limpar_texto(texto)
    linhas = texto.split('\n')
    
    estrutura = []
    secao_atual = None
    
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha == '-':
            continue
        
        # Detectar seções principais
        if re.match(r'^[0-9]+\.\s+[A-Z\s]+$', linha):
            secao_atual = linha
            estrutura.append({'tipo': 'secao', 'conteudo': linha})
        # Detectar subtítulos
        elif linha.startswith('- ') and linha[2:3].isupper():
            estrutura.append({'tipo': 'subtitulo', 'conteudo': linha[2:]})
        # Detectar itens de lista
        elif linha.startswith('- '):
            estrutura.append({'tipo': 'lista', 'conteudo': linha[2:]})
        # Detectar cursos (formato especial)
        elif re.match(r'^[0-9]+\.\s+.+:', linha):
            estrutura.append({'tipo': 'curso_titulo', 'conteudo': linha})
        elif linha.startswith('URL:'):
            estrutura.append({'tipo': 'curso_url', 'conteudo': linha[4:].strip()})
        elif linha.startswith('Aprendizado:'):
            estrutura.append({'tipo': 'curso_aprendizado', 'conteudo': linha[12:].strip()})
        # Parágrafos normais
        else:
            estrutura.append({'tipo': 'paragrafo', 'conteudo': linha})
    
    return estrutura

def salvar_pdf_organizado(texto, nome_arquivo="Plano_de_Carreira.pdf"):
    """Salva PDF com design profissional"""
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    caminho_completo = os.path.join(downloads_path, nome_arquivo)

    pdf = PDF_Profissional()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    estrutura = processar_conteudo(texto)
    
    curso_temp = {}
    
    for item in estrutura:
        tipo = item['tipo']
        conteudo = item['conteudo']
        
        try:
            if tipo == 'secao':
                pdf.ln(3)
                pdf.titulo_secao(conteudo)
                
            elif tipo == 'subtitulo':
                pdf.subtitulo(conteudo)
                
            elif tipo == 'lista':
                pdf.item_lista(conteudo)
                
            elif tipo == 'curso_titulo':
                curso_temp = {'titulo': conteudo}
                
            elif tipo == 'curso_url':
                curso_temp['url'] = conteudo
                
            elif tipo == 'curso_aprendizado':
                curso_temp['aprendizado'] = conteudo
                if 'titulo' in curso_temp and 'url' in curso_temp:
                    # Extrair número
                    match = re.match(r'^([0-9]+)\.\s+(.+):', curso_temp['titulo'])
                    if match:
                        num = match.group(1)
                        titulo = match.group(2)
                        pdf.curso_destaque(
                            num, 
                            titulo, 
                            curso_temp['url'],
                            curso_temp['aprendizado']
                        )
                curso_temp = {}
                
            elif tipo == 'paragrafo':
                pdf.paragrafo(conteudo)
                
        except Exception as e:
            print(f"Erro ao processar item: {e}")
            continue

    pdf.output(caminho_completo)
    print(f"✅ PDF salvo em: {caminho_completo}")
    return caminho_completo
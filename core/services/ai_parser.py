import os
import json
import tempfile
import google.generativeai as genai
from django.conf import settings

def extrair_aulas_extras_com_ia(file_obj, filename, ano_letivo):
    """
    Recebe um arquivo (PDF/Imagem), envia para o Gemini Vision e extrai 
    os dados no formato JSON esperado.
    Retorna uma lista de dicionários.
    """
    api_key = os.environ.get("GEMINI_API_KEY", getattr(settings, 'GEMINI_API_KEY', None))
    if not api_key:
        raise Exception("Chave GEMINI_API_KEY não configurada no servidor.")
        
    genai.configure(api_key=api_key)
    
    # 1. Salvar arquivo temporário (pois genai.upload_file precisa de path em disco)
    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
    try:
        with os.fdopen(fd, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
                
        # 2. Upload para o Gemini
        try:
            uploaded_file = genai.upload_file(temp_path)
        except Exception as e:
            raise Exception(f"Falha ao enviar arquivo para o Google Gemini: {str(e)}")
        
        # 3. Prompt detalhado
        prompt = f"""
Você é um assistente acadêmico especializado em extrair dados de calendários de escolas.
Estou fornecendo o calendário de "Aulas Extras" e "Eletivas" do ano letivo de {ano_letivo}.

A tabela pode ter a data/dia, o horário e as disciplinas divididas por colunas para cada turma (ex: Turma 31, Turma 32, Turma 11, etc.).
No calendário, pode haver nomes de professores com a disciplina entre parênteses. 
Exemplo: "THEREZA (Lit)" para a "Turma 31", no dia 02/3 das 14h às 15h30.

Sua tarefa é ler TODO o documento e gerar UMA LISTA estruturada em formato JSON estrito, extraindo CADA célula de aula como um registro individual.

Regras de Mapeamento de Nomes de Disciplinas:
- Se for 3ª Série (ex: Turma 31, 32):
  - "Mat" ou "Geom" -> "Aprofundamento em Matemática"
  - "Lit" ou "Port" ou "Redação" -> "Aprofundamento em Linguagens"
  - "Bio", "Quí", "Fís", "Natureza" -> "Aprofundamento em Ciências da Natureza"
  - "His", "Geo", "Humanas" -> "Aprofundamento em Ciências Humanas"
- Se for 1ª Série (ex: Turma 11, 12, 13):
  - "Sociedade e Cidadania", "Sustentabilidade e Meio Ambiente"
- Se for 2ª Série (ex: Turma 21, 22, 23):
  - "Educação Financeira", "Múltiplas Linguagens"

Regras do JSON:
Deve ser puramente um array JSON de objetos, com as seguintes chaves exatas:
"data": formato "DD/MM/AAAA". (infira o ano como {ano_letivo} se não estiver escrito).
"horario": texto (ex: "14h às 15h30"). Opcional se não houver.
"turma": texto (apenas os números, ex: "31", "12").
"disciplina": texto (use os nomes completos descritos nas Regras de Mapeamento, sem abreviações).
"professor": texto (o nome do professor, ex: "Thereza", "Silvio", sem parênteses).

ATENÇÃO: Retorne APENAS o JSON válido dentro de um bloco ```json ... ```, sem explicações adicionais.
"""
        # 4. Chamada da IA
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            [uploaded_file, prompt],
            request_options={"timeout": 60}
        )
        
        # 5. Processar saída JSON
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        try:
            dados = json.loads(text.strip())
            return dados
        except json.JSONDecodeError:
            raise Exception("O Gemini retornou um formato inválido. Tente novamente.")
            
    finally:
        os.remove(temp_path)

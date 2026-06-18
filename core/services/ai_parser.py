import os
import json
import tempfile
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

    try:
        from google import genai
        from google.genai import types
        NEW_SDK = True
    except ImportError:
        import google.generativeai as genai_old
        NEW_SDK = False

    # 1. Salvar arquivo temporário
    ext = os.path.splitext(filename)[1].lower() or '.pdf'
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        # 2. Montar Prompt
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
  - "Bio", "Qui", "Fis", "Natureza" -> "Aprofundamento em Ciências da Natureza"
  - "His", "Geo", "Humanas" -> "Aprofundamento em Ciências Humanas"
- Se for 1ª Série (ex: Turma 11, 12, 13):
  - Disciplinas: "Sociedade e Cidadania", "Sustentabilidade e Meio Ambiente"
- Se for 2ª Série (ex: Turma 21, 22, 23):
  - Disciplinas: "Educação Financeira", "Múltiplas Linguagens"

Regras do JSON:
Deve ser puramente um array JSON de objetos, com as seguintes chaves exatas:
"data": formato "DD/MM/AAAA". (infira o ano como {ano_letivo} se não estiver escrito).
"horario": texto (ex: "14h às 15h30"). Opcional se não houver.
"turma": texto (apenas os números, ex: "31", "12").
"disciplina": texto (use os nomes completos das Regras de Mapeamento, sem abreviações).
"professor": texto (o nome do professor, ex: "Thereza", "Silvio", sem parênteses).

ATENÇÃO: Retorne APENAS o JSON válido dentro de um bloco ```json ... ```, sem explicações adicionais.
Ignore células com seta "←" (elas indicam que é a mesma aula da turma ao lado).
"""

        # 3. Chamar a IA (tenta nova SDK, depois antiga como fallback)
        if NEW_SDK:
            client = genai.Client(api_key=api_key)

            with open(temp_path, 'rb') as f:
                file_bytes = f.read()

            # Detectar mime_type
            if ext in ['.pdf']:
                mime_type = 'application/pdf'
            elif ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            else:
                mime_type = 'application/pdf'

            # Tenta os modelos em ordem de prioridade (do mais leve ao mais pesado)
            models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-lite', 'gemini-2.0-flash']
            last_error = None
            response = None
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                            prompt
                        ]
                    )
                    break  # Sucesso — sai do loop
                except Exception as e:
                    last_error = e
                    if '429' in str(e) or '404' in str(e) or 'not found' in str(e).lower() or 'exhausted' in str(e).lower():
                        continue  # Tenta o próximo modelo
                    else:
                        raise e  # Erro diferente — re-levanta
            if response is None:
                raise Exception(f"Nenhum modelo Gemini disponível: {str(last_error)}")
            text = response.text.strip()
        else:
            # Fallback: biblioteca antiga
            import google.generativeai as genai_old
            genai_old.configure(api_key=api_key)
            uploaded = genai_old.upload_file(temp_path)
            model = genai_old.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([uploaded, prompt])
            text = response.text.strip()

        # 4. Processar saída JSON
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            dados = json.loads(text.strip())
            return dados
        except json.JSONDecodeError as e:
            raise Exception(f"O Gemini retornou um formato inválido. Detalhe: {str(e)}\n\nResposta recebida: {text[:300]}")

    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass

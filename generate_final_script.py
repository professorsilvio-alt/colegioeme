import json
import os

# Load the data
with open('suggestions_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The logic template
logic = f"""import os
import django
import sys

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
    django.setup()
    from core.models import SugestaoConteudo, Disciplina, Turma
    print('Django inicializado com sucesso.')
except Exception as e:
    print(f'Erro na inicializa\\u00e7\\u00e3o do Django: {{e}}')
    sys.exit(1)

DATA = {json.dumps(data, indent=2)}

def run_import():
    print(f'Iniciando importa\\u00e7\\u00e3o de {{len(DATA)}} sugest\\u00f5es...')
    
    if not Disciplina.objects.exists():
        print('ERRO: N\\u00e3o existem disciplinas cadastradas no banco!')
        return
    if not Turma.objects.exists():
        print('ERRO: N\\u00e3o existem turmas cadastradas no banco!')
        return

    created_count = 0
    updated_count = 0
    
    for item in DATA:
        disc_nome = item.get('disc')
        texto = item.get('texto')
        turmas_cods = item.get('turmas')
        
        try:
            # 1. Obter ou criar a disciplina
            disciplina, _ = Disciplina.objects.get_or_create(nome=disc_nome)
            
            # 2. Criar a sugest\\u00e3o
            sugestao, created = SugestaoConteudo.objects.get_or_create(
                disciplina=disciplina,
                texto=texto
            )
            
            # 3. Vincular as turmas
            if turmas_cods:
                turmas = Turma.objects.filter(codigo__in=turmas_cods)
                sugestao.turmas.set(turmas)
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        except Exception as ex:
            print(f'Erro ao importar item: {{ex}}')

    print(f'Processo finalizado!')
    print(f'- Criadas: {{created_count}}')
    print(f'- Atualizadas: {{updated_count}}')

if __name__ == "__main__":
    run_import()
"""

with open('import_final.py', 'w', encoding='utf-8') as f:
    f.write(logic)

print("import_final.py gerado com sucesso.")

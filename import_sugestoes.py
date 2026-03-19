import os
import django

# Setup Django atmosphere
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from core.models import SugestaoConteudo, Disciplina, Turma

DATA = [
    # Full data will be injected here or provided to the user
]

def run_import():
    print(f"Iniciando importação de {len(DATA)} sugestões...")
    created_count = 0
    
    for item in DATA:
        disc_nome = item['disc']
        texto = item['texto']
        turmas_cods = item['turmas']
        
        # 1. Obter ou criar a disciplina
        disciplina, _ = Disciplina.objects.get_or_create(nome=disc_nome)
        
        # 2. Criar a sugestão (usando get_or_create para evitar duplicidade)
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

    print(f"Importação concluída! {created_count} novas sugestões criadas.")

if __name__ == "__main__":
    run_import()

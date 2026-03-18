import os
import django
from django.db import transaction
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from core.models import ConteudoProgramatico

def run_split():
    # Find all ConteudoProgramatico that have more than 1 turma
    conteudos_multiples = ConteudoProgramatico.objects.annotate(num_turmas=Count('turmas')).filter(num_turmas__gt=1)
    
    count = conteudos_multiples.count()
    print(f"Found {count} conteudos with multiple turmas.")
    
    with transaction.atomic():
        for cp in conteudos_multiples:
            turmas = list(cp.turmas.all())
            print(f"Splitting CP ID {cp.pk} with turmas: {[t.codigo for t in turmas]}")
            
            # Keep the first turma in the original CP
            primeira_turma = turmas[0]
            turmas_restantes = turmas[1:]
            
            # Update the original CP to only have the first turma
            cp.turmas.set([primeira_turma])
            
            # For each remaining turma, create a copy of CP
            for t in turmas_restantes:
                nova_cp = ConteudoProgramatico.objects.create(
                    data=cp.data,
                    professor=cp.professor,
                    disciplina=cp.disciplina,
                    descricao=cp.descricao
                )
                nova_cp.turmas.add(t)
                
    print(f"Successfully split {count} records!")

if __name__ == '__main__':
    run_split()

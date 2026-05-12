import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'eme_project.settings'
django.setup()
from core.models import Aluno

alunos = Aluno.objects.filter(turma__codigo__in=['61', '62', '63'])

with open('core/management/commands/cadastrar_6ano.py', 'w', encoding='utf-8') as f:
    f.write('''import os
from django.core.management.base import BaseCommand
from core.models import Aluno, Turma

class Command(BaseCommand):
    help = 'Cadastra alunos do 6o ano que foram extraidos localmente.'

    def handle(self, *args, **options):
        dados = [
''')
    for a in alunos:
        f.write(f'            ("{a.turma.codigo}", "{a.nome}", "{a.foto.name if a.foto else ""}"),\n')
    f.write('''        ]
        criados = 0
        for cod_turma, nome, foto_name in dados:
            try:
                turma = Turma.objects.get(codigo=cod_turma)
                aluno, created = Aluno.objects.get_or_create(turma=turma, nome=nome)
                if foto_name:
                    aluno.foto.name = foto_name
                    aluno.save(update_fields=['foto'])
                if created:
                    criados += 1
            except Turma.DoesNotExist:
                self.stdout.write(f'Turma {cod_turma} nao encontrada.')
        
        self.stdout.write(self.style.SUCCESS(f'Concluido! {criados} alunos do 6o ano criados/atualizados.'))
''')

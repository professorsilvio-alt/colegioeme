import os
import re
from django.core.management.base import BaseCommand
from core.models import Aluno
from django.conf import settings

class Command(BaseCommand):
    help = 'Vincula fotos existentes na pasta media aos alunos no banco de dados.'

    def handle(self, *args, **options):
        fotos_dir = os.path.join(settings.MEDIA_ROOT, 'alunos', 'fotos')
        if not os.path.exists(fotos_dir):
            self.stdout.write(self.style.ERROR(f'A pasta {fotos_dir} nao existe.'))
            return

        alunos = Aluno.objects.all()
        vinculados = 0
        nao_encontrados = 0

        for aluno in alunos:
            # Recria o mesmo nome de arquivo gerado pelo importar_fotos_pdf
            nome_arquivo = f'{aluno.turma.codigo}_{re.sub(r"[^a-zA-Z0-9]", "_", aluno.nome.lower())}.jpg'
            caminho_completo = os.path.join(fotos_dir, nome_arquivo)

            if os.path.exists(caminho_completo):
                # Salva apenas o caminho relativo no banco (ex: alunos/fotos/arquivo.jpg)
                aluno.foto.name = f'alunos/fotos/{nome_arquivo}'
                aluno.save(update_fields=['foto'])
                vinculados += 1
            else:
                nao_encontrados += 1

        self.stdout.write(self.style.SUCCESS(f'Concluido! {vinculados} fotos vinculadas aos alunos.'))
        if nao_encontrados > 0:
            self.stdout.write(self.style.WARNING(f'{nao_encontrados} alunos continuam sem foto na pasta.'))

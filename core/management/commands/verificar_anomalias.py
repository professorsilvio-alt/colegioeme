from django.core.management.base import BaseCommand
from core.models import ConteudoProgramatico, GradeHoraria
from collections import defaultdict

class Command(BaseCommand):
    help = 'Procura por lançamentos em dias da semana em que a turma não possui aula da respectiva disciplina (Anomalias).'

    def handle(self, *args, **kwargs):
        all_conteudos = ConteudoProgramatico.objects.all().prefetch_related('turmas', 'professor', 'disciplina')
        anomalies = []

        # wd: 0=Mon, ..., 4=Fri -> dia_semana_str: 1=Mon, ..., 5=Fri
        for cont in all_conteudos:
            if not cont.data or not cont.professor or not cont.disciplina:
                continue
            
            wd = cont.data.weekday()
            if wd > 4:
                continue # Consideramos findes semana como propositais (Aula Extra)
            
            dia_semana_str = str(wd + 1)
            
            for turma in cont.turmas.all():
                grade_exists = GradeHoraria.objects.filter(
                    professor=cont.professor,
                    disciplina=cont.disciplina,
                    turma=turma,
                    dia_semana=dia_semana_str
                ).exists()
                
                if not grade_exists:
                    anomalies.append({
                        'id': cont.pk,
                        'data': cont.data,
                        'turma': turma.codigo,
                        'professor': cont.professor.nome,
                        'disciplina': cont.disciplina.nome,
                        'descricao': cont.descricao[:40]
                    })

        if anomalies:
            self.stdout.write(self.style.WARNING(f"\n FORAM ENCONTRADAS {len(anomalies)} ANOMALIAS:"))
            for a in anomalies:
                self.stdout.write(
                    f"ID: {a['id']:04d} | Data: {a['data'].strftime('%d/%m/%Y')} | "
                    f"Turma: {a['turma']:>3} | Prof: {a['professor'][:15]:<15} | "
                    f"Disc: {a['disciplina'][:20]:<20} | Resumo: {a['descricao']}"
                )
        else:
            self.stdout.write(self.style.SUCCESS(' Nenhuma anomalia de lançamento foi encontrada! Todos os lançamentos em dias úteis possuem grade horária.'))

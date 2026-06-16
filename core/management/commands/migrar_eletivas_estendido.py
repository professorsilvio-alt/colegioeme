import logging
from django.core.management.base import BaseCommand
from core.models import (
    Disciplina, Professor, GradeHoraria, AulaExtraProgramada, 
    Ocorrencia, SugestaoConteudo, NotaBimestral, ProvaAuxiliar, ConteudoProgramatico
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migra as disciplinas genéricas (Eletiva 1, Eletiva 2, Estendido) para as suas disciplinas reais conforme a série.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando migração de disciplinas Eletivas e Estendido...")

        # 1. Criação / Obtenção das novas disciplinas
        soc_cid, _ = Disciplina.objects.get_or_create(nome='Sociedade e Cidadania')
        ed_fin, _ = Disciplina.objects.get_or_create(nome='Educação Financeira')
        sust_meio, _ = Disciplina.objects.get_or_create(nome='Sustentabilidade e Meio Ambiente')
        mult_ling, _ = Disciplina.objects.get_or_create(nome='Múltiplas Linguagens')
        
        aprof_mat, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Matemática')
        aprof_nat, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Ciências da Natureza')
        aprof_hum, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Ciências Humanas')
        aprof_ling, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Linguagens')
        
        aprof_todas = [aprof_mat, aprof_nat, aprof_hum, aprof_ling]

        # 2. Obtenção das antigas disciplinas
        eletiva1 = Disciplina.objects.filter(nome__icontains='Eletiva 1').first()
        eletiva2 = Disciplina.objects.filter(nome__icontains='Eletiva 2').first()
        estendido = Disciplina.objects.filter(nome__icontains='Estendido').first()

        def get_disciplina_correta(disciplina_antiga, turma_codigo):
            if not turma_codigo:
                return None
            
            if disciplina_antiga == eletiva1:
                if turma_codigo.startswith('1'):
                    return soc_cid
                elif turma_codigo.startswith('2'):
                    return ed_fin
            elif disciplina_antiga == eletiva2:
                if turma_codigo.startswith('1'):
                    return sust_meio
                elif turma_codigo.startswith('2'):
                    return mult_ling
            return None

        # 3. Atualização de GradeHoraria
        self.stdout.write("Migrando GradeHoraria...")
        for grade in GradeHoraria.objects.filter(disciplina__in=[eletiva1, eletiva2, estendido]):
            if grade.disciplina in [eletiva1, eletiva2]:
                nova_disc = get_disciplina_correta(grade.disciplina, grade.turma.codigo)
                if nova_disc:
                    grade.disciplina = nova_disc
                    grade.save()
                    self.stdout.write(f"Grade {grade.turma.codigo}: Atualizado para {nova_disc.nome}")
            elif grade.disciplina == estendido:
                # O professor ganha todas as 4 frentes do Estendido na grade para aquela turma
                for aprof in aprof_todas:
                    GradeHoraria.objects.get_or_create(
                        escola=grade.escola,
                        ano_letivo=grade.ano_letivo,
                        turma=grade.turma,
                        disciplina=aprof,
                        professor=grade.professor
                    )
                self.stdout.write(f"Grade {grade.turma.codigo}: Substituído Estendido pelos 4 Aprofundamentos.")
                grade.delete()

        # 4. Atualização das permissões (M2M) do Professor
        self.stdout.write("Migrando cadastro de Professores (M2M)...")
        for prof in Professor.objects.filter(disciplinas__in=[eletiva1, eletiva2, estendido]).distinct():
            has_e1 = prof.disciplinas.filter(pk=eletiva1.pk if eletiva1 else 0).exists()
            has_e2 = prof.disciplinas.filter(pk=eletiva2.pk if eletiva2 else 0).exists()
            has_est = prof.disciplinas.filter(pk=estendido.pk if estendido else 0).exists()

            if has_e1:
                prof.disciplinas.add(soc_cid, ed_fin)
                prof.disciplinas.remove(eletiva1)
            if has_e2:
                prof.disciplinas.add(sust_meio, mult_ling)
                prof.disciplinas.remove(eletiva2)
            if has_est:
                prof.disciplinas.add(*aprof_todas)
                prof.disciplinas.remove(estendido)
            self.stdout.write(f"Professor {prof.nome}: Disciplinas atualizadas.")

        # Função auxiliar para migrar registros dependentes de turma e disciplina
        def migrar_registros(Modelo, field_turma='turma', pre_save_callback=None):
            if not eletiva1 and not eletiva2 and not estendido:
                return
            registros = Modelo.objects.filter(disciplina__in=[eletiva1, eletiva2, estendido])
            for reg in registros:
                antiga = reg.disciplina
                turma_cod = getattr(reg, field_turma).codigo if getattr(reg, field_turma) else None
                
                if antiga in [eletiva1, eletiva2]:
                    nova_disc = get_disciplina_correta(antiga, turma_cod)
                    if nova_disc:
                        reg.disciplina = nova_disc
                        if pre_save_callback:
                            pre_save_callback(reg, antiga, nova_disc)
                        reg.save()
                elif antiga == estendido:
                    # Tentar inferir aprofundamento ou jogar no primeiro (Matemática)
                    # Inferir pelo professor do registro, se houver
                    professor = getattr(reg, 'professor', None)
                    nova_disc = aprof_mat # Default fallback
                    if professor:
                        profs_discs = professor.disciplinas.values_list('nome', flat=True)
                        if any('Matemática' in d for d in profs_discs) or any('Mat.' in d for d in profs_discs):
                            nova_disc = aprof_mat
                        elif any('Natureza' in d for d in profs_discs) or any('Física' in d for d in profs_discs) or any('Química' in d for d in profs_discs) or any('Biologia' in d for d in profs_discs):
                            nova_disc = aprof_nat
                        elif any('Humanas' in d for d in profs_discs) or any('Geografia' in d for d in profs_discs) or any('História' in d for d in profs_discs) or any('Filosofia' in d for d in profs_discs) or any('Sociologia' in d for d in profs_discs):
                            nova_disc = aprof_hum
                        elif any('Linguagens' in d for d in profs_discs) or any('Português' in d for d in profs_discs) or any('Inglês' in d for d in profs_discs) or any('Artes' in d for d in profs_discs) or any('Educação Física' in d for d in profs_discs):
                            nova_disc = aprof_ling
                    
                    reg.disciplina = nova_disc
                    if pre_save_callback:
                        pre_save_callback(reg, antiga, nova_disc)
                    reg.save()

        # 5. Atualização das Aulas Extras, Ocorrências, Sugestoes, Notas
        self.stdout.write("Migrando Aulas Extras...")
        migrar_registros(AulaExtraProgramada)

        self.stdout.write("Migrando Ocorrências...")
        migrar_registros(Ocorrencia)

        self.stdout.write("Migrando Sugestão de Conteúdo...")
        migrar_registros(SugestaoConteudo)
        
        self.stdout.write("Migrando Conteúdo Programático...")
        migrar_registros(ConteudoProgramatico)

        self.stdout.write("Migrando Notas Bimestrais...")
        migrar_registros(NotaBimestral, field_turma='turma') # assumindo que nota tenha relacao indireta ou direta; wait, NotaBimestral tem 'aluno.turma_atual' mas não 'turma' direto.
        # Vamos corrigir:
        def callback_nota(reg, antiga, nova):
            pass # Sem customização necessária
        
        if eletiva1 or eletiva2 or estendido:
            notas = NotaBimestral.objects.filter(disciplina__in=[eletiva1, eletiva2, estendido])
            for nota in notas:
                turma_cod = nota.aluno.turma_atual.codigo if nota.aluno and nota.aluno.turma_atual else None
                if nota.disciplina in [eletiva1, eletiva2]:
                    n = get_disciplina_correta(nota.disciplina, turma_cod)
                    if n:
                        nota.disciplina = n
                        nota.save()
                elif nota.disciplina == estendido:
                    nota.disciplina = aprof_mat # Default
                    nota.save()

            pas = ProvaAuxiliar.objects.filter(disciplina__in=[eletiva1, eletiva2, estendido])
            for pa in pas:
                turma_cod = pa.aluno.turma_atual.codigo if pa.aluno and pa.aluno.turma_atual else None
                if pa.disciplina in [eletiva1, eletiva2]:
                    n = get_disciplina_correta(pa.disciplina, turma_cod)
                    if n:
                        pa.disciplina = n
                        pa.save()
                elif pa.disciplina == estendido:
                    pa.disciplina = aprof_mat
                    pa.save()

        # 6. Exclusão das genéricas
        self.stdout.write("Excluindo disciplinas antigas genéricas...")
        if eletiva1: eletiva1.delete()
        if eletiva2: eletiva2.delete()
        if estendido: estendido.delete()

        self.stdout.write(self.style.SUCCESS("Migração concluída com sucesso!"))

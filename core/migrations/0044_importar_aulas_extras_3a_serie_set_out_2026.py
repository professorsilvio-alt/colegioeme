# Generated for Aulas Extras / Aprofundamento 3ª série Setembro/Outubro 2026
import datetime
from django.db import migrations

AULAS_EXTRAS_DATA = [
    # 22/09/2026 (ter) - MATEMÁTICA: Soares (Geom)
    {'data': '2026-09-22', 'turma': '31', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Soares'},
    {'data': '2026-09-22', 'turma': '32', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Soares'},

    # 23/09/2026 (qua) - NATUREZA: Wilson (Bio)
    {'data': '2026-09-23', 'turma': '31', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Wilson'},
    {'data': '2026-09-23', 'turma': '32', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Wilson'},

    # 25/09/2026 (sex) - HUMANAS: Vitor (Geo)
    {'data': '2026-09-25', 'turma': '31', 'disciplina': 'Aprofundamento em Ciências Humanas', 'professor': 'Vitor'},
    {'data': '2026-09-25', 'turma': '32', 'disciplina': 'Aprofundamento em Ciências Humanas', 'professor': 'Vitor'},

    # 28/09/2026 (seg) - LINGUAGENS: Luíz Otávio (Port)
    {'data': '2026-09-28', 'turma': '31', 'disciplina': 'Aprofundamento em Linguagens', 'professor': 'Luiz Otávio'},
    {'data': '2026-09-28', 'turma': '32', 'disciplina': 'Aprofundamento em Linguagens', 'professor': 'Luiz Otávio'},

    # 29/09/2026 (ter) - MATEMÁTICA: Soares (Geom) e Silvio (Mat)
    {'data': '2026-09-29', 'turma': '31', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Soares'},
    {'data': '2026-09-29', 'turma': '31', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Silvio'},
    {'data': '2026-09-29', 'turma': '32', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Soares'},
    {'data': '2026-09-29', 'turma': '32', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Silvio'},

    # 30/09/2026 (qua) - NATUREZA: Manoel (Fís) e Vânia (Quí)
    {'data': '2026-09-30', 'turma': '31', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Manoel'},
    {'data': '2026-09-30', 'turma': '31', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Vânia'},
    {'data': '2026-09-30', 'turma': '32', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Manoel'},
    {'data': '2026-09-30', 'turma': '32', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Vânia'},

    # 02/10/2026 (sex) - HUMANAS: Ulisses (His)
    {'data': '2026-10-02', 'turma': '31', 'disciplina': 'Aprofundamento em Ciências Humanas', 'professor': 'Ulisses'},
    {'data': '2026-10-02', 'turma': '32', 'disciplina': 'Aprofundamento em Ciências Humanas', 'professor': 'Ulisses'},

    # 05/10/2026 (seg) - LINGUAGENS: Thereza (Lit)
    {'data': '2026-10-05', 'turma': '31', 'disciplina': 'Aprofundamento em Linguagens', 'professor': 'Thereza'},
    {'data': '2026-10-05', 'turma': '32', 'disciplina': 'Aprofundamento em Linguagens', 'professor': 'Thereza'},

    # 06/10/2026 (ter) - MATEMÁTICA: Soares (Geom) e Silvio (Mat)
    {'data': '2026-10-06', 'turma': '31', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Soares'},
    {'data': '2026-10-06', 'turma': '31', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Silvio'},
    {'data': '2026-10-06', 'turma': '32', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Soares'},
    {'data': '2026-10-06', 'turma': '32', 'disciplina': 'Aprofundamento em Matemática', 'professor': 'Silvio'},

    # 07/10/2026 (qua) - NATUREZA: Wilson (Bio)
    {'data': '2026-10-07', 'turma': '31', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Wilson'},
    {'data': '2026-10-07', 'turma': '32', 'disciplina': 'Aprofundamento em Ciências da Natureza', 'professor': 'Wilson'},

    # 09/10/2026 (sex) - HUMANAS: Vitor (Geo)
    {'data': '2026-10-09', 'turma': '31', 'disciplina': 'Aprofundamento em Ciências Humanas', 'professor': 'Vitor'},
    {'data': '2026-10-09', 'turma': '32', 'disciplina': 'Aprofundamento em Ciências Humanas', 'professor': 'Vitor'},
]

def importar_aulas_extras_3a_serie(apps, schema_editor):
    Turma = apps.get_model('core', 'Turma')
    Disciplina = apps.get_model('core', 'Disciplina')
    Professor = apps.get_model('core', 'Professor')
    AulaExtraProgramada = apps.get_model('core', 'AulaExtraProgramada')

    # 1. Garante disciplinas de Aprofundamento
    disc_mat, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Matemática')
    disc_nat, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Ciências da Natureza')
    disc_hum, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Ciências Humanas')
    disc_ling, _ = Disciplina.objects.get_or_create(nome='Aprofundamento em Linguagens')

    t31 = Turma.objects.filter(codigo='31').first()
    t32 = Turma.objects.filter(codigo='32').first()

    prof_disc_map = {
        'Soares': disc_mat,
        'Silvio': disc_mat,
        'Wilson': disc_nat,
        'Manoel': disc_nat,
        'Vânia': disc_nat,
        'Ulisses': disc_hum,
        'Vitor': disc_hum,
        'Thereza': disc_ling,
        'Luiz Otávio': disc_ling,
    }

    for p_nome, d_obj in prof_disc_map.items():
        prof = Professor.objects.filter(nome__iexact=p_nome).first()
        if prof:
            prof.disciplinas.add(d_obj)
            if t31 and t32:
                prof.turmas.add(t31, t32)

    # 2. Insere registros
    for item in AULAS_EXTRAS_DATA:
        t = Turma.objects.filter(codigo=item['turma']).first()
        d = Disciplina.objects.filter(nome=item['disciplina']).first()
        p = Professor.objects.filter(nome__iexact=item['professor']).first()
        if t and d and p:
            dt = datetime.datetime.strptime(item['data'], '%Y-%m-%d').date()
            AulaExtraProgramada.objects.get_or_create(
                data=dt,
                turma=t,
                disciplina=d,
                professor=p
            )

def rollback(apps, schema_editor):
    AulaExtraProgramada = apps.get_model('core', 'AulaExtraProgramada')
    datas = [
        '2026-09-22', '2026-09-23', '2026-09-25', '2026-09-28',
        '2026-09-29', '2026-09-30', '2026-10-02', '2026-10-05',
        '2026-10-06', '2026-10-07', '2026-10-09'
    ]
    AulaExtraProgramada.objects.filter(turma__codigo__in=['31', '32'], data__in=datas).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0043_aluno_telefone_responsavel'),
    ]

    operations = [
        migrations.RunPython(importar_aulas_extras_3a_serie, rollback),
    ]

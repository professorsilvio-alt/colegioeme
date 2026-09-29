# Generated for Aulas Extras / Eletivas e Projeto de Vida 2ª série 4º Bimestre 2026
import datetime
from django.db import migrations

AULAS_EXTRAS_2A_4BIM_DATA = [
    # 22/09/2026 (ter)
    {'data': '2026-09-22', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Leonardo'},
    {'data': '2026-09-22', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Leonardo'},
    {'data': '2026-09-22', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Leonardo'},
    {'data': '2026-09-22', 'turma': '21', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-09-22', 'turma': '22', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-09-22', 'turma': '23', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-09-22', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-09-22', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-09-22', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-09-22', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-09-22', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-09-22', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'},

    # 29/09/2026 (ter)
    {'data': '2026-09-29', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-09-29', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-09-29', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-09-29', 'turma': '21', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-09-29', 'turma': '22', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-09-29', 'turma': '23', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-09-29', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-09-29', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-09-29', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-09-29', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-09-29', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-09-29', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'},

    # 06/10/2026 (ter)
    {'data': '2026-10-06', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-06', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-06', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-06', 'turma': '21', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-10-06', 'turma': '22', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-10-06', 'turma': '23', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-10-06', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-06', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-06', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-06', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-06', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-06', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'},

    # 13/10/2026 (ter)
    {'data': '2026-10-13', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-13', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-13', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-13', 'turma': '21', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-10-13', 'turma': '22', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-10-13', 'turma': '23', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-10-13', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-13', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-13', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-13', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-13', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-13', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'},

    # 20/10/2026 (ter)
    {'data': '2026-10-20', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-20', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-20', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-20', 'turma': '21', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-10-20', 'turma': '22', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-10-20', 'turma': '23', 'disciplina': 'Múltiplas Linguagens I', 'professor': 'Lorena'},
    {'data': '2026-10-20', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-20', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-20', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-20', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-20', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-20', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'},

    # 27/10/2026 (ter)
    {'data': '2026-10-27', 'turma': '21', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-27', 'turma': '22', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-27', 'turma': '23', 'disciplina': 'Educação Financeira', 'professor': 'Silvio'},
    {'data': '2026-10-27', 'turma': '21', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-10-27', 'turma': '22', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-10-27', 'turma': '23', 'disciplina': 'Múltiplas Linguagens II', 'professor': 'Luiz Otávio'},
    {'data': '2026-10-27', 'turma': '21', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-27', 'turma': '22', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-27', 'turma': '23', 'disciplina': 'Projeto de Vida', 'professor': 'Lorena'},
    {'data': '2026-10-27', 'turma': '21', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-27', 'turma': '22', 'disciplina': 'Artes', 'professor': 'Bruna'},
    {'data': '2026-10-27', 'turma': '23', 'disciplina': 'Artes', 'professor': 'Bruna'},
]

def importar_aulas_extras_2a_serie_4bim(apps, schema_editor):
    Turma = apps.get_model('core', 'Turma')
    Disciplina = apps.get_model('core', 'Disciplina')
    Professor = apps.get_model('core', 'Professor')
    AulaExtraProgramada = apps.get_model('core', 'AulaExtraProgramada')

    turmas_2 = list(Turma.objects.filter(codigo__in=['21', '22', '23']))

    # Garante vinculação de disciplinas e turmas aos professores
    prof_disc_map = {
        'Leonardo': ['Educação Financeira'],
        'Silvio': ['Educação Financeira'],
        'Lorena': ['Projeto de Vida', 'Múltiplas Linguagens I'],
        'Luiz Otávio': ['Múltiplas Linguagens II'],
        'Bruna': ['Artes'],
    }

    for p_nome, d_nomes in prof_disc_map.items():
        prof = Professor.objects.filter(nome__iexact=p_nome).first()
        if prof:
            for dn in d_nomes:
                disc = Disciplina.objects.filter(nome__iexact=dn).first()
                if disc:
                    prof.disciplinas.add(disc)
            if turmas_2:
                prof.turmas.add(*turmas_2)

    # Insere as aulas extras programadas
    for item in AULAS_EXTRAS_2A_4BIM_DATA:
        t = Turma.objects.filter(codigo=item['turma']).first()
        d = Disciplina.objects.filter(nome__iexact=item['disciplina']).first()
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
        '2026-09-22', '2026-09-29', '2026-10-06',
        '2026-10-13', '2026-10-20', '2026-10-27'
    ]
    AulaExtraProgramada.objects.filter(turma__codigo__in=['21', '22', '23'], data__in=datas).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0045_importar_aulas_extras_1a_serie_4o_bimestre_2026'),
    ]

    operations = [
        migrations.RunPython(importar_aulas_extras_2a_serie_4bim, rollback),
    ]

import datetime
from decimal import Decimal
from django.db import migrations


def configurar_eletivas_grupos_pontuacoes(apps, schema_editor):
    GrupoDisciplina = apps.get_model('core', 'GrupoDisciplina')
    Disciplina = apps.get_model('core', 'Disciplina')
    AulaExtraProgramada = apps.get_model('core', 'AulaExtraProgramada')
    Professor = apps.get_model('core', 'Professor')
    PontuacaoSubdisciplina = apps.get_model('core', 'PontuacaoSubdisciplina')
    AnoLetivo = apps.get_model('core', 'AnoLetivo')
    Escola = apps.get_model('core', 'Escola')

    # 1. Criação dos Grupos de Disciplina
    grp_soc, _ = GrupoDisciplina.objects.get_or_create(
        nome_boletim='Sociedade e Cidadania',
        defaults={'ordem_boletim': 8, 'faz_simulado_ef': False}
    )
    grp_sust, _ = GrupoDisciplina.objects.get_or_create(
        nome_boletim='Sustentabilidade e Meio Ambiente',
        defaults={'ordem_boletim': 9, 'faz_simulado_ef': False}
    )
    grp_mult, _ = GrupoDisciplina.objects.get_or_create(
        nome_boletim='Múltiplas Linguagens',
        defaults={'ordem_boletim': 10, 'faz_simulado_ef': False}
    )

    # 2. Criação das Subdisciplinas
    # Sociedade e Cidadania
    disc_soc_1, _ = Disciplina.objects.get_or_create(
        nome='Sociedade e Cidadania I',
        defaults={'grupo': grp_soc, 'faz_simulado_ef': False}
    )
    disc_soc_1.grupo = grp_soc
    disc_soc_1.save()

    disc_soc_2, _ = Disciplina.objects.get_or_create(
        nome='Sociedade e Cidadania II',
        defaults={'grupo': grp_soc, 'faz_simulado_ef': False}
    )
    disc_soc_2.grupo = grp_soc
    disc_soc_2.save()

    # Sustentabilidade e Meio Ambiente
    disc_sust_1, _ = Disciplina.objects.get_or_create(
        nome='Sustentabilidade e Meio Ambiente I',
        defaults={'grupo': grp_sust, 'faz_simulado_ef': False}
    )
    disc_sust_1.grupo = grp_sust
    disc_sust_1.save()

    disc_sust_2, _ = Disciplina.objects.get_or_create(
        nome='Sustentabilidade e Meio Ambiente II',
        defaults={'grupo': grp_sust, 'faz_simulado_ef': False}
    )
    disc_sust_2.grupo = grp_sust
    disc_sust_2.save()

    # Múltiplas Linguagens
    disc_mult_1, _ = Disciplina.objects.get_or_create(
        nome='Múltiplas Linguagens I',
        defaults={'grupo': grp_mult, 'faz_simulado_ef': False}
    )
    disc_mult_1.grupo = grp_mult
    disc_mult_1.save()

    disc_mult_2, _ = Disciplina.objects.get_or_create(
        nome='Múltiplas Linguagens II',
        defaults={'grupo': grp_mult, 'faz_simulado_ef': False}
    )
    disc_mult_2.grupo = grp_mult
    disc_mult_2.save()

    # 3. Mapear e migrar registros de AulaExtraProgramada
    # Sociedade e Cidadania antiga -> I (Varanda) ou II (Gustavo)
    old_soc = Disciplina.objects.filter(nome='Sociedade e Cidadania').first()
    if old_soc and old_soc.pk not in (disc_soc_1.pk, disc_soc_2.pk):
        for ae in AulaExtraProgramada.objects.filter(disciplina=old_soc):
            if ae.professor and 'varanda' in ae.professor.nome.lower():
                ae.disciplina = disc_soc_1
            else:
                ae.disciplina = disc_soc_2
            ae.save()

    # Sustentabilidade e Meio Ambiente antiga -> I (Diniz) ou II (Fernanda)
    old_sust = Disciplina.objects.filter(nome='Sustentabilidade e Meio Ambiente').first()
    if old_sust and old_sust.pk not in (disc_sust_1.pk, disc_sust_2.pk):
        for ae in AulaExtraProgramada.objects.filter(disciplina=old_sust):
            if ae.professor and 'diniz' in ae.professor.nome.lower():
                ae.disciplina = disc_sust_1
            else:
                ae.disciplina = disc_sust_2
            ae.save()

    # Múltiplas Linguagens antiga -> I (Lorena) ou II (Luiz Otávio)
    old_mult = Disciplina.objects.filter(nome='Múltiplas Linguagens').first()
    if old_mult and old_mult.pk not in (disc_mult_1.pk, disc_mult_2.pk):
        for ae in AulaExtraProgramada.objects.filter(disciplina=old_mult):
            if ae.professor and ('luiz' in ae.professor.nome.lower() or 'otávio' in ae.professor.nome.lower() or 'otavio' in ae.professor.nome.lower()):
                ae.disciplina = disc_mult_2
            else:
                ae.disciplina = disc_mult_1
            ae.save()

    # 4. Vincular subdisciplinas aos professores
    p_varanda = Professor.objects.filter(nome__icontains='Varanda').first()
    p_gustavo = Professor.objects.filter(nome__icontains='Gustavo').first()
    p_diniz = Professor.objects.filter(nome__icontains='Diniz').first()
    p_fernanda = Professor.objects.filter(nome__icontains='Fernanda').first()
    p_lorena = Professor.objects.filter(nome__icontains='Lorena').first()
    p_luiz = Professor.objects.filter(nome__icontains='Luiz').first()
    p_leonardo = Professor.objects.filter(nome__icontains='Leonardo').first()
    p_silvio = Professor.objects.filter(nome__icontains='Silvio').first()

    if p_varanda:
        p_varanda.disciplinas.add(disc_soc_1)
        p_varanda.autorizado_lancar_notas = True
        p_varanda.save()
    if p_gustavo:
        p_gustavo.disciplinas.add(disc_soc_2)
        p_gustavo.autorizado_lancar_notas = True
        p_gustavo.save()
    if p_diniz:
        p_diniz.disciplinas.add(disc_sust_1)
        p_diniz.autorizado_lancar_notas = True
        p_diniz.save()
    if p_fernanda:
        p_fernanda.disciplinas.add(disc_sust_2)
        p_fernanda.autorizado_lancar_notas = True
        p_fernanda.save()
    if p_lorena:
        p_lorena.disciplinas.add(disc_mult_1)
        p_lorena.autorizado_lancar_notas = True
        p_lorena.save()
    if p_luiz:
        p_luiz.disciplinas.add(disc_mult_2)
        p_luiz.autorizado_lancar_notas = True
        p_luiz.save()
    if p_leonardo:
        p_leonardo.autorizado_lancar_notas = True
        p_leonardo.save()
    if p_silvio:
        p_silvio.autorizado_lancar_notas = True
        p_silvio.save()

    # Liberar todos os professores docentes
    for p in Professor.objects.filter(cargo='PROFESSOR'):
        p.autorizado_lancar_notas = True
        p.save()

    # 5. Criar pontuações padrão (5.00 cada para subdisciplinas)
    ano_2026 = AnoLetivo.objects.filter(ano=2026).first() or AnoLetivo.objects.first()
    escola = Escola.objects.first()

    if ano_2026:
        # 1ª Série
        PontuacaoSubdisciplina.objects.update_or_create(
            ano_letivo=ano_2026, escola=escola, serie='1', disciplina=disc_soc_1,
            defaults={'pontuacao_maxima': Decimal('5.00')}
        )
        PontuacaoSubdisciplina.objects.update_or_create(
            ano_letivo=ano_2026, escola=escola, serie='1', disciplina=disc_soc_2,
            defaults={'pontuacao_maxima': Decimal('5.00')}
        )
        PontuacaoSubdisciplina.objects.update_or_create(
            ano_letivo=ano_2026, escola=escola, serie='1', disciplina=disc_sust_1,
            defaults={'pontuacao_maxima': Decimal('5.00')}
        )
        PontuacaoSubdisciplina.objects.update_or_create(
            ano_letivo=ano_2026, escola=escola, serie='1', disciplina=disc_sust_2,
            defaults={'pontuacao_maxima': Decimal('5.00')}
        )

        # 2ª Série
        PontuacaoSubdisciplina.objects.update_or_create(
            ano_letivo=ano_2026, escola=escola, serie='2', disciplina=disc_mult_1,
            defaults={'pontuacao_maxima': Decimal('5.00')}
        )
        PontuacaoSubdisciplina.objects.update_or_create(
            ano_letivo=ano_2026, escola=escola, serie='2', disciplina=disc_mult_2,
            defaults={'pontuacao_maxima': Decimal('5.00')}
        )


def rollback(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0040_importar_aulas_extras_1a_serie_3o_bimestre_2026'),
    ]
    operations = [
        migrations.RunPython(configurar_eletivas_grupos_pontuacoes, rollback),
    ]

from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from ..models import (
    Aluno, Disciplina, GrupoDisciplina, NotaBimestral,
    ProvaAuxiliar, RecuperacaoFinal, ConselhoClasse
)


def round_2(val):
    """Arredonda Decimal ou float para 2 casas decimais usando ROUND_HALF_UP."""
    if val is None:
        return None
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    return val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_notas_disciplina(aluno_pk, disc_pk, notas_map, pas_map, recs_map, conselho_map):
    """
    Calcula os resultados (B1..B4, PA1, PA2, Media Anual, REC, Media Final, Situação)
    para um aluno em uma disciplina específica.
    """
    pa1_val = pas_map.get((aluno_pk, disc_pk, 1))
    pa2_val = pas_map.get((aluno_pk, disc_pk, 2))
    rec_val = recs_map.get((aluno_pk, disc_pk))
    conselho_obj = conselho_map.get((aluno_pk, disc_pk))

    # 1. Obter notas brutas dos bimestres
    raw_bims = {}
    na_flags = {}
    for b in (1, 2, 3, 4):
        nota_obj = notas_map.get((aluno_pk, disc_pk, b))
        if nota_obj is not None:
            raw_bims[b] = nota_obj.nota_final
            na_flags[b] = nota_obj.nao_avaliado
        else:
            raw_bims[b] = None
            na_flags[b] = False

    # 2. Resolução de B1 e B2 com PA1 e N/A
    b1_info = {'valor': None, 'substituido_por_pa': False, 'is_na': False}
    b2_info = {'valor': None, 'substituido_por_pa': False, 'is_na': False}

    for b, info in [(1, b1_info), (2, b2_info)]:
        if raw_bims[b] is not None or na_flags[b]:
            if na_flags[b]:
                if pa1_val is not None:
                    info['valor'] = round_2(pa1_val)
                    info['substituido_por_pa'] = True
                else:
                    # Falta sem PA realizada -> vira zero
                    info['valor'] = Decimal('0.00')
                    info['is_na'] = True
            else:
                nota_base = raw_bims[b]
                if pa1_val is not None:
                    media_pa1 = round_2((nota_base + pa1_val) / Decimal('2'))
                    if media_pa1 > nota_base:
                        info['valor'] = media_pa1
                        info['substituido_por_pa'] = True
                    else:
                        info['valor'] = round_2(nota_base)
                else:
                    info['valor'] = round_2(nota_base)

    # 3. Resolução inicial de B3 e B4 (apenas com tratamento de N/A)
    b3_info = {'valor': None, 'substituido_por_pa': False, 'is_na': False}
    b4_info = {'valor': None, 'substituido_por_pa': False, 'is_na': False}

    for b, info in [(3, b3_info), (4, b4_info)]:
        if raw_bims[b] is not None or na_flags[b]:
            if na_flags[b]:
                if pa2_val is not None:
                    info['valor'] = round_2(pa2_val)
                    info['substituido_por_pa'] = True
                else:
                    info['valor'] = Decimal('0.00')
                    info['is_na'] = True
            else:
                info['valor'] = round_2(raw_bims[b])

    # 4. Avaliar critério da PA2 para recuperação (Somatório < 20 pontos)
    # Somatório provisório dos 4 bimestres
    vals_provisorios = [b1_info['valor'], b2_info['valor'], b3_info['valor'], b4_info['valor']]
    vals_validos_prov = [v for v in vals_provisorios if v is not None]

    if len(vals_validos_prov) == 4:
        soma_pontos = sum(vals_validos_prov)
    elif len(vals_validos_prov) > 0:
        # Se ainda não temos todos os 4 bimestres mas tem 3º/4º lançado
        soma_pontos = sum(vals_validos_prov) * Decimal(str(4 / len(vals_validos_prov)))
    else:
        soma_pontos = None

    # Se somatório < 20.0 (média < 5.0) e tem PA2 lançada, aplica recuperação na P3 e/ou P4
    if soma_pontos is not None and soma_pontos < Decimal('20.00') and pa2_val is not None:
        for b, info in [(3, b3_info), (4, b4_info)]:
            if not na_flags[b] and raw_bims[b] is not None:
                nota_base = raw_bims[b]
                media_pa2 = round_2((nota_base + pa2_val) / Decimal('2'))
                if media_pa2 > nota_base:
                    info['valor'] = media_pa2
                    info['substituido_por_pa'] = True

    # 5. Média Anual
    b_vals = [b1_info['valor'], b2_info['valor'], b3_info['valor'], b4_info['valor']]
    b_validos = [v for v in b_vals if v is not None]

    if b_validos:
        media_anual = round_2(sum(b_validos) / Decimal(str(len(b_validos))))
    else:
        media_anual = None

    # 6. Recuperação Final e Conselho de Classe
    rec_nota = round_2(rec_val) if rec_val is not None else None
    media_final = None
    situacao = 'Pendente'
    promovido_conselho = False

    if media_anual is not None:
        if media_anual >= Decimal('5.00'):
            media_final = media_anual
            situacao = 'Aprovado'
        else:
            # Média anual < 5.0 -> Precisa de REC ou Conselho
            if rec_nota is not None and rec_nota >= Decimal('5.00'):
                # Aprovado na Recuperação: média final fixada em 5.00
                media_final = Decimal('5.00')
                situacao = 'Aprovado na REC'
            else:
                # Não atingiu na REC ou não fez -> Conselho de Classe
                if conselho_obj and conselho_obj.promovido:
                    media_final = Decimal('5.00')
                    situacao = 'Aprovado pelo Conselho'
                    promovido_conselho = True
                else:
                    if rec_nota is not None:
                        media_final = media_anual
                        situacao = 'Reprovado'
                    else:
                        media_final = media_anual
                        situacao = 'Em Recuperação'

    return {
        'b1': b1_info,
        'b2': b2_info,
        'pa1': {'valor': round_2(pa1_val)},
        'b3': b3_info,
        'b4': b4_info,
        'pa2': {'valor': round_2(pa2_val)},
        'media_anual': media_anual,
        'rec_final': {'valor': rec_nota},
        'media_final': media_final,
        'situacao': situacao,
        'promovido_conselho': promovido_conselho,
        'conselho_obs': conselho_obj.observacao if conselho_obj else '',
    }


def carregar_dados_boletim_aluno(aluno, ano_letivo):
    """
    Monta a estrutura de notas do aluno agrupada por grupos curriculares e avulsas.
    """
    notas_qs = NotaBimestral.objects.filter(
        aluno=aluno, ano_letivo=ano_letivo
    ).select_related('disciplina', 'disciplina__grupo')

    pas_qs = ProvaAuxiliar.objects.filter(
        aluno=aluno, ano_letivo=ano_letivo
    )
    recs_qs = RecuperacaoFinal.objects.filter(
        aluno=aluno, ano_letivo=ano_letivo
    )
    conselho_qs = ConselhoClasse.objects.filter(
        aluno=aluno, ano_letivo=ano_letivo
    )

    notas_map = {(n.aluno_id, n.disciplina_id, n.bimestre): n for n in notas_qs}
    pas_map = {(p.aluno_id, p.disciplina_id, p.numero_pa): p.nota for p in pas_qs}
    recs_map = {(r.aluno_id, r.disciplina_id): r.nota for r in recs_qs}
    conselho_map = {(c.aluno_id, c.disciplina_id): c for c in conselho_qs}

    disc_ids_com_nota = set(n.disciplina_id for n in notas_qs) | \
                        set(p.disciplina_id for p in pas_qs) | \
                        set(r.disciplina_id for r in recs_qs) | \
                        set(c.disciplina_id for c in conselho_qs)

    grupos_no_boletim = []

    # 1. Grupos
    grupos = GrupoDisciplina.objects.prefetch_related('disciplinas').order_by('ordem_boletim')
    for grupo in grupos:
        discs_grupo = [d for d in grupo.disciplinas.all() if d.pk in disc_ids_com_nota]
        if not discs_grupo:
            continue

        res_discs = [calcular_notas_disciplina(aluno.pk, d.pk, notas_map, pas_map, recs_map, conselho_map) for d in discs_grupo]

        linha_grupo = {
            'nome': grupo.nome_boletim,
            'is_grupo': True,
            'disciplina_pk': None,
        }
        for b_key, b_num in [('b1', 1), ('b2', 2), ('b3', 3), ('b4', 4)]:
            notas_b = [notas_map.get((aluno.pk, d.pk, b_num)) for d in discs_grupo]
            notas_validas = [n for n in notas_b if n is not None]

            if not notas_validas:
                linha_grupo[b_key] = {'valor': None, 'substituido_por_pa': False, 'is_na': False}
                continue

            all_na = all(n.nao_avaliado for n in notas_validas) and len(notas_validas) == len(discs_grupo)

            vals_subdiscs = []
            teve_pa = False
            for d in discs_grupo:
                r_disc = next((r for r, disc_obj in zip(res_discs, discs_grupo) if disc_obj.pk == d.pk), None)
                if r_disc and r_disc[b_key]['valor'] is not None:
                    vals_subdiscs.append(r_disc[b_key]['valor'])
                    if r_disc[b_key]['substituido_por_pa']:
                        teve_pa = True

            if all_na:
                soma_grupo = Decimal('0.00')
            elif vals_subdiscs:
                soma_grupo = sum(vals_subdiscs)
            else:
                soma_grupo = None

            # Aplicação do simulado sobre a nota fechada do grupo
            if soma_grupo is not None and not all_na:
                simulados = [n.nota_simulado for n in notas_validas if n.nota_simulado is not None]
                if simulados:
                    max_sim = max(simulados)
                    bonus = float(max_sim) * 0.01
                    calc_sim = soma_grupo * Decimal(str(round(1 + bonus, 4)))
                    soma_grupo = min(Decimal('10.00'), round_2(calc_sim))
                else:
                    soma_grupo = min(Decimal('10.00'), round_2(soma_grupo))

            linha_grupo[b_key] = {
                'valor': soma_grupo,
                'substituido_por_pa': teve_pa,
                'is_na': all_na,
            }

        for pa_key in ('pa1', 'pa2'):
            vals_pa = [r[pa_key]['valor'] for r in res_discs if r[pa_key]['valor'] is not None]
            linha_grupo[pa_key] = {
                'valor': round_2(sum(vals_pa)) if vals_pa else None
            }

        vals_rec = [r['rec_final']['valor'] for r in res_discs if r['rec_final']['valor'] is not None]
        linha_grupo['rec_final'] = {
            'valor': round_2(sum(vals_rec)) if vals_rec else None
        }

        b_vals_grp = [linha_grupo[f'b{b}']['valor'] for b in (1, 2, 3, 4) if linha_grupo[f'b{b}']['valor'] is not None]
        if b_vals_grp:
            media_anual_grp = round_2(sum(b_vals_grp) / Decimal(str(len(b_vals_grp))))
        else:
            media_anual_grp = None
        linha_grupo['media_anual'] = media_anual_grp

        if media_anual_grp is not None:
            if media_anual_grp >= Decimal('5.00'):
                linha_grupo['media_final'] = media_anual_grp
                linha_grupo['situacao'] = 'Aprovado'
                linha_grupo['promovido_conselho'] = False
            else:
                if linha_grupo['rec_final']['valor'] is not None and linha_grupo['rec_final']['valor'] >= Decimal('5.00'):
                    linha_grupo['media_final'] = Decimal('5.00')
                    linha_grupo['situacao'] = 'Aprovado na REC'
                    linha_grupo['promovido_conselho'] = False
                elif any(r['promovido_conselho'] for r in res_discs):
                    linha_grupo['media_final'] = Decimal('5.00')
                    linha_grupo['situacao'] = 'Aprovado pelo Conselho'
                    linha_grupo['promovido_conselho'] = True
                else:
                    linha_grupo['media_final'] = media_anual_grp
                    linha_grupo['situacao'] = 'Reprovado' if linha_grupo['rec_final']['valor'] is not None else 'Em Recuperação'
                    linha_grupo['promovido_conselho'] = False
        else:
            linha_grupo['media_final'] = None
            linha_grupo['situacao'] = 'Pendente'
            linha_grupo['promovido_conselho'] = False

        grupos_no_boletim.append(linha_grupo)

    # 2. Standalone
    discs_standalone = Disciplina.objects.filter(
        pk__in=disc_ids_com_nota, grupo__isnull=True
    ).order_by('nome')
    for disc in discs_standalone:
        res = calcular_notas_disciplina(aluno.pk, disc.pk, notas_map, pas_map, recs_map, conselho_map)
        res['nome'] = disc.nome
        res['is_grupo'] = False
        res['disciplina_pk'] = disc.pk
        grupos_no_boletim.append(res)

    return grupos_no_boletim

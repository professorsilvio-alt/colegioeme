import csv
import datetime
import io
import logging
import sys
import os
from datetime import date
from collections import defaultdict
from functools import partial

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.staticfiles import finders
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from ..models import (Aluno, AnoLetivo, ConteudoProgramatico, Disciplina,
                     Escola, GradeHoraria, Ocorrencia, Professor,
                     SugestaoConteudo, Turma, Configuracao, NotaBimestral,
                     ProvaAuxiliar, GrupoDisciplina)
from ..utils import get_professor, get_feriados, get_client_ip, ordenar_por_nome
from .ocorrencias import ocorrencias_do_usuario

# Logger para auditoria de ações sensíveis
logger = logging.getLogger('core')



# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────

def _verificar_recaptcha(token):
    """Verifica o token reCAPTCHA v3 com os servidores do Google. Retorna True se válido."""
    if settings.DEBUG or getattr(settings, 'BYPASS_RECAPTCHA', False):
        return True
    import urllib.request
    import urllib.parse
    import json
    secret = settings.RECAPTCHA_SECRET_KEY
    if not secret:
        # Chave não configurada no servidor — bloqueia por segurança
        logger.warning('reCAPTCHA: RECAPTCHA_SECRET_KEY não configurada. Bloqueando requisição.')
        return False
    if not token:
        # Token ausente — usuário não completou o reCAPTCHA
        logger.warning('reCAPTCHA: token ausente na requisição. Bloqueando.')
        return False
    data = urllib.parse.urlencode({
        'secret': secret,
        'response': token,
    }).encode()
    try:
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify', 
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
        logger.debug('RECAPTCHA verify: token_prefix=%s result=%s', str(token)[:30], result)
        return result.get('success', False)
    except Exception as e:
        # Em caso de falha de rede, registra o erro e BLOQUEIA por segurança
        logger.warning('reCAPTCHA: falha na verificação (%s). Bloqueando requisição.', e)


def conteudos_do_usuario(request):
    user = request.user
    prof = get_professor(user)
    ano_letivo = request.ano_letivo
    escola = request.escola
    qs = ConteudoProgramatico.objects.select_related('professor', 'disciplina').prefetch_related('turmas')
    
    if escola:
        qs = qs.filter(turmas__escola=escola)
    if ano_letivo:
        qs = qs.filter(turmas__ano_letivo=ano_letivo).distinct()
        
    if prof and not prof.pode_ver_tudo:
        qs = qs.filter(professor=prof)
    return qs


def filtrar_ocorrencias(request, qs):
    filtro_turma = request.GET.get('filtro_turma', '')
    filtro_status = request.GET.get('filtro_status', '')
    filtro_professor = request.GET.get('filtro_professor', '')
    filtro_aluno = request.GET.get('filtro_aluno', '').strip()
    filtro_data_ini = request.GET.get('data_ini', '')
    filtro_data_fim = request.GET.get('data_fim', '')

    resumo = []
    if filtro_turma:
        qs = qs.filter(turma__codigo=filtro_turma)
        resumo.append(f"Turma: {filtro_turma}")
    if filtro_status:
        qs = qs.filter(status=filtro_status)
        resumo.append(f"Status: {filtro_status}")
    if filtro_professor:
        p = get_object_or_404(Professor, pk=filtro_professor)
        qs = qs.filter(professor=p)
        resumo.append(f"Professor: {p.nome}")
    if filtro_aluno:
        qs = qs.filter(alunos__nome__icontains=filtro_aluno)
        resumo.append(f"Aluno: {filtro_aluno}")
    if filtro_data_ini:
        qs = qs.filter(data__gte=filtro_data_ini)
        resumo.append(f"Início: {filtro_data_ini}")
    if filtro_data_fim:
        qs = qs.filter(data__lte=filtro_data_fim)
        resumo.append(f"Fim: {filtro_data_fim}")

    return qs.distinct(), " | ".join(resumo)


def filtrar_conteudos(request, qs, override_prof=None):
    filtro_turma_c = request.GET.get('filtro_turma_c', '')
    filtro_disc_c = request.GET.get('filtro_disc_c', '')
    filtro_prof_c = override_prof or request.GET.get('filtro_prof_c', '')
    filtro_data_ini = request.GET.get('data_ini', '')
    filtro_data_fim = request.GET.get('data_fim', '')

    resumo = []
    if filtro_turma_c:
        qs = qs.filter(turmas__codigo=filtro_turma_c)
        resumo.append(f"Turma: {filtro_turma_c}")
    if filtro_disc_c:
        d = get_object_or_404(Disciplina, pk=filtro_disc_c)
        qs = qs.filter(disciplina=d)
        resumo.append(f"Disc: {d.nome}")
    if filtro_prof_c:
        p = get_object_or_404(Professor, pk=filtro_prof_c)
        qs = qs.filter(professor=p)
        resumo.append(f"Prof: {p.nome}")
    if filtro_data_ini:
        qs = qs.filter(data__gte=filtro_data_ini)
        resumo.append(f"Início: {filtro_data_ini}")
    if filtro_data_fim:
        qs = qs.filter(data__lte=filtro_data_fim)
        resumo.append(f"Fim: {filtro_data_fim}")

    return qs, " | ".join(resumo)

def calcular_stats_conteudo(prof, data_ini=None, data_fim=None, feriados=None, ano_letivo=None, escola=None):
    """
    Retorna estatísticas de total/preenchidos/faltam.
    Otimizado para evitar o problema N+1 queries.
    """
    if feriados is None:
        feriados = get_feriados(ano_letivo=ano_letivo, escola=escola)

    from django.db.models import Q
    import datetime

    CARGOS_GLOBAIS = ['ADMIN', 'DIRETOR', 'SECRETARIA', 'COORDENADOR', 'AUX_COORD', 'ORIENTADOR']
    hoje = datetime.date.today()
    
    # Datas do período letivo
    config = Configuracao.objects.filter(ano_letivo=ano_letivo, escola=escola).first()
    if config:
        config_ini = config.inicio_periodo_letivo
        config_fim = config.fim_periodo_letivo
    else:
        ano = ano_letivo.ano if ano_letivo else hoje.year
        config_ini = datetime.date(ano, 1, 1)
        config_fim = datetime.date(ano, 12, 20)

    # Filtros de data
    inicio = config_ini
    if data_ini:
        try:
            inicio_prov = datetime.datetime.strptime(data_ini, '%Y-%m-%d').date() if isinstance(data_ini, str) else data_ini
            inicio = max(inicio, inicio_prov)
        except (ValueError, TypeError): pass

    fim = config_fim
    if data_fim:
        try:
            fim_prov = datetime.datetime.strptime(data_fim, '%Y-%m-%d').date() if isinstance(data_fim, str) else data_fim
            fim = min(fim, fim_prov)
        except (ValueError, TypeError): pass

    # Escopo: global ou por professor
    global_view = (not prof) or (prof.cargo in CARGOS_GLOBAIS)
    
    # 1. Busca todas as grades relevantes de uma vez
    gh_qs = GradeHoraria.objects.select_related('turma', 'professor')
    if ano_letivo:
        gh_qs = gh_qs.filter(turma__ano_letivo=ano_letivo)
    if escola:
        gh_qs = gh_qs.filter(turma__escola=escola)
    if not global_view:
        gh_qs = gh_qs.filter(professor=prof)
    
    grades = list(gh_qs)
    if not grades:
        return {
            'total_conteudo': 0, 'preenchidos': 0, 'faltam': 0,
            'total_ate_hoje': 0, 'preenchidos_ate_hoje': 0, 'faltam_ate_hoje': 0
        }

    # Agrupa dias da semana por tríade (prof, turma, disc) em memória.
    # Usa set de weekdays (não contagem): garante que múltiplos horários no mesmo
    # dia da semana não inflam o total — igual à lógica do relatório de pendências.
    DIA_TO_WEEKDAY = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
    slots_map = defaultdict(set)  # key -> set of weekdays com aula

    for g in grades:
        key = (g.professor_id, g.turma.codigo, g.disciplina_id)
        if g.dia_semana in DIA_TO_WEEKDAY:
            slots_map[key].add(DIA_TO_WEEKDAY[g.dia_semana])

    # 2. Busca todos os conteúdos lançados no período de uma vez
    cp_qs = ConteudoProgramatico.objects.filter(data__gte=inicio, data__lte=fim).prefetch_related('turmas')
    if ano_letivo:
        cp_qs = cp_qs.filter(turmas__ano_letivo=ano_letivo)
    if escola:
        cp_qs = cp_qs.filter(turmas__escola=escola)
    if not global_view:
        cp_qs = cp_qs.filter(professor=prof)
    
    # Mapeia lançamentos existentes: (prof_id, turma_cod, disc_id) -> set of dates
    lancados_map = defaultdict(set)
    extras_adicionais = 0
    extras_adicionais_ate_hoje = 0
    
    disciplinas_peso_2 = [
        'Eletiva 1', 'Eletiva 2', 'Estendido', # Nomes legados
        'Sociedade e Cidadania', 'Sustentabilidade e Meio Ambiente',
        'Educação Financeira', 'Múltiplas Linguagens',
        'Aprofundamento em Matemática', 'Aprofundamento em Ciências da Natureza', 
        'Aprofundamento em Ciências Humanas', 'Aprofundamento em Linguagens'
    ]

    for cp in cp_qs:
        for t in cp.turmas.all():
            key = (cp.professor_id, t.codigo, cp.disciplina_id)
            if key in slots_map: # Só conta se estiver na grade
                lancados_map[key].add(cp.data)
            elif cp.disciplina and cp.disciplina.nome in disciplinas_peso_2:
                # Aula extra fora da grade com peso 2
                extras_adicionais += 2
                if cp.data <= hoje:
                    extras_adicionais_ate_hoje += 2

    # 3. Processa cálculos em Python
    total = extras_adicionais
    total_ate_hoje = extras_adicionais_ate_hoje
    preenchidos = extras_adicionais
    preenchidos_ate_hoje = extras_adicionais_ate_hoje

    for key, weekdays in slots_map.items():
        # Cálculo de esperado (Total): 1 por data de aula no período
        cur = inicio
        while cur <= fim:
            if cur.weekday() in weekdays and cur not in feriados:
                total += 1
                if cur <= hoje:
                    total_ate_hoje += 1
            cur += datetime.timedelta(days=1)

        # Cálculo de realizado (Preenchidos): 1 por data efetivamente lançada
        dates_lancadas = lancados_map.get(key, set())
        for d in dates_lancadas:
            if d.weekday() in weekdays and d not in feriados:
                preenchidos += 1
                if d <= hoje:
                    preenchidos_ate_hoje += 1

    return {
        'total_conteudo': total,
        'preenchidos': preenchidos,
        'faltam': max(0, total - preenchidos),
        'total_ate_hoje': total_ate_hoje,
        'preenchidos_ate_hoje': preenchidos_ate_hoje,
        'faltam_ate_hoje': max(0, total_ate_hoje - preenchidos_ate_hoje)
    }

@login_required
def exportar_ocorrencias_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="ocorrencias.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Data', 'Turma', 'Alunos', 'Professor', 'Disciplina', 'Descrição', 'Status'])
    
    qs, _ = filtrar_ocorrencias(request, ocorrencias_do_usuario(request))
    for oc in qs:
        writer.writerow([
            f'OC-{oc.pk:04d}',
            oc.data.strftime('%d/%m/%Y') if oc.data else '',
            oc.turma.codigo if oc.turma else '',
            oc.alunos_str(),
            oc.professor.nome if oc.professor else '',
            oc.disciplina.nome if oc.disciplina else '',
            oc.descricao,
            oc.status,
        ])
    return response


@login_required
def exportar_conteudos_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="conteudos.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Data', 'Turmas', 'Professor', 'Disciplina', 'Descrição'])
    
    qs, _ = filtrar_conteudos(request, conteudos_do_usuario(request))
    for c in qs:
        writer.writerow([
            c.data.strftime('%d/%m/%Y') if c.data else '',
            c.turmas_str(),
            c.professor.nome if c.professor else '',
            c.disciplina.nome if c.disciplina else '',
            c.descricao,
        ])
    return response


# ──────────────────────────────────────────────
# EXPORTAR PDF
# ──────────────────────────────────────────────

def _pdf_response(buf, filename):
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)


class EllipticalImage(Image):
    """Custom Image class to apply elliptical clipping and border (matches web logo)."""
    def draw(self):
        # Save state to apply clipping
        self.canv.saveState()
        w, h = self.drawWidth, self.drawHeight

        # Create elliptical clip path
        path = self.canv.beginPath()
        # center_x, center_y, width, height (actually it's x1, y1, x2, y2)
        # But reportlab's path.ellipse(x1, y1, width, height)
        path.ellipse(0, 0, w, h)
        self.canv.clipPath(path, stroke=0)

        # Draw background color (matching the web dashboard)
        self.canv.setFillColor(colors.HexColor('#003366'))
        self.canv.rect(0, 0, w, h, fill=1, stroke=0)

        # Draw the image (it will be clipped)
        super().draw()
        
        # Restore to remove clipping
        self.canv.restoreState()

        # Draw the white elliptical border
        self.canv.saveState()
        self.canv.setStrokeColor(colors.white)
        self.canv.setLineWidth(2)
        self.canv.ellipse(0, 0, w, h)
        self.canv.restoreState()


def _get_logo_path(mode='eme'):
    """Retorna o caminho absoluto para a logo usando finders do Django."""
    if mode == 'capelum':
        search_paths = [
            'core/capelum_logo_transparent.png',
            'core/capelum_logo.png',
        ]
    else:
        # EME / Escola
        search_paths = [
            'core/logo.jpg',
            'core/logo.png',
            'core/img/logo.png',
        ]
    
    for relative_path in search_paths:
        abs_path = finders.find(relative_path)
        if abs_path:
            return abs_path
            
    # Fallback search if mode fails
    if mode == 'capelum':
        return _get_logo_path(mode='eme')
    return None


def _get_logo_element():
    """Helper to return the standardized elliptical logo for PDFs (cabeçalho - EME)."""
    logo_path = _get_logo_path(mode='eme')
    if logo_path:
        # 4cm x 2cm maintains the 2:1 ratio used in the web dashboard (200x100px)
        logo = EllipticalImage(logo_path, width=4*cm, height=2*cm)
        logo.hAlign = 'LEFT'
        return logo
    return None

def _get_saas_table_style():
    """Retorna o TableStyle no formato SaaS Premium."""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),             
        ('FONTSIZE', (0, 0), (-1, 0), 9),                            
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),                       
        ('TOPPADDING', (0, 0), (-1, 0), 8),                          
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),                           
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')), 
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),                      
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]), 
    ])

def _get_saas_title_style(base_styles):
    """Retorna o estilo do título principal no formato SaaS Premium."""
    return ParagraphStyle(
        'SaaSTitle', 
        parent=base_styles['Title'], 
        fontName='Helvetica-Bold', 
        fontSize=14, 
        textColor=colors.HexColor('#003366'), 
        spaceAfter=12,
        alignment=1 # Center
    )


@login_required
def exportar_ocorrencias_pdf(request):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    title_style = _get_saas_title_style(styles)
    small = ParagraphStyle('small', fontSize=7, leading=9, textColor=colors.HexColor('#374151'))
    filter_style = ParagraphStyle('filters', fontSize=9, italic=True, textColor=colors.HexColor('#6B7280'))
    cell_normal = ParagraphStyle('cell_normal', fontSize=8, leading=10, textColor=colors.HexColor('#374151'))
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    elems.append(Paragraph('Ocorrências - SCA - Sistema de Controle Acadêmico', title_style))
    
    qs, resumo_filtros = filtrar_ocorrencias(request, ocorrencias_do_usuario(request))
    if resumo_filtros:
        elems.append(Paragraph(f"Filtros aplicados: {resumo_filtros}", filter_style))
    
    elems.append(Spacer(1, 0.3*cm))
    data = [['ID', 'Data', 'Turma', 'Alunos', 'Professor', 'Disciplina', 'Status']]
    for oc in qs:
        data.append([
            f'OC-{oc.pk:04d}',
            oc.data.strftime('%d/%m/%Y') if oc.data else '',
            oc.turma.codigo if oc.turma else '',
            Paragraph(oc.alunos_str(), small),
            oc.professor.nome if oc.professor else '',
            Paragraph(oc.disciplina.nome if oc.disciplina else '', cell_normal),
            oc.status,
        ])
    # Total width with 1.0cm margins on A4 (21cm) is 19cm.
    # 1.8+2.0+1.4+5.0+4.0+2.8+2.0 = 19.0cm (Perfect Fill)
    t = Table(data, colWidths=[1.8*cm, 2.0*cm, 1.4*cm, 5.0*cm, 4.0*cm, 2.8*cm, 2.0*cm], repeatRows=1)
    t.setStyle(_get_saas_table_style())
    elems.append(t)
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, 'ocorrencias.pdf')


def _add_signature_footer(canvas, doc, data_professor=None, data_secretaria=None):
    """Adds signature lines for Professor and Secretary at the bottom of the page,
    with different dates (Prof=last launch, Sec=last confirmation), and draws the Capelum logo centered."""
    canvas.saveState()

    # Configuration
    page_width, page_height = doc.pagesize
    margin = 1.5 * cm
    line_width = 7 * cm
    line_y  = 3.2 * cm
    text_y  = 2.8 * cm
    small_y = 2.4 * cm

    # ── Logo Capelum centralizado no rodapé ────────────────────
    logo_path = _get_logo_path(mode='capelum')
    if logo_path:
        logo_w, logo_h = 3.5 * cm, 1.75 * cm
        logo_x = (page_width - logo_w) / 2
        logo_y = 0.5 * cm
        try:
            canvas.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # ── Assinatura Professor (esquerda) ─────────────────
    canvas.setFont('Helvetica', 9)
    canvas.line(margin, line_y, margin + line_width, line_y)
    canvas.drawCentredString(margin + (line_width / 2), text_y, 'Assinatura do Professor')
    
    # Data do lançamento do Professor
    if data_professor:
        if hasattr(data_professor, 'astimezone'): data_professor = data_professor.astimezone()
        prof_str = f'Lançado em: {data_professor.strftime("%d/%m/%Y %H:%M")}'
    else:
        from datetime import datetime as dt
        prof_str = f'Assinado eletronicamente em: {dt.now().strftime("%d/%m/%Y %H:%M")}'
    
    canvas.setFont('Helvetica-Oblique', 7)
    canvas.drawCentredString(margin + (line_width / 2), small_y, prof_str)

    # ── Assinatura Secretaria (direita) ─────────────────
    canvas.setFont('Helvetica', 9)
    canvas.line(page_width - margin - line_width, line_y, page_width - margin, line_y)
    canvas.drawCentredString(page_width - margin - (line_width / 2), text_y, 'Assinatura da Secretaria')
    
    # Data da confirmação da Secretaria
    if data_secretaria:
        if hasattr(data_secretaria, 'astimezone'): data_secretaria = data_secretaria.astimezone()
        sec_str = f'Confirmado pela Secretaria em: {data_secretaria.strftime("%d/%m/%Y %H:%M")}'
    else:
        from datetime import datetime as dt
        sec_str = f'Assinado eletronicamente em: {dt.now().strftime("%d/%m/%Y %H:%M")}'

    canvas.setFont('Helvetica-Oblique', 7)
    canvas.drawCentredString(page_width - margin - (line_width / 2), small_y, sec_str)

    canvas.restoreState()


@login_required
def exportar_conteudos_pdf(request):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    title_style = _get_saas_title_style(styles)
    small = ParagraphStyle('small', fontSize=7, leading=9, textColor=colors.HexColor('#374151'))
    filter_style = ParagraphStyle('filters', fontSize=9, italic=True, textColor=colors.HexColor('#6B7280'))
    cell_normal = ParagraphStyle('cell_normal', fontSize=8, leading=10, textColor=colors.HexColor('#374151'))

    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    elems.append(Paragraph('Conteúdo Programático - SCA', title_style))
    
    qs, resumo_filtros = filtrar_conteudos(request, conteudos_do_usuario(request))
    if resumo_filtros:
        elems.append(Paragraph(f"Filtros aplicados: {resumo_filtros}", filter_style))
        
    elems.append(Spacer(1, 0.3*cm))
    data = [['Data', 'Turmas', 'Professor', 'Disciplina', 'Descrição']]
    for c in qs:
        data.append([
            c.data.strftime('%d/%m/%Y') if c.data else '',
            c.turmas_str(),
            c.professor.nome if c.professor else '',
            Paragraph(c.disciplina.nome if c.disciplina else '', cell_normal),
            Paragraph(c.descricao, small),
        ])
    # Total width with 1.0cm margins on A4 (21cm) is 19cm.
    # 1.8+1.6+2.8+3.4+9.4 = 19.0cm (Perfect Fill)
    t = Table(data, colWidths=[1.8*cm, 1.6*cm, 2.8*cm, 3.4*cm, 9.4*cm], repeatRows=1)
    t.setStyle(_get_saas_table_style())
    elems.append(t)

    # Datas das assinaturas no queryset
    from functools import partial
    from django.db.models import Max
    resumo = qs.aggregate(max_criado=Max('criado_em'), max_confirmado=Max('confirmado_em'))
    
    footer_fn = partial(_add_signature_footer, 
                        data_professor=resumo['max_criado'], 
                        data_secretaria=resumo['max_confirmado'])

    doc.build(elems, onFirstPage=footer_fn, onLaterPages=footer_fn)
    return _pdf_response(buf, 'conteudos.pdf')

@login_required
def exportar_alocacao_pdf(request):
    prof = get_professor(request.user)
    if prof and not prof.pode_gerar_relatorios:
        return HttpResponse('Acesso negado', status=403)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=0.5*cm, rightMargin=0.5*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, leading=8)
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    title_style = _get_saas_title_style(styles)
    elems.append(Paragraph('Relatório de Alocação de Professores', title_style))
    elems.append(Spacer(1, 0.5*cm))
    
    from django.db.models import Prefetch
    professores = Professor.objects.filter(cargo='PROFESSOR').prefetch_related(
        'disciplinas', 'turmas', 
        Prefetch('grade_horaria', queryset=GradeHoraria.objects.select_related('turma', 'disciplina'))
    )
    professores = ordenar_por_nome(professores)
    
    data = [['Professor', 'Disciplinas', 'Turmas', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex']]
    for p in professores:
        discs = ", ".join([d.nome for d in p.disciplinas.all()])
        turmas_list = sorted([t.codigo for t in p.turmas.all()])
        turmas = ", ".join(turmas_list)
        
        seg = []
        ter = []
        qua = []
        qui = []
        sex = []
        for gh in p.grade_horaria.all():
            line = f"{gh.hora_inicio.strftime('%H:%M')}: {gh.turma.codigo} ({gh.disciplina.nome})"
            if gh.dia_semana == '1': seg.append(line)
            elif gh.dia_semana == '2': ter.append(line)
            elif gh.dia_semana == '3': qua.append(line)
            elif gh.dia_semana == '4': qui.append(line)
            elif gh.dia_semana == '5': sex.append(line)
        
        data.append([
            p.nome, 
            Paragraph(discs, small_style), 
            Paragraph(turmas, small_style),
            Paragraph("<br/>".join(seg), small_style),
            Paragraph("<br/>".join(ter), small_style),
            Paragraph("<br/>".join(qua), small_style),
            Paragraph("<br/>".join(qui), small_style),
            Paragraph("<br/>".join(sex), small_style)
        ])
    # Total width with 0.5cm margins on A4 (21cm) is 20cm.
    # 2.0 + 2.5 + 1.5 + 5 * 2.5 = 6.0 + 12.5 = 18.5cm (Safe)
    t = Table(data, colWidths=[2.0*cm, 2.5*cm, 1.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm], repeatRows=1)
    t.setStyle(_get_saas_table_style())
    elems.append(t)
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, 'alocacao_professores.pdf')

@login_required
def exportar_pendencias_pdf(request):
    """Exports the pendency report table to PDF."""
    prof_user = get_professor(request.user)
    if prof_user and not prof_user.pode_gerar_relatorios:
        return HttpResponse('Acesso negado', status=403)


    prof_ids_com_grade = GradeHoraria.objects.filter(turma__ano_letivo=request.ano_letivo, turma__escola=request.escola).values_list('professor_id', flat=True).distinct()
    professores = ordenar_por_nome(Professor.objects.filter(pk__in=prof_ids_com_grade))
    nome_filtro = request.GET.get('nome', '')
    data_ini = request.GET.get('data_ini', '')
    data_fim = request.GET.get('data_fim', '')

    if nome_filtro:
        professores = professores.filter(nome__icontains=nome_filtro)

    feriados_set = get_feriados(ano_letivo=request.ano_letivo, escola=request.escola)
    relatorio = []
    for p in professores:
        stats = calcular_stats_conteudo(p, data_ini=data_ini, data_fim=data_fim, feriados=feriados_set, ano_letivo=request.ano_letivo, escola=request.escola)
        if stats['total_conteudo'] > 0:
            p.stats = stats
            relatorio.append(p)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))

    title = 'Pendências de Conteúdo'
    if data_ini and data_fim:
        title += f' ({data_ini} a {data_fim})'
    elif data_ini:
        title += f' (desde {data_ini})'
        
    title_style = _get_saas_title_style(styles)
    elems.append(Paragraph(title, title_style))
    elems.append(Spacer(1, 0.5*cm))

    data = [['Professor', 'Total Esperado', 'Preenchidos', 'Faltam (Hoje)', 'Faltam (Total)']]
    for p in relatorio:
        data.append([
            p.nome,
            str(p.stats['total_conteudo']),
            str(p.stats['preenchidos']),
            str(p.stats['faltam_ate_hoje']),
            str(p.stats['faltam']),
        ])
    
    t = Table(data, colWidths=[8*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm], repeatRows=1)
    saas_style = _get_saas_table_style()
    saas_style.add('ALIGN', (1, 0), (-1, -1), 'CENTER')
    t.setStyle(saas_style)
    elems.append(t)
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, 'pendencias.pdf')


# ──────────────────────────────────────────────
# BOLETINS PDF
# ──────────────────────────────────────────────
from decimal import Decimal

@login_required
def exportar_boletim_turma_pdf(request, codigo):
    prof = get_professor(request.user)
    if prof and not prof.pode_ver_tudo and prof.cargo not in ('COORDENADOR', 'AUX_COORD', 'PROFESSOR'):
        messages.error(request, 'Sem permissão para exportar boletins.')
        return redirect('dashboard')

    turma = get_object_or_404(
        Turma, codigo=codigo,
        escola=request.escola, ano_letivo=request.ano_letivo
    )
    alunos = Aluno.objects.filter(turma=turma).order_by('nome')

    notas_turma_qs = NotaBimestral.objects.filter(
        aluno__turma=turma,
        ano_letivo=request.ano_letivo,
    ).select_related('aluno', 'disciplina')

    pas_turma_qs = ProvaAuxiliar.objects.filter(
        aluno__turma=turma,
        ano_letivo=request.ano_letivo,
    ).select_related('aluno', 'disciplina')

    # Indices
    notas_idx = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'valor': None, 'substituido_por_pa': False})))
    pas_idx   = defaultdict(lambda: defaultdict(dict))

    for pa in pas_turma_qs:
        pas_idx[pa.aluno_id][pa.disciplina_id][pa.numero_pa] = pa.nota

    for nota in notas_turma_qs:
        aid, did, b = nota.aluno_id, nota.disciplina_id, nota.bimestre
        if nota.nao_avaliado:
            pa_num = 1 if b in (1, 2) else 2
            pa_val = pas_idx[aid][did].get(pa_num)
            if pa_val is not None:
                notas_idx[aid][did][b] = {'valor': pa_val, 'substituido_por_pa': True}
            else:
                notas_idx[aid][did][b] = {'valor': 'NA', 'substituido_por_pa': False}
        else:
            pa_num = 1 if b in (1, 2) else 2
            pa_val = pas_idx[aid][did].get(pa_num)
            nota_final = nota.nota_final
            if pa_val is not None:
                media_pa = round((nota_final + pa_val) / 2, 1)
                if media_pa > nota_final:
                    notas_idx[aid][did][b] = {'valor': media_pa, 'substituido_por_pa': True}
                else:
                    notas_idx[aid][did][b] = {'valor': nota_final, 'substituido_por_pa': False}
            else:
                notas_idx[aid][did][b] = {'valor': nota_final, 'substituido_por_pa': False}

    disc_ids = GradeHoraria.objects.filter(turma=turma).values_list('disciplina_id', flat=True).distinct()
    disciplinas = list(Disciplina.objects.filter(pk__in=disc_ids).order_by('grupo__ordem_boletim', 'nome'))

    def _media_anual(aluno_pk, disc_pk):
        bims = notas_idx[aluno_pk][disc_pk]
        vals = []
        for b in (1, 2, 3, 4):
            if b in bims and bims[b]['valor'] is not None:
                v = bims[b]['valor']
                vals.append(Decimal('0') if v == 'NA' else v)
        if not vals:
            return None
        return round(sum(vals) / len(vals), 1)

    # Gerar PDF
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Boletim Consolidado - Turma {turma.codigo}"
    )
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))
        
    styles = getSampleStyleSheet()
    
    # Cabeçalho
    title_style = _get_saas_title_style(styles)
    elems.append(Paragraph(f'Boletim Consolidado — Turma {turma.codigo}', title_style))
    elems.append(Spacer(1, 0.5*cm))
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=1,
    )
    elems.append(Paragraph('NA = Não Avaliado | (PA) = Substituído por PA', subtitle_style))
    elems.append(Spacer(1, 1*cm))

    # Construir tabela
    header = ['Aluno']
    for d in disciplinas:
        header.append(d.nome[:15] + ('...' if len(d.nome) > 15 else '')) # Abreviar nomes longos
    header.append('M. Geral')

    data = [header]
    
    # Subheader para bimestres
    sub = ['']
    for _ in disciplinas:
        sub.append('1 | 2 | 3 | 4 | A')
    sub.append('')
    data.append(sub)

    for aluno in alunos:
        linha = [aluno.nome[:25]] # Abreviar nomes longos
        medias_anuais = []
        for disc in disciplinas:
            bims_aluno = notas_idx[aluno.pk][disc.pk]
            cel_str = []
            for b in (1, 2, 3, 4):
                val = bims_aluno.get(b, {'valor': None, 'substituido_por_pa': False})
                if val['valor'] == 'NA':
                    cel_str.append('NA')
                elif val['valor'] is not None:
                    s = str(val['valor'])
                    if val['substituido_por_pa']:
                        s += '*'
                    cel_str.append(s)
                else:
                    cel_str.append('-')
            
            ma = _media_anual(aluno.pk, disc.pk)
            cel_str.append(str(ma) if ma is not None else '-')
            medias_anuais.append(ma)
            
            linha.append(" | ".join(cel_str))
            
        vals_gerais = [v for v in medias_anuais if v is not None]
        mg = round(sum(vals_gerais) / len(vals_gerais), 1) if vals_gerais else None
        linha.append(str(mg) if mg is not None else '-')
        data.append(linha)

    # Estilizar tabela
    col_widths = [6*cm] + [3.8*cm for _ in disciplinas] + [2*cm]
    t = Table(data, colWidths=col_widths, repeatRows=2)
    
    ts = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 2), (0, -1), 'LEFT'), # Alinhar nomes a esquerda
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 9),
        ('FONTSIZE', (0, 2), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 1), 6),
        ('TOPPADDING', (0, 0), (-1, 1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e8f5')),
        ('SPAN', (0, 0), (0, 1)), # Mesclar Aluno
        ('SPAN', (-1, 0), (-1, 1)), # Mesclar M. Geral
    ])
    
    # Listrar linhas
    for i in range(2, len(data)):
        if i % 2 == 0:
            ts.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9fbff'))
            
    t.setStyle(ts)
    elems.append(t)
    
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, f'boletim_turma_{turma.codigo}.pdf')


@login_required
def exportar_boletim_aluno_pdf(request, pk):
    prof = get_professor(request.user)
    if prof and not prof.pode_ver_tudo and prof.cargo not in ('COORDENADOR', 'AUX_COORD', 'PROFESSOR', 'ORIENTADOR'):
        messages.error(request, 'Sem permissão para exportar boletins.')
        return redirect('dashboard')

    aluno = get_object_or_404(Aluno, pk=pk)
    turma = aluno.turma

    notas_qs = NotaBimestral.objects.filter(
        aluno=aluno,
        ano_letivo=request.ano_letivo,
    ).select_related('disciplina', 'disciplina__grupo')

    pas_qs = ProvaAuxiliar.objects.filter(
        aluno=aluno, ano_letivo=request.ano_letivo
    )
    pas_por_disc = defaultdict(dict)
    for pa in pas_qs:
        pas_por_disc[pa.disciplina_id][pa.numero_pa] = pa.nota

    notas_por_disc = defaultdict(lambda: defaultdict(lambda: {'valor': None, 'substituido_por_pa': False}))
    
    for nota in notas_qs:
        disc_id = nota.disciplina_id
        b = nota.bimestre
        
        if nota.nao_avaliado:
            pa_num = 1 if b in (1, 2) else 2
            pa_val = pas_por_disc[disc_id].get(pa_num)
            if pa_val is not None:
                notas_por_disc[disc_id][b] = {'valor': pa_val, 'substituido_por_pa': True}
            else:
                notas_por_disc[disc_id][b] = {'valor': 'NA', 'substituido_por_pa': False}
        else:
            pa_num = 1 if b in (1, 2) else 2
            pa_val = pas_por_disc[disc_id].get(pa_num)
            nota_final = nota.nota_final
            if pa_val is not None:
                media_pa = round((nota_final + pa_val) / 2, 1)
                if media_pa > nota_final:
                    notas_por_disc[disc_id][b] = {'valor': media_pa, 'substituido_por_pa': True}
                else:
                    notas_por_disc[disc_id][b] = {'valor': nota_final, 'substituido_por_pa': False}
            else:
                notas_por_disc[disc_id][b] = {'valor': nota_final, 'substituido_por_pa': False}

    def _medias_e_anual(disc_pks):
        medias = []
        for b in (1, 2, 3, 4):
            valores = []
            for dpk in disc_pks:
                if b in notas_por_disc[dpk]:
                    v = notas_por_disc[dpk][b]['valor']
                    if v is not None:
                        valores.append(Decimal('0') if v == 'NA' else v)
            medias.append(round(sum(valores) / len(valores), 1) if valores else None)
        vals_validos = [v for v in medias if v is not None]
        media_anual = round(sum(vals_validos) / len(vals_validos), 1) if vals_validos else None
        return medias, media_anual

    grupos_no_boletim = []
    grupos = GrupoDisciplina.objects.prefetch_related('disciplinas').order_by('ordem_boletim')
    for grupo in grupos:
        disc_ids_com_nota = [d.pk for d in grupo.disciplinas.all() if d.pk in notas_por_disc]
        if not disc_ids_com_nota: continue
        medias, media_anual = _medias_e_anual(disc_ids_com_nota)
        grupos_no_boletim.append({
            'nome': grupo.nome_boletim,
            'medias': [{'valor': m, 'substituido_por_pa': False} for m in medias],
            'media_anual': media_anual,
            'is_grupo': True,
        })

    discs_standalone = Disciplina.objects.filter(
        pk__in=notas_por_disc.keys(), grupo__isnull=True
    ).order_by('nome')
    for disc in discs_standalone:
        medias, media_anual = _medias_e_anual([disc.pk])
        medias_detalhadas = []
        for b in (1, 2, 3, 4):
            if b in notas_por_disc[disc.pk]:
                medias_detalhadas.append(notas_por_disc[disc.pk][b])
            else:
                medias_detalhadas.append({'valor': None, 'substituido_por_pa': False})

        grupos_no_boletim.append({
            'nome': disc.nome,
            'medias': medias_detalhadas,
            'media_anual': media_anual,
            'is_grupo': False,
        })

    # Gerar PDF
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Boletim - {aluno.nome}"
    )
    
    elems = []
    logo = _get_logo_element()
    if logo:
        elems.append(logo)
        elems.append(Spacer(1, 0.2*cm))
        
    styles = getSampleStyleSheet()
    
    # Cabeçalho
    title_style = _get_saas_title_style(styles)
    elems.append(Paragraph('Boletim Escolar', title_style))
    elems.append(Spacer(1, 0.3*cm))
    
    info_style = ParagraphStyle(
        'Info', parent=styles['Normal'],
        fontSize=12, alignment=1, textColor=colors.HexColor('#333333')
    )
    elems.append(Paragraph(f'<b>Aluno:</b> {aluno.nome}', info_style))
    elems.append(Paragraph(f'<b>Turma:</b> {turma.codigo}', info_style))
    elems.append(Spacer(1, 1*cm))

    # Tabela de notas
    data = [['Disciplina', '1º Bim', '2º Bim', '3º Bim', '4º Bim', 'Média Anual']]
    
    for linha in grupos_no_boletim:
        row = [linha['nome']]
        for v in linha['medias']:
            if v['valor'] == 'NA':
                row.append('NA')
            elif v['valor'] is not None:
                s = str(v['valor'])
                if v['substituido_por_pa']: s += '*'
                row.append(s)
            else:
                row.append('-')
        
        row.append(str(linha['media_anual']) if linha['media_anual'] is not None else '-')
        data.append(row)

    t = Table(data, colWidths=[6.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2.5*cm], repeatRows=1)
    
    ts = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e8f5')),
        ('BACKGROUND', (-1, 1), (-1, -1), colors.HexColor('#eef4ff')), # Coluna de média anual
    ])
    
    # Destacar grupos e pintar listrado
    for i, linha in enumerate(grupos_no_boletim, start=1):
        if linha['is_grupo']:
            ts.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
        elif i % 2 == 0:
            ts.add('BACKGROUND', (0, i), (-2, i), colors.HexColor('#f9fbff'))

    t.setStyle(ts)
    elems.append(t)
    
    elems.append(Spacer(1, 1*cm))
    leg_style = ParagraphStyle('Leg', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#666666'))
    elems.append(Paragraph('NA = Não Avaliado (ausente) &nbsp;&nbsp;|&nbsp;&nbsp; * = Substituído por Prova Auxiliar', leg_style))
    elems.append(Paragraph('Nota mínima para aprovação: 5,0', leg_style))
    
    doc.build(elems, onFirstPage=_add_signature_footer, onLaterPages=_add_signature_footer)
    return _pdf_response(buf, f'boletim_aluno_{aluno.pk}.pdf')


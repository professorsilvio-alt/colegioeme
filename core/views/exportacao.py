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
                     SugestaoConteudo, Turma, Configuracao)
from ..utils import get_professor, get_feriados, get_client_ip

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
    if not secret or not token:
        # Se não configurado, permite a requisição (modo de desenvolvimento)
        return True
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
def ocorrencias_do_usuario(request):
    user = request.user
    prof = get_professor(user)
    ano_letivo = request.ano_letivo
    escola = request.escola
    qs = Ocorrencia.objects.select_related('turma', 'professor', 'disciplina').prefetch_related('alunos')
    
    if escola:
        qs = qs.filter(turma__escola=escola)
    if ano_letivo:
        qs = qs.filter(turma__ano_letivo=ano_letivo)
    
    if not prof:
        return qs  # superuser/admin sem perfil: vê tudo
    
    # Secretária não deve visualizar as ocorrências
    if not prof.pode_ver_ocorrencias:
        return Ocorrencia.objects.none()

    if prof.pode_ver_tudo:
        # Cargos de gestão e inspetores veem tudo (respeitando a restrição de secretária acima)
        pass
    else:
        # Professor comum vê apenas suas próprias ocorrências
        qs = qs.filter(professor=prof)
    return qs


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
        'Eletiva 1', 'Eletiva 2', # Nomes legados, caso existam registros
        'Sociedade e Cidadania', 'Sustentabilidade e Meio Ambiente',
        'Educação Financeira', 'Múltiplas Linguagens',
        'Ciências da Natureza', 'Ciências Humanas', 
        'Matemática e suas tecnologias', 'Linguagens e códigos'
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
    ).order_by('nome')
    
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
    professores = Professor.objects.filter(pk__in=prof_ids_com_grade).order_by('nome')
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

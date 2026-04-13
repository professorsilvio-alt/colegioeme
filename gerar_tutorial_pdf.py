"""
Gerador do Tutorial PDF do Sistema EME / Capelum
Uso: python gerar_tutorial_pdf.py
Saída: tutorial_professores.pdf (na mesma pasta)
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable

# ──────────────────────────────────────────
# CONSTANTES DE COR
# ──────────────────────────────────────────
AZUL_ESCURO  = colors.HexColor('#0D1B3E')   # navy principal
AZUL_MEDIO   = colors.HexColor('#1a3a6b')   # seção
AZUL_CLARO   = colors.HexColor('#e8edf7')   # fundo de cabeçalho de tabela
DOURADO      = colors.HexColor('#C8A951')   # destaque / linhas
CINZA_TEXTO  = colors.HexColor('#2c2c2c')
CINZA_LINHA  = colors.HexColor('#d0d5e0')
BRANCO       = colors.white
VERDE        = colors.HexColor('#1a7a45')
VERMELHO     = colors.HexColor('#9b1a1a')
AMARELO_AVISO = colors.HexColor('#fffbe6')
BORDA_AVISO  = colors.HexColor('#c8a000')

LOGO_PATH = os.path.join(
    os.path.dirname(__file__),
    'core', 'static', 'core', 'capelum_logo_final.png'
)

OUTPUT_PDF = os.path.join(os.path.dirname(__file__), 'tutorial_professores.pdf')
URL_SISTEMA = 'https://capelum.com'

SCREEN_DIR = r'C:\Users\cejar\.gemini\antigravity\brain\a3439257-f5ea-47de-9204-611085faf455'
SCREENS = {
    'login':           os.path.join(SCREEN_DIR, 'screen_login_1775568321341.png'),
    'dashboard':       os.path.join(SCREEN_DIR, 'prof_dashboard_1775573889628.png'),
    'ocorrencias':     os.path.join(SCREEN_DIR, 'prof_ocorrencias_1775573899461.png'),
    'form_ocorrencia': os.path.join(SCREEN_DIR, 'prof_form_ocorrencia_1775573911704.png'),
    'conteudos':       os.path.join(SCREEN_DIR, 'prof_conteudos_1775573925419.png'),
    'form_conteudo':   os.path.join(SCREEN_DIR, 'prof_form_conteudo_1775573934667.png'),
    'pendencias':      os.path.join(SCREEN_DIR, 'prof_pendencias_1775573944951.png'),
}

# ──────────────────────────────────────────
# ESTILOS
# ──────────────────────────────────────────
base_styles = getSampleStyleSheet()

def make_styles():
    s = {}

    s['capa_titulo'] = ParagraphStyle(
        'capaTitulo',
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=AZUL_ESCURO,
        alignment=TA_CENTER,
        leading=34,
        spaceAfter=6,
    )
    s['capa_subtitulo'] = ParagraphStyle(
        'capaSubtitulo',
        fontName='Helvetica',
        fontSize=14,
        textColor=AZUL_MEDIO,
        alignment=TA_CENTER,
        leading=18,
        spaceAfter=4,
    )
    s['capa_url'] = ParagraphStyle(
        'capaUrl',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=AZUL_MEDIO,
        alignment=TA_CENTER,
        leading=18,
        spaceAfter=0,
    )
    s['titulo_secao'] = ParagraphStyle(
        'tituloSecao',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=BRANCO,
        leading=18,
        spaceBefore=8,
        spaceAfter=4,
        leftIndent=0,
    )
    s['corpo'] = ParagraphStyle(
        'corpo',
        fontName='Helvetica',
        fontSize=10,
        textColor=CINZA_TEXTO,
        leading=15,
        spaceBefore=4,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
    )
    s['corpo_bold'] = ParagraphStyle(
        'corpoBold',
        parent=s['corpo'],
        fontName='Helvetica-Bold',
    )
    s['nota'] = ParagraphStyle(
        'nota',
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        leading=13,
        spaceBefore=4,
        spaceAfter=4,
        leftIndent=8,
        rightIndent=8,
        alignment=TA_JUSTIFY,
    )
    s['aviso'] = ParagraphStyle(
        'aviso',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#7a5500'),
        leading=13,
        spaceBefore=2,
        spaceAfter=2,
    )
    s['passo'] = ParagraphStyle(
        'passo',
        fontName='Helvetica',
        fontSize=10,
        textColor=CINZA_TEXTO,
        leading=15,
        leftIndent=14,
        spaceBefore=2,
        spaceAfter=2,
    )
    s['bullet'] = ParagraphStyle(
        'bullet',
        fontName='Helvetica',
        fontSize=10,
        textColor=CINZA_TEXTO,
        leading=15,
        leftIndent=14,
        bulletIndent=4,
        spaceBefore=1,
        spaceAfter=1,
        bulletFontName='Helvetica-Bold',
        bulletFontSize=10,
        bulletColor=DOURADO,
    )
    s['th'] = ParagraphStyle(
        'th',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=AZUL_ESCURO,
        alignment=TA_CENTER,
        leading=12,
    )
    s['td'] = ParagraphStyle(
        'td',
        fontName='Helvetica',
        fontSize=9,
        textColor=CINZA_TEXTO,
        leading=12,
        alignment=TA_LEFT,
    )
    s['td_center'] = ParagraphStyle(
        'tdCenter',
        parent=s['td'],
        alignment=TA_CENTER,
    )
    s['rodape'] = ParagraphStyle(
        'rodape',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER,
        leading=11,
    )
    s['subtitulo'] = ParagraphStyle(
        'subtitulo',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=AZUL_MEDIO,
        leading=15,
        spaceBefore=10,
        spaceAfter=4,
    )
    s['label_campo'] = ParagraphStyle(
        'labelCampo',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=AZUL_ESCURO,
        leading=13,
    )
    return s

ST = make_styles()

# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────

def cabecalho_secao(numero, titulo):
    """Retorna uma tabela que representa o cabeçalho de seção estilizado."""
    cell = Paragraph(f'<font color="white"><b>{numero} {titulo}</b></font>', ST['titulo_secao'])
    t = Table([[cell]], colWidths=[None])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), AZUL_MEDIO),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('LINEBELOW', (0, 0), (-1, -1), 2, DOURADO),
    ]))
    return t

def caixa_aviso(texto):
    """Caixa de atenção/aviso amarela."""
    p = Paragraph(f'⚠ {texto}', ST['aviso'])
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), AMARELO_AVISO),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('BOX', (0, 0), (-1, -1), 1, BORDA_AVISO),
        ('ROUNDEDCORNERS', [3, 3, 3, 3]),
    ]))
    return t

def caixa_dica(texto):
    """Caixa de dica azul claro."""
    p = Paragraph(f'💡 {texto}', ST['nota'])
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), AZUL_CLARO),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, AZUL_MEDIO),
        ('ROUNDEDCORNERS', [3, 3, 3, 3]),
    ]))
    return t

def tabela_dados(header_row, data_rows, col_widths):
    """Tabela padrão com cabeçalho azul."""
    all_rows = [[Paragraph(h, ST['th']) for h in header_row]]
    for row in data_rows:
        all_rows.append([Paragraph(str(c), ST['td_center'] if i > 0 and len(row) > 2 else ST['td'])
                         for i, c in enumerate(row)])
    t = Table(all_rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_CLARO),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, AZUL_MEDIO),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRANCO, colors.HexColor('#f5f7fb')]),
        ('GRID', (0, 0), (-1, -1), 0.5, CINZA_LINHA),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return t

def linha_divisoria():
    return HRFlowable(width='100%', thickness=0.5, color=CINZA_LINHA, spaceAfter=10, spaceBefore=10)

def insert_screenshot(key, legenda, max_w=None, max_h=8*cm):
    """Insere uma screenshot com borda, sombra leve e legenda centrada."""
    path = SCREENS.get(key, '')
    if not path or not os.path.exists(path):
        return []
    if max_w is None:
        max_w = FRAME_W
    img = Image(path, width=max_w, height=max_h, kind='proportional')
    img.hAlign = 'CENTER'
    # Envolve em tabela para adicionar borda e fundo
    img_table = Table([[img]], colWidths=[FRAME_W])
    img_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, CINZA_LINHA),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fafafa')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROUNDEDCORNERS', [3,3,3,3]),
    ]))
    caption_style = ParagraphStyle(
        'caption', fontName='Helvetica-Oblique', fontSize=8,
        textColor=colors.HexColor('#666666'), alignment=TA_CENTER,
        spaceBefore=3, spaceAfter=8,
    )
    caption = Paragraph(legenda, caption_style)
    return [Spacer(1, 0.2*cm), img_table, caption]

def passos(lista):
    """Gera parágrafos numerados estilizados."""
    items = []
    for i, texto in enumerate(lista, 1):
        items.append(Paragraph(f'<b><font color="#1a3a6b">{i}.</font></b>  {texto}', ST['passo']))
    return items

def bullets(lista, cor_bullet='•'):
    items = []
    for texto in lista:
        items.append(Paragraph(f'<b><font color="#C8A951">{cor_bullet}</font></b>  {texto}', ST['bullet']))
    return items

# ──────────────────────────────────────────
# TEMPLATES DE PÁGINA
# ──────────────────────────────────────────

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
FRAME_W = PAGE_W - 2 * MARGIN

HEADER_H = 2.2 * cm   # altura do cabeçalho em todas as páginas
FOOTER_H = 1.4 * cm  # altura do rodapé em todas as páginas

def capa_frame():
    """Frame da capa ocupa a área útil abaixo do header e acima do footer."""
    return Frame(
        MARGIN, FOOTER_H,
        FRAME_W, PAGE_H - HEADER_H - FOOTER_H,
        leftPadding=0, rightPadding=0, id='capa'
    )

def corpo_frame():
    """Frame das páginas internas."""
    return Frame(
        MARGIN, FOOTER_H,
        FRAME_W, PAGE_H - HEADER_H - FOOTER_H,
        leftPadding=0, rightPadding=0, id='corpo'
    )

def _draw_header_footer(canvas, doc):
    """Cabeçalho e rodapé comuns — fundo branco com linha dourada."""
    canvas.saveState()

    # ── CABEÇALHO ──
    # Linha dourada inferior do header
    canvas.setFillColor(DOURADO)
    canvas.rect(0, PAGE_H - HEADER_H - 2, PAGE_W, 2, fill=1, stroke=0)
    # Linha fina azul no topo absoluto
    canvas.setFillColor(AZUL_ESCURO)
    canvas.rect(0, PAGE_H - 3, PAGE_W, 3, fill=1, stroke=0)

    # Logo no canto esquerdo do header
    if os.path.exists(LOGO_PATH):
        logo_h = HEADER_H - 0.5 * cm
        logo_w = logo_h * 2.5  # proporção aproximada da logo
        canvas.drawImage(
            LOGO_PATH,
            MARGIN,
            PAGE_H - HEADER_H + (HEADER_H - logo_h) / 2,
            width=logo_w, height=logo_h,
            preserveAspectRatio=True, mask='auto'
        )

    # Texto do header à direita
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(CINZA_TEXTO)
    canvas.drawRightString(
        PAGE_W - MARGIN,
        PAGE_H - HEADER_H + 0.55 * cm,
        'Manual do Usuário — Capelum Controle Acadêmico'
    )

    # ── RODAPÉ ──
    # Linha dourada superior do rodapé
    canvas.setFillColor(DOURADO)
    canvas.rect(0, FOOTER_H, PAGE_W, 1.5, fill=1, stroke=0)
    # Linha fina azul na base
    canvas.setFillColor(AZUL_ESCURO)
    canvas.rect(0, 0, PAGE_W, 2, fill=1, stroke=0)

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(CINZA_TEXTO)
    canvas.drawString(MARGIN, FOOTER_H / 2 - 3, URL_SISTEMA)
    canvas.drawRightString(
        PAGE_W - MARGIN, FOOTER_H / 2 - 3,
        f'Pagina {doc.page}'
    )

    canvas.restoreState()

def on_capa(canvas, doc):
    _draw_header_footer(canvas, doc)

def on_normal(canvas, doc):
    _draw_header_footer(canvas, doc)

# ──────────────────────────────────────────
# CONTEÚDO
# ──────────────────────────────────────────

def build_content():
    story = []

    # ── CAPA ──────────────────────────────
    story.append(NextPageTemplate('capa'))

    # Espaço abaixo do header
    story.append(Spacer(1, 2.0*cm))

    story.append(Paragraph('Manual do Usuário', ST['capa_titulo']))
    story.append(Paragraph('Sistema de Gestão Escolar Capelum', ST['capa_subtitulo']))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='60%', thickness=2, color=DOURADO,
                             spaceBefore=0, spaceAfter=10, hAlign='CENTER'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph('Guia de Utilização para o Corpo Docente', ST['capa_subtitulo']))
    story.append(Spacer(1, 3.5*cm))

    # Caixa de destaque com URL
    url_p = Paragraph(
        f'Acesso ao sistema:<br/><b><font color="#1a3a6b" size="14">{URL_SISTEMA}</font></b>',
        ST['capa_subtitulo']
    )
    url_table = Table([[url_p]], colWidths=[FRAME_W])
    url_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AZUL_CLARO),
        ('BOX', (0,0), (-1,-1), 1.5, DOURADO),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('ROUNDEDCORNERS', [6,6,6,6]),
    ]))
    story.append(url_table)
    story.append(Spacer(1, 3.5*cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=CINZA_LINHA,
                             spaceBefore=0, spaceAfter=8))
    story.append(Paragraph(
        'Versão 1.0  ·  Ano Letivo 2026  ·  Documento de Uso Interno',
        ST['capa_subtitulo']
    ))

    story.append(PageBreak())

    # ── RESTANTE DAS PÁGINAS ──────────────
    story.append(NextPageTemplate('normal'))

    # ── 1. ACESSO ─────────────────────────
    story.append(Spacer(1, 0.2*cm))
    story.append(cabecalho_secao('1', 'Acesso ao Sistema'))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        'O Capelum é acessado exclusivamente por navegador de internet (Google Chrome, '
        'Firefox ou <nobr>Microsoft Edge</nobr>). Não é necessário instalar nenhum aplicativo no '
        'computador ou celular.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Como realizar o login</b>', ST['subtitulo']))
    story.append(Paragraph(
        'A tela de login é dividida em dois painéis: à esquerda, o painel de identidade visual '
        'do Capelum; à direita, o formulário de acesso com os campos de usuário e senha.',
        ST['corpo']
    ))
    story.extend(passos([
        f'Abra o navegador e acesse: <b><font color="#1a3a6b">{URL_SISTEMA}</font></b>',
        'No painel direito, informe seu <b>usuário</b> (geralmente seu e-mail ou nome fornecido '
        'pela coordenação) e a <b>senha</b> provisória recebida.',
        'Clique em <b>Entrar</b>. Você será direcionado ao Painel Principal.',
    ]))
    story.extend(insert_screenshot('login', 'Figura 1 — Tela de login do Capelum: painel de identidade visual à esquerda e formulário de acesso à direita.', max_h=6*cm))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Primeiro acesso — troca de senha e cadastro de e-mail</b>', ST['subtitulo']))
    story.append(Paragraph(
        'No primeiro acesso, o sistema realizará dois procedimentos obrigatórios:',
        ST['corpo']
    ))
    story.extend(bullets([
        '<b>Cadastro de e-mail de contato:</b> você informará um endereço de e-mail pessoal '
        'que será utilizado para recuperação de senha e comunicações do sistema.',
        '<b>Criação de nova senha:</b> a senha provisória fornecida pela coordenação deverá '
        'ser substituída por uma senha pessoal com no mínimo 6 caracteres.',
    ]))
    story.append(Paragraph(
        'Após concluir ambos os passos, você será redirecionado ao Painel Principal automaticamente.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(caixa_aviso(
        'Não compartilhe sua senha com ninguém. Cada professor possui acesso individual '
        'e todos os lançamentos ficam registrados com seu nome de usuário.'
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Encerrando a sessão</b>', ST['subtitulo']))
    story.append(Paragraph(
        'Para sair, clique no botão <b>Sair</b> no menu superior da tela. '
        'Por segurança, a sessão é encerrada automaticamente após <b>8 horas</b> de inatividade.',
        ST['corpo']
    ))
    story.append(linha_divisoria())

    # ── 2. PAINEL PRINCIPAL ───────────────
    story.append(cabecalho_secao('2', 'Painel Principal (Dashboard)'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'Após o login, o usuário é direcionado ao Painel Principal. '
        'Esta tela reúne as informações mais relevantes e dá acesso a todas as funcionalidades do sistema.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Cards de resumo</b>', ST['subtitulo']))
    h = ['Indicador', 'Descrição']
    d = [
        ['Lançamentos Totais', 'Número total de aulas previstas para o ano letivo, conforme a grade horária.'],
        ['Já Preenchidos', 'Quantidade de aulas cujo conteúdo programático já foi registrado.'],
        ['Falta Preencher:', 'Aulas que já deveriam ter sido lançadas (até a data atual) e ainda não possuem registro de conteúdo. Aulas futuras não são contabilizadas.'],
    ]
    story.append(tabela_dados(h, d, [5*cm, None]))
    story.append(Spacer(1, 0.3*cm))
    story.append(caixa_dica(
        'Mantenha o indicador "Falta Preencher:" sempre zerado. Isso garante que o '
        'diário de classe esteja permanentemente atualizado.'
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Grade de horários semanal</b>', ST['subtitulo']))
    story.append(Paragraph(
        'Professores visualizam sua própria grade horária organizada por dias da semana '
        '(segunda a sexta-feira), com horários, turmas e disciplinas. '
        'Gestores visualizam o logotipo da escola nesta posição.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph('<b>Abas de navegação</b>', ST['subtitulo']))
    story.extend(bullets([
        '<b>Ocorrências:</b> Registro e consulta de incidentes disciplinares.',
        '<b>Conteúdos:</b> Lançamento e consulta do diário de conteúdo programático.',
    ]))
    story.extend(insert_screenshot('dashboard', 'Figura 2 — Painel principal: cards de resumo com totais de ocorrências e lançamentos de conteúdo.', max_h=6*cm))
    story.append(linha_divisoria())

    # ── 3. OCORRÊNCIAS ────────────────────
    story.append(cabecalho_secao('3', 'Registrando uma Ocorrência'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'Uma ocorrência constitui o registro de acontecimentos disciplinares ou situações '
        'relevantes que envolvam um ou mais alunos em contexto escolar. '
        'Todos os registros ficam disponíveis para consulta da equipe gestora.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(caixa_aviso(
        'IMPORTANTE: O módulo de Ocorrências do Capelum NÃO substitui os instrumentos '
        'oficiais já utilizados no dia a dia da escola (livros de ocorrência, fichas '
        'disciplinares, comunicados impressos, etc.). Ele funciona como uma ferramenta '
        'complementar de anotações digitais, permitindo que o professor registre rapidamente '
        'observações comportamentais diárias e as compartilhe com a equipe gestora de forma '
        'ágil e organizada.'
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Procedimento de registro</b>', ST['subtitulo']))
    story.extend(passos([
        'Acesse a aba <b>Ocorrências</b>.',
        'Clique em <b>+ Registrar Nova Ocorrência</b>.',
        'Preencha o formulário conforme a tabela abaixo.',
        'Clique em <b>Salvar Ocorrência</b>.',
    ]))
    story.append(Spacer(1, 0.3*cm))

    h = ['Campo', 'Orientação de preenchimento']
    d = [
        ['Data', 'Data em que o fato ocorreu. Preenchida automaticamente com a data atual.'],
        ['Turma', 'Selecione a turma em que o episódio ocorreu.'],
        ['Alunos', 'Após selecionar a turma, marque os alunos envolvidos (um ou mais).'],
        ['Disciplina', 'Disciplina em que o fato aconteceu.'],
        ['Prof. Responsável', 'Preenchido automaticamente com o nome do usuário logado.'],
        ['Descrição', 'Relate o ocorrido de forma objetiva, sem adjetivações desnecessárias.'],
        ['Status', 'Mantenha como "Aberta". A coordenação atualizará quando a situação for tratada.'],
    ]
    story.append(tabela_dados(h, d, [4*cm, None]))
    story.append(Spacer(1, 0.3*cm))
    story.append(caixa_dica(
        'Boas práticas de escrita: seja factual e objetivo. '
        'Evite julgamentos de valor. Exemplo adequado: '
        '"O estudante recusou-se a sentar após três solicitações, '
        'interrompendo o andamento da aula."'
    ))
    story.extend(insert_screenshot('form_ocorrencia', 'Figura 3 — Formulário de registro de nova ocorrência, exibindo os campos Data, Turma, Alunos e Disciplina.', max_h=6.5*cm))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Consulta, edição e exclusão</b>', ST['subtitulo']))
    story.append(Paragraph(
        'A listagem de ocorrências exibe todas as ocorrências do professor logado, '
        'em ordem cronológica inversa. É possível visualizar o registro completo '
        'clicando em <b>Ver</b>, editar clicando em <b>Editar</b>, '
        'ou excluir pelo ícone 🗑 (a exclusão é permanente e irreversível).',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph('<b>Filtros disponíveis</b>', ST['subtitulo']))
    story.extend(bullets([
        '<b>Turma</b> — exibe apenas ocorrências de uma turma específica.',
        '<b>Status</b> — filtra por situação: Aberta ou Resolvida.',
        '<b>Período</b> — delimita por data inicial e data final.',
    ]))
    story.extend(insert_screenshot('ocorrencias', 'Figura 4 — Listagem de ocorrências com filtros de busca, ações em massa e opções de exportação.', max_h=6*cm))
    story.append(linha_divisoria())

    # ── 4. CONTEÚDO PROGRAMÁTICO ──────────
    story.append(cabecalho_secao('4', 'Lançamento do Diário de Conteúdo'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'O registro do conteúdo programático constitui o diário de classe digital. '
        'O preenchimento é obrigatório e pode ser auditado pela coordenação a qualquer momento. '
        'O sistema garante que apenas aulas previstas na grade horária sejam registradas, '
        'evitando lançamentos indevidos.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('<b>Passo a passo do lançamento</b>', ST['subtitulo']))
    story.extend(passos([
        'Acesse a aba <b>Conteúdos</b> e clique em <b>+ Lançar Conteúdo Programático</b>.',
        '<b>Turma:</b> Selecione a turma em que a aula foi ministrada.',
        '<b>Disciplina:</b> O sistema carregará automaticamente as disciplinas pertinentes àquela turma conforme a grade horária.',
        '<b>Professor:</b> Seu nome será selecionado automaticamente.',
        '<b>Data da Aula:</b> O sistema listará todas as datas válidas do ano letivo (excluindo feriados e fins de semana). Datas já registradas são identificadas com o símbolo <b>✓ já lançado</b>. Selecione a data desejada.',
        '<b>Conteúdo Ministrado:</b> O sistema exibirá sugestões de conteúdo pré-cadastradas '
        'para a disciplina e turma selecionadas, baseadas no material disponibilizado pela '
        'editora <b>Bernoulli</b>. Clique na sugestão para utilizá-la ou redija o conteúdo livremente '  
        '— as sugestões são um ponto de partida, não uma obrigação.',
        'Clique em <b>Salvar Conteúdo</b>.',
    ]))
    story.append(Spacer(1, 0.3*cm))
    story.append(caixa_dica(
        'Seja específico na descrição do conteúdo. Em vez de escrever apenas "Gramática", '
        'prefira: "Análise sintática: sujeito e predicado — exercícios do livro, págs. 45-48."'
    ))
    story.extend(insert_screenshot('form_conteudo', 'Figura 5 — Formulário de lançamento de conteúdo programático, com seleção em cascata de Turma, Disciplina, Professor e Data.', max_h=6.5*cm))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('<b>Cópia simultânea para turmas da mesma série</b>', ST['subtitulo']))
    story.append(Paragraph(
        'Ao selecionar uma turma, o sistema identifica automaticamente outras turmas do mesmo ano '
        'letivo em que o professor também leciona. Caso a mesma aula tenha sido ministrada para '
        'mais de uma turma, basta marcar as turmas adicionais no painel que surge abaixo do '
        'seletor de turma. O conteúdo será registrado para todas simultaneamente.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(caixa_aviso(
        'Turmas em que o professor não possui aula na data selecionada aparecem '
        'desabilitadas (cinza) e não podem ser marcadas.'
    ))
    story.extend(insert_screenshot('conteudos', 'Figura 6 — Aba Diário com listagem de conteúdos e botões de lançamento normal e Aula Extra.', max_h=6*cm))
    story.append(linha_divisoria())

    # ── 5. AULA EXTRA ─────────────────────
    story.append(cabecalho_secao('5', 'Registro de Aula Extra (⚡)'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'A funcionalidade de <b>Aula Extra</b> destina-se ao registro de conteúdos ministrados '
        'fora da grade horária regular, como eletivas, aulas de reforço, projetos integrados e '
        'áreas temáticas especiais (ex.: Sociedade e Cidadania, Educação Financeira, '
        'Múltiplas Linguagens, Ciências da Natureza).',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('<b>Diferenças em relação ao lançamento regular</b>', ST['subtitulo']))
    story.extend(bullets([
        '<b>Disciplina:</b> apresenta todas as disciplinas disponíveis, incluindo áreas temáticas especiais.',
        '<b>Data:</b> campo de livre escolha — não está restrito à grade horária.',
        'Atribuição ao professor permanece vinculada ao usuário logado.',
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        'Para utilizar, clique no botão <b>⚡ + Aula Extra</b> na aba Conteúdos e preencha '
        'o formulário normalmente.',
        ST['corpo']
    ))
    story.append(linha_divisoria())

    # ── 6. RELATÓRIO DE PENDÊNCIAS ────────
    story.append(cabecalho_secao('6', 'Relatório de Pendências'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'O Relatório de Pendências exibe, de forma consolidada, todas as datas de aulas '
        'que ainda não possuem conteúdo registrado, considerando apenas o período até a '
        'data atual.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('<b>Como acessar</b>', ST['subtitulo']))
    story.extend(passos([
        'Acesse a aba <b>Conteúdos</b>.',
        'Clique no botão <b>📊 Relatório de Pendências</b>.',
        'O painel exibirá os totais de aulas previstas, preenchidas e pendentes.',
        'Para visualizar as datas específicas em atraso, clique em seu nome.',
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(caixa_dica(
        'Recomenda-se acessar o Relatório de Pendências ao menos uma vez por semana '
        'para manter o diário sempre atualizado.'
    ))
    story.extend(insert_screenshot('pendencias', 'Figura 7 — Relatório de Pendências: visão consolidada por professor com totais esperados, preenchidos e em atraso.', max_h=6.5*cm))
    story.append(linha_divisoria())

    # ── 7. EXPORTAÇÃO ─────────────────────
    story.append(cabecalho_secao('7', 'Exportação de Dados'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'Os registros do sistema podem ser exportados para fins de arquivamento, '
        'impressão ou análise em planilhas.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.3*cm))

    h = ['Tipo', 'Formato', 'Como exportar']
    d = [
        ['Ocorrências', 'PDF / CSV', 'Aba Ocorrências → aplicar filtros desejados → botão PDF ou CSV (Filtrado)'],
        ['Conteúdos', 'PDF / CSV', 'Aba Conteúdos → aplicar filtros desejados → botão PDF (Filtrado)'],
    ]
    story.append(tabela_dados(h, d, [3.5*cm, 3*cm, None]))
    story.append(linha_divisoria())

    # ── 8. PERMISSÕES ─────────────────────
    story.append(cabecalho_secao('8', 'Permissões por Perfil de Usuário'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'O sistema adapta automaticamente as funcionalidades disponíveis conforme o perfil '
        'de cada usuário, garantindo que cada profissional acesse apenas o que é '
        'pertinente a suas atribuições.',
        ST['corpo']
    ))
    story.append(Spacer(1, 0.3*cm))

    h = ['Perfil', 'Reg. Ocorr.', 'Lançar Cont.', 'Ver Ocorr.', 'Ver Cont.', 'Exportar']
    d = [
        ['Professor', '✓ Próprias', '✓ Próprios', '✓ Próprias', '✓ Próprios', 'PDF'],
        ['Inspetor', '✓', '—', '✓ Todas', '—', '—'],
        ['Orientador Ed.', '—', '—', '✓ Todas', '✓ Todos', '✓'],
        ['Coordenador', '—', '—', '✓ Todas', '✓ Leitura', '✓'],
        ['Diretor', '✓', '✓', '✓ Todas', '✓ Todos', '✓'],
    ]
    story.append(tabela_dados(h, d, [3.5*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, None]))
    story.append(linha_divisoria())

    # ── 9. BOAS PRÁTICAS ──────────────────
    story.append(cabecalho_secao('9', 'Boas Práticas e Recomendações'))
    story.append(Spacer(1, 0.4*cm))
    story.extend(bullets([
        'Lance o conteúdo no mesmo dia ou no dia imediatamente seguinte à aula, evitando o acúmulo de pendências.',
        'Seja específico e detalhado na descrição do conteúdo — o diário é um documento pedagógico oficial.',
        'Verifique a data antes de salvar; datas incorretas geram registros indevidos.',
        'Consulte o Relatório de Pendências ao menos uma vez por semana.',
        'Não compartilhe sua senha com outros usuários — cada ação no sistema fica registrada em seu nome.',
        'Em caso de lançamento incorreto, utilize a opção Editar antes de recorrer à exclusão.',
    ]))
    story.append(linha_divisoria())

    # ── 10. FAQ ───────────────────────────
    story.append(cabecalho_secao('10', 'Perguntas Frequentes'))
    story.append(Spacer(1, 0.4*cm))

    faqs = [
        ('Esqueci minha senha. O que devo fazer?',
         'Entre em contato com a secretaria ou coordenação pedagógica para solicitar a '
         'redefinição da senha de acesso.'),
        ('Minha turma ou disciplina não aparece no formulário. Por quê?',
         'As turmas e disciplinas exibidas são baseadas exclusivamente na grade horária '
         'cadastrada no sistema. Se houver ausência, comunique à coordenação para '
         'verificação e correção.'),
        ('Posso registrar conteúdo de datas passadas?',
         'Sim. O sistema lista todas as datas do ano letivo, inclusive as anteriores à '
         'data atual, permitindo o preenchimento retroativo de pendências.'),
        ('O que acontece se tentar salvar o formulário incompleto?',
         'O sistema exibirá uma mensagem indicando os campos obrigatórios não preenchidos. '
         'O registro só é gravado após o preenchimento completo.'),
        ('É possível lançar o mesmo conteúdo para mais de uma turma ao mesmo tempo?',
         'Sim. Ao selecionar a turma principal, o sistema exibe automaticamente as demais '
         'turmas da mesma série em que o professor leciona. Basta marcá-las antes de salvar.'),
        ('O sistema funciona em celular ou tablet?',
         'Sim. O sistema é acessível por qualquer dispositivo com navegador atualizado e '
         'conexão com a internet.'),
    ]

    for pergunta, resposta in faqs:
        story.append(KeepTogether([
            Paragraph(f'<b>P: {pergunta}</b>', ST['corpo_bold']),
            Paragraph(f'<b>R:</b> {resposta}', ST['corpo']),
            Spacer(1, 0.2*cm),
        ]))

    story.append(linha_divisoria())

    # Rodapé final
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        f'Documento de uso interno. Qualquer dificuldade técnica, entre em '
        f'contato com a coordenação pedagógica.<br/>'
        f'Acesso ao sistema: <b>{URL_SISTEMA}</b>',
        ST['nota']
    ))

    return story


# ──────────────────────────────────────────
# MONTAGEM DO DOCUMENTO
# ──────────────────────────────────────────

def gerar_pdf():
    doc = BaseDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN + 0.5*cm,
        bottomMargin=MARGIN,
    )

    doc.addPageTemplates([
        PageTemplate(id='capa', frames=[capa_frame()], onPage=on_capa),
        PageTemplate(id='normal', frames=[corpo_frame()], onPage=on_normal),
    ])

    story = build_content()
    doc.build(story)
    print(f'[OK] PDF gerado com sucesso: {OUTPUT_PDF}')


if __name__ == '__main__':
    gerar_pdf()

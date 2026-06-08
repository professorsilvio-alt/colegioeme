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
@login_required
def gerenciar_sugestoes(request):
    """Standalone page for administrators to manage content suggestions."""
    prof = get_professor(request.user)
    
    # Permission check: Admin, Diretor or superuser without profile
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')
    
    filtro_disciplina = request.GET.get('disciplina', '')
    filtro_turma = request.GET.get('turma', '')
    filtro_aplicado = bool(filtro_disciplina or filtro_turma)

    # Só carrega os dados do banco quando pelo menos um filtro foi aplicado.
    # Isso evita carregar milhares de sugestões desnecessariamente na abertura da página.
    if filtro_aplicado:
        qs = SugestaoConteudo.objects.all().select_related('disciplina').prefetch_related('turmas').order_by('disciplina__nome', 'texto')
        if filtro_disciplina:
            qs = qs.filter(disciplina_id=filtro_disciplina)
        if filtro_turma:
            qs = qs.filter(turmas__id=filtro_turma)
            qs = qs.distinct()  # evita duplicatas por ManyToMany
    else:
        qs = SugestaoConteudo.objects.none()

    context = {
        'prof': prof,
        'sugestoes': qs,
        'filtro_aplicado': filtro_aplicado,
        'disciplinas': Disciplina.objects.all().order_by('nome'),
        'turmas': Turma.objects.all().order_by('ordem_exibicao', 'codigo'),
        'filtro_disciplina': filtro_disciplina,
        'filtro_turma': filtro_turma,
    }
    return render(request, 'core/gerenciar_sugestoes.html', context)


@login_required
def sugestao_editar(request, pk):
    sug = get_object_or_404(SugestaoConteudo, pk=pk)
    prof = get_professor(request.user)
    
    # Permission check
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')
            
    if request.method == 'POST':
        texto = request.POST.get('texto')
        disc_id = request.POST.get('disciplina')
        turmas_ids = request.POST.getlist('turmas')
        
        if texto and disc_id:
            sug.texto = texto
            sug.disciplina = get_object_or_404(Disciplina, pk=disc_id)
            sug.save()
            
            if turmas_ids:
                sug.turmas.set(turmas_ids)
            else:
                sug.turmas.clear()
                
            messages.success(request, "Sugestão atualizada com sucesso.")
        else:
            messages.error(request, "Texto e disciplina são obrigatórios.")
            
    return redirect('gerenciar_sugestoes')


@login_required
@require_POST
def sugestao_excluir(request, pk):
    sug = get_object_or_404(SugestaoConteudo, pk=pk)
    prof = get_professor(request.user)
    
    # Permission check
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')
            
    sug.delete()
    messages.success(request, "Sugestão excluída com sucesso.")
    return redirect('gerenciar_sugestoes')


@login_required
@require_POST
def sugestoes_acoes_massa(request):
    sugestoes_ids = request.POST.getlist('sugestao_id')
    acao = request.POST.get('acao')

    if not sugestoes_ids:
        messages.error(request, "Nenhuma sugestão selecionada.")
        return redirect('gerenciar_sugestoes')

    prof = get_professor(request.user)
    if not request.user.is_superuser:
        if not prof or not prof.pode_editar_tudo:
            messages.error(request, "Acesso restrito.")
            return redirect('dashboard')

    sugestoes = SugestaoConteudo.objects.filter(pk__in=sugestoes_ids)

    if acao == 'excluir':
        count = sugestoes.count()
        sugestoes.delete()
        messages.success(request, f"{count} sugestões excluídas com sucesso.")
    
    elif acao == 'editar':
        disc_id = request.POST.get('disciplina')
        turmas_ids = request.POST.getlist('turmas')
        
        if not disc_id:
            messages.error(request, "Para edição em massa, é necessário informar a nova disciplina.")
            return redirect('gerenciar_sugestoes')
            
        disciplina = get_object_or_404(Disciplina, pk=disc_id)
        
        for sug in sugestoes:
            sug.disciplina = disciplina
            sug.save()
            if turmas_ids:
                sug.turmas.set(turmas_ids)
            else:
                sug.turmas.clear()
                
        messages.success(request, f"{sugestoes.count()} sugestões foram atualizadas com sucesso.")
        
    return redirect('gerenciar_sugestoes')


@login_required
def sugestao_criar_massa(request):
    prof = get_professor(request.user)
    if not prof or not prof.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    if request.method == 'POST':
        discs_ids = request.POST.getlist('disciplinas')
        turmas_ids = request.POST.getlist('turmas')
        file_obj = request.FILES.get('arquivo_excel')

        if not discs_ids or not turmas_ids or not file_obj:
            messages.error(request, 'Selecione pelo menos uma disciplina, turmas e o arquivo Excel.')
            return redirect('dashboard')

        # Validação de tipo e tamanho do arquivo (#9)
        MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
        EXTENSOES_PERMITIDAS = ('.csv', '.xlsx', '.xls')
        nome_arquivo = file_obj.name.lower()
        if not nome_arquivo.endswith(EXTENSOES_PERMITIDAS):
            messages.error(request, f'Tipo de arquivo não permitido. Use: {", ".join(EXTENSOES_PERMITIDAS)}')
            return redirect('dashboard')
        if file_obj.size > MAX_UPLOAD_SIZE:
            messages.error(request, f'Arquivo muito grande (máximo {MAX_UPLOAD_SIZE // (1024*1024)} MB).')
            return redirect('dashboard')

        try:
            import openpyxl
        except ImportError:
            # Check if it's a CSV file, which doesn't need openpyxl
            if file_obj.name.lower().endswith('.csv'):
                pass # Will handle below
            else:
                debug_info = f" (Python: {sys.version.split()[0]}, Path: {sys.path[:3]})"
                messages.error(request, f'O servidor não possui "openpyxl" para arquivos Excel. Use um arquivo .CSV ou peça suporte. {debug_info}')
                return redirect('dashboard')

        try:
            textos = []
            
            if file_obj.name.lower().endswith('.csv'):
                # Handle CSV
                content = file_obj.read().decode('utf-8-sig')
                io_string = io.StringIO(content)
                reader = csv.reader(io_string, delimiter=';') # Try semicolon first (common in Excel CSV)
                
                # Check if it looks like comma delimited instead
                first_row = next(reader, None)
                if first_row and len(first_row) == 1 and ',' in first_row[0]:
                    io_string.seek(0)
                    reader = csv.reader(io_string, delimiter=',')
                else:
                    # Reset if semicolon worked
                    io_string.seek(0)
                    reader = csv.reader(io_string, delimiter=';')

                for row in reader:
                    if row and str(row[0]).strip():
                        textos.append(str(row[0]).strip())
            else:
                # Handle Excel
                workbook = openpyxl.load_workbook(file_obj, data_only=True)
                sheet = workbook.active
                for row in sheet.iter_rows(min_row=1, max_col=1, values_only=True):
                    val = row[0]
                    if val and str(val).strip():
                        textos.append(str(val).strip())
            
            if not textos:
                messages.warning(request, 'Nenhum conteúdo encontrado na primeira coluna da planilha.')
                return redirect('dashboard')

            disciplinas = Disciplina.objects.filter(pk__in=discs_ids)
            turmas = Turma.objects.filter(pk__in=turmas_ids)
            
            from django.db import transaction
            with transaction.atomic():
                # Opcional: Evitar duplicidade exata na mesma disc/turma?
                # Por agora, cria direto seguindo o pedido anterior.
                for txt in textos:
                    for disciplina in disciplinas:
                        sug = SugestaoConteudo.objects.create(disciplina=disciplina, texto=txt)
                        sug.turmas.set(turmas)

            total_criado = len(textos) * disciplinas.count()
            messages.success(request, f'{total_criado} sugestões cadastradas com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao processar Excel: {str(e)}')
            
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def migrar_alunos(request):
    """Ferramenta para migrar (copiar) alunos de um ano letivo para outro."""
    prof = get_professor(request.user)
    if not prof or not prof.pode_editar_tudo:
        messages.error(request, "Acesso restrito à administração e direção.")
        return redirect('dashboard')
    
    anos = AnoLetivo.objects.all()
    turmas_origem = []
    alunos = []
    turmas_destino = []
    
    ano_origem_id = request.GET.get('ano_origem')
    turma_origem_id = request.GET.get('turma_origem')
    ano_destino_id = request.GET.get('ano_destino')
    
    if ano_origem_id:
        turmas_origem = Turma.objects.filter(ano_letivo_id=ano_origem_id, escola=request.escola)
        
    if turma_origem_id:
        alunos = Aluno.objects.filter(turma_id=turma_origem_id)
        
    if ano_destino_id:
        turmas_destino = Turma.objects.filter(ano_letivo_id=ano_destino_id, escola=request.escola)

    if request.method == 'POST':
        aluno_ids = request.POST.getlist('alunos_migrar')
        turma_dest_id = request.POST.get('turma_destino')
        
        if not aluno_ids or not turma_dest_id:
            messages.error(request, "Selecione os alunos e a turma de destino.")
        else:
            t_dest = get_object_or_404(Turma, pk=turma_dest_id)
            sucesso = 0
            for a_id in aluno_ids:
                try:
                    a_origem = Aluno.objects.get(pk=a_id)
                    # Cria um NOVO registro de aluno vinculado à turma de destino
                    # Preserva os dados básicos e a foto
                    Aluno.objects.create(
                        nome=a_origem.nome,
                        turma=t_dest,
                        email_responsavel=a_origem.email_responsavel,
                        foto=a_origem.foto
                    )
                    sucesso += 1
                except Aluno.DoesNotExist:
                    continue
            
            messages.success(request, f"Migração concluída: {sucesso} alunos copiados para {t_dest}.")
            return redirect('migrar_alunos')

    context = {
        'anos': anos,
        'turmas_origem': turmas_origem,
        'turmas_destino': turmas_destino,
        'alunos': alunos,
        'ano_origem_id': int(ano_origem_id) if ano_origem_id else None,
        'turma_origem_id': int(turma_origem_id) if turma_origem_id else None,
        'ano_destino_id': int(ano_destino_id) if ano_destino_id else None,
    }
    return render(request, 'core/migrar_alunos.html', context)
@login_required
def escola_configurar(request):
    """Permite ao administrador da escola alterar as cores e logo."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')

    from ..forms import EscolaForm
    escola = request.escola

    if request.method == 'POST':
        form = EscolaForm(request.POST, request.FILES, instance=escola)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações da escola atualizadas com sucesso!')
            return redirect('escola_configurar')
    else:
        form = EscolaForm(instance=escola)

    return render(request, 'core/escola_configurar.html', {
        'form': form,
        'escola': escola
    })


@login_required
def escola_professores_list(request):
    """Lista professores da escola atual."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    professores = Professor.objects.filter(escolas=request.escola).order_by('nome')
    return render(request, 'core/escola_professores_list.html', {
        'professores': professores
    })


@login_required
def escola_professor_edit(request, pk):
    """Edita um professor (vínculo com a escola atual)."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    professor = get_object_or_404(Professor, pk=pk, escolas=request.escola)
    from ..forms import ProfessorForm
    
    if request.method == 'POST':
        form = ProfessorForm(request.POST, instance=professor, escola=request.escola)
        if form.is_valid():
            # Precisamos manter as turmas de OUTRAS escolas
            # O CheckboxSelectMultiple filtrado remove as outras
            outras_turmas = list(professor.turmas.exclude(escola=request.escola))
            professor = form.save(commit=False)
            professor.save()
            form.save_m2m() # Salva as turmas da escola atual
            
            # Re-adiciona as outras
            for t in outras_turmas:
                professor.turmas.add(t)
                
            messages.success(request, f'Professor {professor.nome} atualizado!')
            return redirect('escola_professores_list')
    else:
        form = ProfessorForm(instance=professor, escola=request.escola)
        
    return render(request, 'core/escola_professor_form.html', {
        'form': form,
        'professor': professor,
        'titulo': f'Editar: {professor.nome}'
    })


@login_required
def escola_professor_novo(request):
    """Cria um novo professor e seu respectivo User."""
    prof_atual = get_professor(request.user)
    if not prof_atual or not prof_atual.pode_editar_tudo:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    from ..forms import ProfessorForm
    from django.contrib.auth.models import User
    
    if request.method == 'POST':
        form = ProfessorForm(request.POST, escola=request.escola)
        usuario_login = request.POST.get('username_login')
        
        if form.is_valid() and usuario_login:
            if User.objects.filter(username=usuario_login).exists():
                messages.error(request, 'Este nome de usuário já está em uso.')
            else:
                # 1. Cria o User
                # Senha temporária aleatória segura (força troca no primeiro login)
                import secrets
                import string
                senha_temp = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                user = User.objects.create_user(username=usuario_login, password=senha_temp)
                
                # 2. Cria o Professor
                professor = form.save(commit=False)
                professor.user = user
                professor.deve_trocar_senha = True # Força troca no primeiro login
                professor.save()
                form.save_m2m()
                
                # 3. Vincula à escola atual
                professor.escolas.add(request.escola)
                
                messages.success(request, f'Professor {professor.nome} criado com sucesso!')
                logger.info('PROFESSOR CRIADO: %s (user=%s) por %s', professor.nome, usuario_login, request.user.username)
                return render(request, 'core/professor_criado.html', {
                    'professor': professor,
                    'usuario_login': usuario_login,
                    'senha_temp': senha_temp,
                })
    else:
        form = ProfessorForm(escola=request.escola)
        
    return render(request, 'core/escola_professor_form.html', {
        'form': form,
        'titulo': 'Cadastrar Novo Professor',
        'novo': True
    })

import sys
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db import transaction

from ..models import AulaExtraProgramada, Disciplina, Professor, Turma
from ..utils import get_professor


@login_required
def upload_aulas_extras(request):
    prof = get_professor(request.user)
    if not prof or not prof.pode_editar_tudo:
        messages.error(request, 'Acesso restrito à administração e direção.')
        return redirect('dashboard')

    if request.method == 'POST':
        file_obj = request.FILES.get('arquivo_excel')
        if not file_obj:
            messages.error(request, 'Por favor, selecione um arquivo.')
            return redirect('upload_aulas_extras')

        MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
        if file_obj.size > MAX_UPLOAD_SIZE:
            messages.error(request, f'Arquivo muito grande (máximo {MAX_UPLOAD_SIZE // (1024*1024)} MB).')
            return redirect('upload_aulas_extras')

        if not file_obj.name.lower().endswith('.xlsx'):
            messages.error(request, 'Formato de arquivo inválido. Use um arquivo Excel (.xlsx).')
            return redirect('upload_aulas_extras')

        try:
            import openpyxl
        except ImportError:
            messages.error(request, 'A biblioteca openpyxl não está instalada no servidor.')
            return redirect('upload_aulas_extras')

        try:
            workbook = openpyxl.load_workbook(file_obj, data_only=True)
            sheet = workbook.active
            
            sucesso = 0
            erros = []
            
            # Assume header in first row: Data | Horario | Turma | Disciplina | Professor
            # Horario might be ignored since pendencies are daily, but we parse it.
            
            with transaction.atomic():
                for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    # Check if row is mostly empty
                    if not any(row):
                        continue
                        
                    # Extract columns assuming specific order
                    # 0: Data, 1: Horario, 2: Turma, 3: Disciplina, 4: Professor
                    if len(row) < 5:
                        erros.append(f"Linha {i}: Colunas insuficientes.")
                        continue
                        
                    val_data = row[0]
                    val_horario = row[1]
                    val_turma = row[2]
                    val_disc = row[3]
                    val_prof = row[4]
                    
                    if not all([val_data, val_turma, val_disc, val_prof]):
                        erros.append(f"Linha {i}: Campos em branco.")
                        continue

                    # Parse Date
                    data_aula = None
                    if isinstance(val_data, datetime.datetime):
                        data_aula = val_data.date()
                    else:
                        try:
                            # Assume DD/MM/YYYY or YYYY-MM-DD
                            val_data_str = str(val_data).strip()
                            if '/' in val_data_str:
                                d, m, y = val_data_str.split('/')
                                data_aula = datetime.date(int(y), int(m), int(d))
                            else:
                                data_aula = datetime.date.fromisoformat(val_data_str[:10])
                        except Exception:
                            erros.append(f"Linha {i}: Data inválida '{val_data}'.")
                            continue
                            
                    # Match Turma
                    turma = Turma.objects.filter(codigo__iexact=str(val_turma).strip(), ano_letivo=request.ano_letivo, escola=request.escola).first()
                    if not turma:
                        erros.append(f"Linha {i}: Turma '{val_turma}' não encontrada no ano/escola atual.")
                        continue
                        
                    # Match Disciplina
                    disciplina = Disciplina.objects.filter(nome__iexact=str(val_disc).strip()).first()
                    if not disciplina:
                        erros.append(f"Linha {i}: Disciplina '{val_disc}' não encontrada.")
                        continue
                        
                    # Match Professor
                    professor = Professor.objects.filter(nome__iexact=str(val_prof).strip()).first()
                    if not professor:
                        # Try partial match if exact match fails
                        professores = Professor.objects.filter(nome__icontains=str(val_prof).strip())
                        if professores.count() == 1:
                            professor = professores.first()
                        else:
                            erros.append(f"Linha {i}: Professor '{val_prof}' não encontrado de forma única.")
                            continue

                    # Save record
                    obj, created = AulaExtraProgramada.objects.get_or_create(
                        data=data_aula,
                        turma=turma,
                        disciplina=disciplina,
                        professor=professor
                    )
                    if created:
                        sucesso += 1

            if sucesso > 0:
                messages.success(request, f"{sucesso} aulas extras programadas com sucesso!")
            if erros:
                for erro in erros[:10]: # Limita os erros exibidos
                    messages.warning(request, erro)
                if len(erros) > 10:
                    messages.warning(request, f"... e mais {len(erros) - 10} erros.")
                    
            return redirect('upload_aulas_extras')

        except Exception as e:
            messages.error(request, f'Erro ao processar planilha: {str(e)}')
            return redirect('upload_aulas_extras')

    return render(request, 'core/upload_aulas_extras.html')

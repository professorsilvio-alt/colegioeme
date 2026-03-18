from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.html import format_html
from django.contrib import messages
from .models import Turma, Disciplina, Professor, Aluno, Ocorrencia, ConteudoProgramatico, GradeHoraria, InspetorProxy, ProfessorDocente, SugestaoConteudo
import datetime


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'grade_semanal_link']
    search_fields = ['codigo']

    def grade_semanal_link(self, obj):
        return format_html(
            '<a class="button" href="{}/grade-semanal/">Ver Grade Semanal</a>',
            obj.pk
        )
    grade_semanal_link.short_description = 'Grade Semanal'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/grade-semanal/',
                self.admin_site.admin_view(self.grade_semanal_view),
                name='turma-grade-semanal',
            ),
        ]
        return custom_urls + urls

    def grade_semanal_view(self, request, object_id, *args, **kwargs):
        turma = get_object_or_404(Turma, pk=object_id)
        
        # Fixed slots from mon to fri
        dias_semana = GradeHoraria.DIA_CHOICES
        # We need to construct expected time slots. For simplification based on current DB:
        slots_db = GradeHoraria.objects.filter(turma=turma).values_list('hora_inicio', 'hora_fim').distinct().order_by('hora_inicio')
        
        if not slots_db:
            # Fallback typical slots if empty
            slots = [
                {'inicio': '07:00:00', 'fim': '07:45:00'},
                {'inicio': '07:30:00', 'fim': '08:15:00'},
                {'inicio': '07:45:00', 'fim': '08:30:00'},
                {'inicio': '08:15:00', 'fim': '09:00:00'},
                {'inicio': '08:30:00', 'fim': '09:15:00'},
                {'inicio': '09:00:00', 'fim': '09:45:00'},
                {'inicio': '09:30:00', 'fim': '10:15:00'},
                {'inicio': '09:45:00', 'fim': '10:30:00'},
                {'inicio': '10:15:00', 'fim': '11:00:00'},
                {'inicio': '11:00:00', 'fim': '11:45:00'},
                {'inicio': '11:45:00', 'fim': '12:30:00'},
                {'inicio': '12:00:00', 'fim': '12:45:00'},
                {'inicio': '13:00:00', 'fim': '13:45:00'}
            ]
        else:
            slots = [{'inicio': s[0].strftime('%H:%M:%S'), 'fim': s[1].strftime('%H:%M:%S')} for s in slots_db]

        if request.method == 'POST':
            # Handle save
            professores_afetados = set()
            
            # Since rows are dynamic count, we check the length of slots we passed or look for inputs
            # Actually we know how many slots were shown on GET by looking at "slot_X_ini"
            slot_indices = set()
            for key in request.POST:
                if key.startswith('slot_') and key.endswith('_ini'):
                    parts = key.split('_')
                    if len(parts) == 3:
                        slot_indices.add(parts[1])
            
            for idx in sorted(list(slot_indices), key=int):
                inicio_str = request.POST.get(f'slot_{idx}_ini')
                fim_str = request.POST.get(f'slot_{idx}_fim')
                
                # If these are empty, skip row
                if not inicio_str or not fim_str:
                    continue
                
                # We format strict times to HH:MM:00 for the database
                if len(inicio_str) == 5: inicio_str += ':00'
                if len(fim_str) == 5: fim_str += ':00'

                for dia_id, _ in dias_semana:
                    disc_id = request.POST.get(f"disciplina_{dia_id}_{idx}")
                    prof_id = request.POST.get(f"professor_{dia_id}_{idx}")

                    # Since time might have changed from what was in DB for this specific 'slot index', 
                    # we should probably just treat it as an update if an old record existed at the same dia/turma 
                    # But the easiest approach given the model is to find by (turma, dia, start_time) 
                    # wait, if they change the start_time, we might orphan the old one. 
                    # Better approach: when regenerating the form, we should pass the original start time as hidden, 
                    # but since the UI row is just a "slot", we can just query the exact start_time they submit.
                    # Wait, if they *change* a slot time, the old one won't be matched and might stay if we just create new.
                    # Given the UI structure, it's safer to clear all for this turma and recreate from the submitted grid
                    # to make sure deleted slots or time changes are fully flushed.
                    pass
            
            # A cleaner approach since we submit the whole week schedule:
            # 1. Gather all current professors for this turma to update them later
            todas_antigas = GradeHoraria.objects.filter(turma=turma)
            professores_afetados.update(list(Professor.objects.filter(grade_horaria__in=todas_antigas)))
            
            # 2. Delete all existing schedule for this turma
            todas_antigas.delete()

            # 3. Recreate based on form data
            for idx in sorted(list(slot_indices), key=int):
                inicio_str = request.POST.get(f'slot_{idx}_ini')
                fim_str = request.POST.get(f'slot_{idx}_fim')
                
                if not inicio_str or not fim_str:
                    continue
                
                if len(inicio_str) == 5: inicio_str += ':00'
                if len(fim_str) == 5: fim_str += ':00'

                for dia_id, _ in dias_semana:
                    disc_id = request.POST.get(f"disciplina_{dia_id}_{idx}")
                    prof_id = request.POST.get(f"professor_{dia_id}_{idx}")

                    if disc_id and prof_id:
                        nova = GradeHoraria.objects.create(
                            turma=turma,
                            dia_semana=dia_id,
                            hora_inicio=inicio_str,
                            hora_fim=fim_str,
                            disciplina_id=disc_id,
                            professor_id=prof_id
                        )
                        professores_afetados.add(nova.professor)
            
            # Sync profiles for affected
            for p in professores_afetados:
                # remove old and re-add all current
                p.turmas.clear()
                p.disciplinas.clear()
                aulas_prof = GradeHoraria.objects.filter(professor=p).select_related('turma', 'disciplina')
                for a in aulas_prof:
                    p.turmas.add(a.turma)
                    p.disciplinas.add(a.disciplina)

            self.message_user(request, "Grade semanal atualizada com sucesso!", messages.SUCCESS)
            return redirect(request.path)

        # GET
        disciplinas = Disciplina.objects.all().order_by('nome')
        professores = Professor.objects.all().order_by('nome')
        # Ensure that no matter what, we just order it alphabetically, it is already via Meta ordering mostly,
        # but the explicit order_by('nome') ensures it.

        grade_atual = GradeHoraria.objects.filter(turma=turma).order_by('hora_inicio')

        grade_dict = {}
        for dia_id, _ in dias_semana:
            grade_dict[str(dia_id)] = {}
        
        # Populate the dictionary
        for g in grade_atual:
            hi = g.hora_inicio.strftime('%H:%M:%S')
            # For template matching, since input type="time" defaults to HH:MM if 00 seconds
            hi_short = g.hora_inicio.strftime('%H:%M') 
            
            dia_str = str(g.dia_semana)
            if dia_str not in grade_dict:
                grade_dict[dia_str] = {}

            grade_dict[dia_str][hi] = {
                'disciplina_id': g.disciplina_id,
                'professor_id': g.professor_id
            }
            grade_dict[dia_str][hi_short] = {
                'disciplina_id': g.disciplina_id,
                'professor_id': g.professor_id
            }

        cod = turma.codigo
        # Define the expected full schedule template including breaks
        # We use a special flag `is_break` to render it differently
        if any(cod.startswith(p) for p in ['61','62','63','71','72','73']):
            expected_slots = [
                {'inicio': '07:00:00', 'fim': '07:45:00', 'is_break': False},
                {'inicio': '07:45:00', 'fim': '08:30:00', 'is_break': False},
                {'inicio': '08:30:00', 'fim': '09:00:00', 'is_break': True},
                {'inicio': '09:00:00', 'fim': '09:45:00', 'is_break': False}, 
                {'inicio': '09:45:00', 'fim': '10:30:00', 'is_break': False},
                {'inicio': '10:30:00', 'fim': '11:15:00', 'is_break': False},
                {'inicio': '11:15:00', 'fim': '12:00:00', 'is_break': False}
            ]
        elif any(cod.startswith(p) for p in ['21','22','23','31','32']):
            expected_slots = [
                {'inicio': '07:30:00', 'fim': '08:15:00', 'is_break': False},
                {'inicio': '08:15:00', 'fim': '09:00:00', 'is_break': False},
                {'inicio': '09:00:00', 'fim': '09:45:00', 'is_break': True},
                {'inicio': '09:45:00', 'fim': '10:30:00', 'is_break': False}, 
                {'inicio': '10:30:00', 'fim': '11:15:00', 'is_break': False},
                {'inicio': '11:15:00', 'fim': '12:00:00', 'is_break': False},
                {'inicio': '12:00:00', 'fim': '12:45:00', 'is_break': False}
            ]
        elif any(cod.startswith(p) for p in ['11','12','13']):
            expected_slots = [
                {'inicio': '07:30:00', 'fim': '08:15:00', 'is_break': False},
                {'inicio': '08:15:00', 'fim': '09:00:00', 'is_break': False},
                {'inicio': '09:00:00', 'fim': '09:45:00', 'is_break': False},
                {'inicio': '09:45:00', 'fim': '10:15:00', 'is_break': True},
                {'inicio': '10:15:00', 'fim': '11:00:00', 'is_break': False}, 
                {'inicio': '11:00:00', 'fim': '11:45:00', 'is_break': False},
                {'inicio': '11:45:00', 'fim': '12:30:00', 'is_break': False}
            ]
        elif any(cod.startswith(p) for p in ['81','82','91','92','93']):
            expected_slots = [
                {'inicio': '07:30:00', 'fim': '08:15:00', 'is_break': False},
                {'inicio': '08:15:00', 'fim': '09:00:00', 'is_break': False},
                {'inicio': '09:00:00', 'fim': '09:45:00', 'is_break': False},
                {'inicio': '09:45:00', 'fim': '10:30:00', 'is_break': False},
                {'inicio': '10:30:00', 'fim': '11:00:00', 'is_break': True},
                {'inicio': '11:00:00', 'fim': '11:45:00', 'is_break': False}, 
                {'inicio': '11:45:00', 'fim': '12:30:00', 'is_break': False}
            ]
        else:
            # Generic fallback
            expected_slots = [
                {'inicio': '07:30:00', 'fim': '08:15:00', 'is_break': False},
                {'inicio': '08:15:00', 'fim': '09:00:00', 'is_break': False},
                {'inicio': '09:00:00', 'fim': '09:45:00', 'is_break': False},
                {'inicio': '09:45:00', 'fim': '10:00:00', 'is_break': True},
                {'inicio': '10:00:00', 'fim': '10:45:00', 'is_break': False},
                {'inicio': '10:45:00', 'fim': '11:30:00', 'is_break': False}
            ]

        # Always combine DB existing slots with the expected breaks if DB slots exist, 
        # Actually, if we have expected slots for this turma, we should ALWAYS show all of them
        # so that missing classes can be added even if not in DB yet.
        slots_db = list(grade_atual.values('hora_inicio', 'hora_fim').distinct().order_by('hora_inicio'))
        
        db_slots_parsed = {
            s['hora_inicio'].strftime('%H:%M'): s['hora_fim'].strftime('%H:%M')
            for s in slots_db
        }
        
        slots = []
        for s in expected_slots:
            slots.append({
                'inicio': s['inicio'][:5], 
                'inicio_short': s['inicio'][:5],
                'fim': s['fim'][:5], 
                'is_break': s['is_break']
            })
            
        # Also include any DB slots that somehow aren't in expected_slots
        expected_starts = {s['inicio'][:5] for s in expected_slots}
        for inicio, fim in db_slots_parsed.items():
            if inicio not in expected_starts:
                slots.append({
                    'inicio': inicio,
                    'inicio_short': inicio,
                    'fim': fim,
                    'is_break': False
                })
                
        # Sort all slots by start time to maintain timeline order
        slots = sorted(slots, key=lambda x: x['inicio'])

        context = {
            **self.admin_site.each_context(request),
            'title': f'Grade Semanal: {turma.codigo}',
            'turma': turma,
            'dias_semana': dias_semana,
            'slots': slots,
            'disciplinas': disciplinas,
            'professores': professores,
            'grade_dict': grade_dict,
        }
        
        return render(request, "admin/core/turma/grade_semanal.html", context)


class SugestaoConteudoInline(admin.TabularInline):
    model = SugestaoConteudo
    extra = 1

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    inlines = [SugestaoConteudoInline]


@admin.register(SugestaoConteudo)
class SugestaoConteudoAdmin(admin.ModelAdmin):
    list_display = ['disciplina', 'texto_curto', 'ordem']
    list_filter = ['disciplina', 'turmas']
    filter_horizontal = ['turmas']
    search_fields = ['texto']

    def texto_curto(self, obj):
        return obj.texto[:100]
    texto_curto.short_description = 'Conteúdo'


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo_badge', 'cpf', 'todas_turmas', 'todas_disciplinas']
    list_filter = ['cargo']
    search_fields = ['nome', 'cpf']
    ordering = ['cargo', 'nome']
    filter_horizontal = ['turmas', 'turmas_inspetor', 'disciplinas']
    fieldsets = [
        ('Dados Pessoais', {
            'fields': ['user', 'nome', 'cpf', 'cargo']
        }),
        ('Permissões', {
            'fields': ['todas_turmas', 'todas_disciplinas']
        }),
        ('Turmas e Disciplinas (Professores)', {
            'fields': ['turmas', 'disciplinas'],
            'classes': ['collapse'],
        }),
        ('Turmas de Responsabilidade (Inspetor)', {
            'fields': ['turmas_inspetor'],
            'classes': ['collapse'],
            'description': 'Apenas para inspetores. As ocorrências dessas turmas serão visíveis para este inspetor.',
        }),
    ]

    CARGO_COLORS = {
        'ADMIN':       '#6c757d',
        'DIRETOR':     '#0055aa',
        'COORDENADOR': '#0077cc',
        'AUX_COORD':   '#5ba4cf',
        'ORIENTADOR':  '#8e44ad',
        'SECRETARIA':  '#16a085',
        'PROFESSOR':   '#27ae60',
        'INSPETOR':    '#e67e22',
    }

    def cargo_badge(self, obj):
        color = self.CARGO_COLORS.get(obj.cargo, '#999')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">{}</span>',
            color, obj.get_cargo_display()
        )
    cargo_badge.short_description = 'Cargo'
    cargo_badge.admin_order_field = 'cargo'



@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'turma', 'email_responsavel']
    list_filter = ['turma']
    search_fields = ['nome', 'email_responsavel']
    fields = ['nome', 'turma', 'email_responsavel']


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'data', 'turma', 'professor', 'disciplina', 'status']
    list_filter = ['status', 'turma', 'professor', 'disciplina']
    filter_horizontal = ['alunos']
    date_hierarchy = 'data'


@admin.register(ConteudoProgramatico)
class ConteudoAdmin(admin.ModelAdmin):
    list_display = ['data', 'professor', 'disciplina', 'descricao']
    list_filter = ['turmas', 'professor', 'disciplina']
    filter_horizontal = ['turmas']
    date_hierarchy = 'data'


@admin.register(GradeHoraria)
class GradeHorariaAdmin(admin.ModelAdmin):
    list_display = ['dia_semana', 'hora_inicio', 'turma', 'disciplina', 'professor']
    list_filter = ['dia_semana', 'turma', 'professor']

@admin.register(InspetorProxy)
class InspetorProxyAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'turmas_responsaveis']
    search_fields = ['nome', 'cpf']
    filter_horizontal = ['turmas_inspetor']
    fieldsets = [
        ('Dados Pessoais', {'fields': ['user', 'nome', 'cpf']}),
        ('Turmas de Responsabilidade', {
            'fields': ['turmas_inspetor'],
            'description': 'As ocorrências dessas turmas serão visíveis para este inspetor.',
        }),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(cargo='INSPETOR')

    def turmas_responsaveis(self, obj):
        codigos = ', '.join(obj.turmas_inspetor.values_list('codigo', flat=True).order_by('codigo'))
        return codigos or '—'
    turmas_responsaveis.short_description = 'Turmas (Responsabilidade)'

    def save_model(self, request, obj, form, change):
        obj.cargo = 'INSPETOR'
        super().save_model(request, obj, form, change)


@admin.register(ProfessorDocente)
class ProfessorDocenteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'disciplinas_lista', 'turmas_lista']
    search_fields = ['nome', 'cpf']
    filter_horizontal = ['turmas', 'disciplinas']
    fieldsets = [
        ('Dados Pessoais', {'fields': ['user', 'nome', 'cpf']}),
        ('Turmas e Disciplinas', {
            'fields': ['turmas', 'disciplinas', 'todas_turmas', 'todas_disciplinas'],
        }),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(cargo='PROFESSOR')

    def disciplinas_lista(self, obj):
        nomes = ', '.join(obj.disciplinas.values_list('nome', flat=True).order_by('nome'))
        return nomes or '—'
    disciplinas_lista.short_description = 'Disciplinas'

    def turmas_lista(self, obj):
        codigos = ', '.join(obj.turmas.values_list('codigo', flat=True).order_by('codigo'))
        return codigos or '—'
    turmas_lista.short_description = 'Turmas'

    def save_model(self, request, obj, form, change):
        obj.cargo = 'PROFESSOR'
        super().save_model(request, obj, form, change)

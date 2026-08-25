from django import forms
from .models import Escola, Professor, Turma, Disciplina, Aluno

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ['nome', 'logo', 'cor_primaria']
        widgets = {
            'cor_primaria': forms.TextInput(attrs={'type': 'color'}),
        }

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['nome', 'cpf', 'cargo', 'email_contato', 'turmas', 'disciplinas', 'todas_turmas', 'todas_disciplinas', 'autorizado_lancar_notas']
        widgets = {
            'turmas': forms.CheckboxSelectMultiple(),
            'disciplinas': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        escola = kwargs.pop('escola', None)
        super().__init__(*args, **kwargs)
        if escola:
            # Filtra turmas apenas da escola atual
            self.fields['turmas'].queryset = Turma.objects.filter(escola=escola)


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'turma', 'email_responsavel', 'telefone_responsavel', 'foto']
        widgets = {
            'nome': forms.TextInput(attrs={'style': 'width: 100%; padding: 9px 12px; border-radius: 6px; border: 1.5px solid #cbd5e1; font-size: 14px;', 'placeholder': 'Nome completo do aluno'}),
            'turma': forms.Select(attrs={'style': 'width: 100%; padding: 9px 12px; border-radius: 6px; border: 1.5px solid #cbd5e1; font-size: 14px; background: #fff;'}),
            'email_responsavel': forms.EmailInput(attrs={'style': 'width: 100%; padding: 9px 12px; border-radius: 6px; border: 1.5px solid #cbd5e1; font-size: 14px;', 'placeholder': 'email@exemplo.com'}),
            'telefone_responsavel': forms.TextInput(attrs={'style': 'width: 100%; padding: 9px 12px; border-radius: 6px; border: 1.5px solid #cbd5e1; font-size: 14px;', 'placeholder': '(21) 99999-9999'}),
            'foto': forms.FileInput(attrs={'style': 'width: 100%; padding: 6px 0; font-size: 13px;'}),
        }

    def __init__(self, *args, **kwargs):
        escola = kwargs.pop('escola', None)
        ano_letivo = kwargs.pop('ano_letivo', None)
        super().__init__(*args, **kwargs)
        if escola and ano_letivo:
            self.fields['turma'].queryset = Turma.objects.filter(escola=escola, ano_letivo=ano_letivo).order_by('ordem_exibicao', 'codigo')
        elif escola:
            self.fields['turma'].queryset = Turma.objects.filter(escola=escola).order_by('ordem_exibicao', 'codigo')


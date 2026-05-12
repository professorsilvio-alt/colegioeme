from django import forms
from .models import Escola, Professor, Turma, Disciplina

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
        fields = ['nome', 'cpf', 'cargo', 'email_contato', 'turmas', 'disciplinas', 'todas_turmas', 'todas_disciplinas']
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

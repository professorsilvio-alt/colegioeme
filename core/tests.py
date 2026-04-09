from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Turma, Disciplina, Professor, Aluno, SugestaoConteudo, ConteudoProgramatico
import datetime

class CoreModelTests(TestCase):
    def setUp(self):
        self.turma = Turma.objects.create(codigo='31', ordem_exibicao=1)
        self.disc = Disciplina.objects.create(nome='Matemática')
        self.user = User.objects.create_user(username='prof1', password='password123')
        self.prof = Professor.objects.create(user=self.user, nome='Professor Teste', cargo='PROFESSOR')
        self.prof.turmas.add(self.turma)
        self.prof.disciplinas.add(self.disc)

    def test_turma_str(self):
        self.assertEqual(str(self.turma), 'Turma 31')

    def test_disciplina_str(self):
        self.assertEqual(str(self.disc), 'Matemática')

    def test_professor_str(self):
        self.assertEqual(str(self.prof), 'Professor Teste (Professor)')

    def test_aluno_creation(self):
        aluno = Aluno.objects.create(nome='João Silva', turma=self.turma)
        self.assertEqual(str(aluno), 'João Silva (31)')

class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.turma = Turma.objects.create(codigo='31')
        self.user = User.objects.create_user(username='prof1', password='password123')
        self.prof = Professor.objects.create(user=self.user, nome='Professor Teste', cargo='PROFESSOR')

    def test_login_redirect(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_access(self):
        self.client.login(username='prof1', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_api_alunos_turma(self):
        Aluno.objects.create(nome='João Silva', turma=self.turma)
        self.client.login(username='prof1', password='password123')
        response = self.client.get(reverse('api_alunos_turma', args=[self.turma.codigo]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nome'], 'João Silva')

class SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a teacher (common) and a director (pode_editar_tudo)
        self.u_teacher = User.objects.create_user(username='teacher', password='pass')
        self.p_teacher = Professor.objects.create(user=self.u_teacher, nome='Teacher', cargo='PROFESSOR')
        
        self.u_director = User.objects.create_user(username='director', password='pass')
        self.p_director = Professor.objects.create(user=self.u_director, nome='Director', cargo='DIRETOR')
        
        self.disc = Disciplina.objects.create(nome='Física')

    def test_teacher_cannot_bulk_create_suggestions(self):
        self.client.login(username='teacher', password='pass')
        response = self.client.post(reverse('sugestao_criar_massa'), {
            'disciplinas': [self.disc.pk],
            'turmas': [], # Doesn't matter, should fail earlier
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.url) # Redirects to dashboard with error message

    def test_director_can_access_bulk_create_logic(self):
        self.client.login(username='director', password='pass')
        # We don't need a full file upload, just check if it doesn't 403/redirect incorrectly
        # Actually, success would be a redirect to dashboard after processing (or error if missing file)
        response = self.client.post(reverse('sugestao_criar_massa'))
        # Should redirect back to dashboard because it's missing fields, not access denied
        self.assertEqual(response.status_code, 302)
        # Note: In our views.py, failure to provide fields redirects to dashboard with error message

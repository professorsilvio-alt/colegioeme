from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Turma, Disciplina, Professor, Aluno, SugestaoConteudo, ConteudoProgramatico, Ocorrencia
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

class DuplicateProtectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.turma = Turma.objects.create(codigo='93')
        self.disc = Disciplina.objects.create(nome='História')
        self.u_prof = User.objects.create_user(username='prof93', password='pass')
        self.prof = Professor.objects.create(user=self.u_prof, nome='Silvio', cargo='PROFESSOR')
        self.prof.turmas.add(self.turma)
        self.prof.disciplinas.add(self.disc)
        self.data = datetime.date(2026, 4, 10)
        
        # Create initial record
        self.cont = ConteudoProgramatico.objects.create(
            data=self.data, professor=self.prof, disciplina=self.disc, descricao='Aula 1'
        )
        self.cont.turmas.add(self.turma)

    def test_skip_resolution(self):
        self.client.login(username='prof93', password='pass')
        # Attempt to create duplicate with 'pular' resolution
        response = self.client.post(reverse('conteudo_criar'), {
            'data': self.data.isoformat(),
            'turmas': ['93'],
            'disciplina': self.disc.id,
            'descricao': 'Aula 1 Duplicate',
            'resolucao_93': 'pular'
        })
        self.assertEqual(ConteudoProgramatico.objects.filter(data=self.data, turmas=self.turma).count(), 1)
        self.assertEqual(ConteudoProgramatico.objects.get(id=self.cont.id).descricao, 'Aula 1')

    def test_merge_resolution(self):
        self.client.login(username='prof93', password='pass')
        # Attempt to create duplicate with 'mesclar' resolution
        response = self.client.post(reverse('conteudo_criar'), {
            'data': self.data.isoformat(),
            'turmas': ['93'],
            'disciplina': self.disc.id,
            'descricao': 'Novo Conteúdo',
            'resolucao_93': 'mesclar'
        })
        self.cont.refresh_from_db()
        self.assertIn('Aula 1', self.cont.descricao)
        self.assertIn('[MESCLADO EM', self.cont.descricao)
        self.assertIn('Novo Conteúdo', self.cont.descricao)
        self.assertEqual(ConteudoProgramatico.objects.filter(data=self.data, turmas=self.turma).count(), 1)


class OcorrenciaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.turma = Turma.objects.create(codigo='82')
        self.aluno1 = Aluno.objects.create(nome='João Silva', turma=self.turma)
        self.aluno2 = Aluno.objects.create(nome='Maria Oliveira', turma=self.turma)
        self.aluno3 = Aluno.objects.create(nome='Pedro Souza', turma=self.turma)
        self.disc = Disciplina.objects.create(nome='Química')
        
        self.u_prof = User.objects.create_user(username='prof82', password='pass')
        self.prof = Professor.objects.create(user=self.u_prof, nome='Marcos', cargo='PROFESSOR')
        self.prof.turmas.add(self.turma)
        self.prof.disciplinas.add(self.disc)
        self.client.login(username='prof82', password='pass')

    def test_criar_ocorrencia_multiplos_alunos_individualizada(self):
        # Envia formulário para criar ocorrência selecionando 3 alunos
        response = self.client.post(reverse('ocorrencia_criar'), {
            'data': '2026-06-15',
            'turma': self.turma.codigo,
            'alunos': [self.aluno1.pk, self.aluno2.pk, self.aluno3.pk],
            'disciplina': self.disc.pk,
            'status': 'Aberta',
            'tipos_ocorrencia': ['Conversando'],
            'descricao_outros': '',
        })
        self.assertEqual(response.status_code, 302)
        
        # Deve ter criado 3 ocorrências diferentes
        ocorrencias = Ocorrencia.objects.filter(turma=self.turma)
        self.assertEqual(ocorrencias.count(), 3)
        
        # Cada ocorrência deve conter exatamente um aluno
        alunos_vinculados = [oc.alunos.first() for oc in ocorrencias]
        self.assertIn(self.aluno1, alunos_vinculados)
        self.assertIn(self.aluno2, alunos_vinculados)
        self.assertIn(self.aluno3, alunos_vinculados)

    def test_filtrar_ocorrencias_por_aluno(self):
        # Cria uma ocorrência para João Silva
        oc1 = Ocorrencia.objects.create(
            data='2026-06-15', turma=self.turma, professor=self.prof,
            disciplina=self.disc, descricao='Conversando', status='Aberta'
        )
        oc1.alunos.add(self.aluno1)

        # Cria uma ocorrência para Maria Oliveira
        oc2 = Ocorrencia.objects.create(
            data='2026-06-15', turma=self.turma, professor=self.prof,
            disciplina=self.disc, descricao='Dormiu', status='Aberta'
        )
        oc2.alunos.add(self.aluno2)

        # Filtra por 'João'
        response = self.client.get(reverse('dashboard') + '?tab=ocorrencias&filtro_aluno=João')
        self.assertEqual(response.status_code, 200)
        self.assertIn('João Silva', response.content.decode('utf-8'))
        self.assertNotIn('Maria Oliveira', response.content.decode('utf-8'))

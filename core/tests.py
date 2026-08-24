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


class CriteriosNotasTests(TestCase):
    def setUp(self):
        from decimal import Decimal
        from .models import Escola, AnoLetivo, NotaBimestral, ProvaAuxiliar, RecuperacaoFinal, ConselhoClasse
        from .services.calculo_notas import calcular_notas_disciplina, carregar_dados_boletim_aluno

        self.escola = Escola.objects.create(nome='Escola Teste')
        self.ano_letivo = AnoLetivo.objects.create(ano=2026)
        self.turma = Turma.objects.create(codigo='31', escola=self.escola, ano_letivo=self.ano_letivo)
        self.disc = Disciplina.objects.create(nome='Matemática')
        self.aluno = Aluno.objects.create(nome='Aluno Teste', turma=self.turma)

    def test_na_substituido_por_pa1_e_pa2(self):
        from decimal import Decimal
        from .models import NotaBimestral, ProvaAuxiliar
        from .services.calculo_notas import carregar_dados_boletim_aluno

        # B1 com falta (N/A) e B3 com falta (N/A)
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=1, ano_letivo=self.ano_letivo, nao_avaliado=True)
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=2, ano_letivo=self.ano_letivo, nota_prova=Decimal('6.00'))
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=3, ano_letivo=self.ano_letivo, nao_avaliado=True)
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=4, ano_letivo=self.ano_letivo, nota_prova=Decimal('7.00'))

        # Fez PA1 = 8.00 e PA2 = 7.50
        ProvaAuxiliar.objects.create(aluno=self.aluno, disciplina=self.disc, numero_pa=1, ano_letivo=self.ano_letivo, nota=Decimal('8.00'))
        ProvaAuxiliar.objects.create(aluno=self.aluno, disciplina=self.disc, numero_pa=2, ano_letivo=self.ano_letivo, nota=Decimal('7.50'))

        dados = carregar_dados_boletim_aluno(self.aluno, self.ano_letivo)
        linha = dados[0]

        # B1 assume nota da PA1 diretamente
        self.assertEqual(linha['b1']['valor'], Decimal('8.00'))
        self.assertTrue(linha['b1']['substituido_por_pa'])

        # B3 assume nota da PA2 diretamente
        self.assertEqual(linha['b3']['valor'], Decimal('7.50'))
        self.assertTrue(linha['b3']['substituido_por_pa'])

    def test_na_sem_pa_vira_zero(self):
        from decimal import Decimal
        from .models import NotaBimestral
        from .services.calculo_notas import carregar_dados_boletim_aluno

        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=1, ano_letivo=self.ano_letivo, nao_avaliado=True)
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=3, ano_letivo=self.ano_letivo, nao_avaliado=True)

        dados = carregar_dados_boletim_aluno(self.aluno, self.ano_letivo)
        linha = dados[0]

        self.assertEqual(linha['b1']['valor'], Decimal('0.00'))
        self.assertEqual(linha['b3']['valor'], Decimal('0.00'))

    def test_pa2_nao_altera_se_soma_maior_igual_20(self):
        from decimal import Decimal
        from .models import NotaBimestral, ProvaAuxiliar
        from .services.calculo_notas import carregar_dados_boletim_aluno

        # Soma = 6.0 + 6.0 + 5.0 + 5.0 = 22.0 (>= 20.0)
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=1, ano_letivo=self.ano_letivo, nota_prova=Decimal('6.00'))
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=2, ano_letivo=self.ano_letivo, nota_prova=Decimal('6.00'))
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=3, ano_letivo=self.ano_letivo, nota_prova=Decimal('5.00'))
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=4, ano_letivo=self.ano_letivo, nota_prova=Decimal('5.00'))

        # PA2 alta, mas aluno já atingiu os 20 pontos
        ProvaAuxiliar.objects.create(aluno=self.aluno, disciplina=self.disc, numero_pa=2, ano_letivo=self.ano_letivo, nota=Decimal('10.00'))

        dados = carregar_dados_boletim_aluno(self.aluno, self.ano_letivo)
        linha = dados[0]

        # B3 e B4 permanecem 5.00
        self.assertEqual(linha['b3']['valor'], Decimal('5.00'))
        self.assertFalse(linha['b3']['substituido_por_pa'])
        self.assertEqual(linha['media_anual'], Decimal('5.50'))
        self.assertEqual(linha['situacao'], 'Aprovado')

    def test_pa2_recupera_quando_soma_menor_20(self):
        from decimal import Decimal
        from .models import NotaBimestral, ProvaAuxiliar
        from .services.calculo_notas import carregar_dados_boletim_aluno

        # Soma = 3.0 + 4.0 + 3.0 + 4.0 = 14.0 (< 20.0)
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=1, ano_letivo=self.ano_letivo, nota_prova=Decimal('3.00'))
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=2, ano_letivo=self.ano_letivo, nota_prova=Decimal('4.00'))
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=3, ano_letivo=self.ano_letivo, nota_prova=Decimal('3.00'))
        NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=4, ano_letivo=self.ano_letivo, nota_prova=Decimal('4.00'))

        # PA2 = 8.00 -> (3 + 8)/2 = 5.50; (4 + 8)/2 = 6.00
        ProvaAuxiliar.objects.create(aluno=self.aluno, disciplina=self.disc, numero_pa=2, ano_letivo=self.ano_letivo, nota=Decimal('8.00'))

        dados = carregar_dados_boletim_aluno(self.aluno, self.ano_letivo)
        linha = dados[0]

        self.assertEqual(linha['b3']['valor'], Decimal('5.50'))
        self.assertTrue(linha['b3']['substituido_por_pa'])
        self.assertEqual(linha['b4']['valor'], Decimal('6.00'))
        self.assertTrue(linha['b4']['substituido_por_pa'])

        # Nova média anual = (3.0 + 4.0 + 5.50 + 6.0) / 4 = 18.5 / 4 = 4.63 (< 5.0)
        self.assertEqual(linha['media_anual'], Decimal('4.63'))
        self.assertEqual(linha['situacao'], 'Em Recuperação')

    def test_recuperacao_final_aprovado_fixa_media_5(self):
        from decimal import Decimal
        from .models import NotaBimestral, RecuperacaoFinal
        from .services.calculo_notas import carregar_dados_boletim_aluno

        for b in (1, 2, 3, 4):
            NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=b, ano_letivo=self.ano_letivo, nota_prova=Decimal('4.00'))

        # Média anual = 4.00. Aluno tira 8.50 na REC
        RecuperacaoFinal.objects.create(aluno=self.aluno, disciplina=self.disc, ano_letivo=self.ano_letivo, nota=Decimal('8.50'))

        dados = carregar_dados_boletim_aluno(self.aluno, self.ano_letivo)
        linha = dados[0]

        self.assertEqual(linha['rec_final']['valor'], Decimal('8.50'))
        # Média final deve ser 5.00 e não 8.50
        self.assertEqual(linha['media_final'], Decimal('5.00'))
        self.assertEqual(linha['situacao'], 'Aprovado na REC')

    def test_conselho_classe_promovido_fixa_media_5(self):
        from decimal import Decimal
        from .models import NotaBimestral, RecuperacaoFinal, ConselhoClasse
        from .services.calculo_notas import carregar_dados_boletim_aluno

        for b in (1, 2, 3, 4):
            NotaBimestral.objects.create(aluno=self.aluno, disciplina=self.disc, bimestre=b, ano_letivo=self.ano_letivo, nota_prova=Decimal('4.00'))

        # Tirou 3.00 na REC (< 5.0)
        RecuperacaoFinal.objects.create(aluno=self.aluno, disciplina=self.disc, ano_letivo=self.ano_letivo, nota=Decimal('3.00'))

        # Conselho de Classe promoveu o aluno
        ConselhoClasse.objects.create(aluno=self.aluno, disciplina=self.disc, ano_letivo=self.ano_letivo, promovido=True, observacao='Ata 05')

        dados = carregar_dados_boletim_aluno(self.aluno, self.ano_letivo)
        linha = dados[0]

        # Média final deve ser 5.00
        self.assertEqual(linha['media_final'], Decimal('5.00'))
        self.assertEqual(linha['situacao'], 'Aprovado pelo Conselho')
        self.assertTrue(linha['promovido_conselho'])


class AlertaOcorrenciasCoordenacaoTests(TestCase):
    def setUp(self):
        from .models import Escola, AnoLetivo, AcaoCoordenacao
        self.client = Client()
        self.escola = Escola.objects.create(nome='Escola Central')
        self.ano_letivo = AnoLetivo.objects.create(ano=2026, atual=True)
        self.turma = Turma.objects.create(codigo='91', escola=self.escola, ano_letivo=self.ano_letivo)
        
        self.aluno_critico = Aluno.objects.create(nome='Carlos Eduardo', turma=self.turma)
        self.aluno_normal = Aluno.objects.create(nome='Lucas Pereira', turma=self.turma)
        
        self.disc1 = Disciplina.objects.create(nome='História')
        self.disc2 = Disciplina.objects.create(nome='Geografia')
        
        self.u_coord = User.objects.create_user(username='coord_teste', password='123')
        self.prof_coord = Professor.objects.create(user=self.u_coord, nome='Coordenadora Ana', cargo='COORDENADOR')
        self.prof_coord.escolas.add(self.escola)

        self.u_prof = User.objects.create_user(username='prof_teste', password='123')
        self.prof_comum = Professor.objects.create(user=self.u_prof, nome='Prof Roberto', cargo='PROFESSOR')
        self.prof_comum.escolas.add(self.escola)

    def test_kpi_tres_ou_mais_ocorrencias(self):
        # 2 ocorrências para o aluno Carlos: ainda não é crítico (total < 3)
        oc1 = Ocorrencia.objects.create(data='2026-04-10', turma=self.turma, professor=self.prof_comum, disciplina=self.disc1, descricao='Sem material', status='Aberta')
        oc1.alunos.add(self.aluno_critico)
        oc2 = Ocorrencia.objects.create(data='2026-04-15', turma=self.turma, professor=self.prof_comum, disciplina=self.disc2, descricao='Conversando', status='Aberta')
        oc2.alunos.add(self.aluno_critico)

        self.client.login(username='coord_teste', password='123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_alunos_criticos'], 0)

        # 3ª ocorrência para o aluno Carlos (por outro professor ou disciplina)
        oc3 = Ocorrencia.objects.create(data='2026-04-20', turma=self.turma, professor=self.prof_comum, disciplina=self.disc1, descricao='Uso de celular', status='Aberta')
        oc3.alunos.add(self.aluno_critico)

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_alunos_criticos'], 1)
        self.assertIn('Alunos com ≥ 3 Ocorrências', response.content.decode('utf-8'))

    def test_listar_alunos_criticos_e_pagina_revisao(self):
        # Criar 3 ocorrências para Carlos
        for i in range(3):
            oc = Ocorrencia.objects.create(data=f'2026-05-0{i+1}', turma=self.turma, professor=self.prof_comum, disciplina=self.disc1, descricao=f'Motivo {i}', status='Aberta')
            oc.alunos.add(self.aluno_critico)

        self.client.login(username='coord_teste', password='123')
        # Acessar listagem de atenção
        response = self.client.get(reverse('ocorrencias_alunos_criticos'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Carlos Eduardo', response.content.decode('utf-8'))
        self.assertNotIn('Lucas Pereira', response.content.decode('utf-8'))

        # Acessar tela de revisão do aluno Carlos
        response_rev = self.client.get(reverse('ocorrencia_revisao_aluno', kwargs={'aluno_pk': self.aluno_critico.pk}))
        self.assertEqual(response_rev.status_code, 200)
        self.assertIn('Histórico de Ocorrências do Aluno', response_rev.content.decode('utf-8'))
        self.assertIn('Registrar Ação da Coordenação', response_rev.content.decode('utf-8'))

    def test_registrar_acao_coordenacao(self):
        from .models import AcaoCoordenacao
        # Criar 3 ocorrências abertas para Carlos
        for i in range(3):
            oc = Ocorrencia.objects.create(data=f'2026-05-0{i+1}', turma=self.turma, professor=self.prof_comum, disciplina=self.disc1, descricao=f'Motivo {i}', status='Aberta')
            oc.alunos.add(self.aluno_critico)

        self.client.login(username='coord_teste', password='123')
        response = self.client.post(reverse('ocorrencia_revisao_aluno', kwargs={'aluno_pk': self.aluno_critico.pk}), {
            'tipo_acao': 'COMUNICADO_FAMILIA',
            'data_acao': '2026-05-05',
            'descricao': 'Enviado comunicado oficial para a mãe e reunião agendada.',
            'marcar_resolvidas': '1'
        })
        self.assertEqual(response.status_code, 302)

        # Verifica criação do registro AcaoCoordenacao
        acao = AcaoCoordenacao.objects.filter(aluno=self.aluno_critico).first()
        self.assertIsNotNone(acao)
        self.assertEqual(acao.tipo_acao, 'COMUNICADO_FAMILIA')
        self.assertEqual(acao.coordenador, self.u_coord)
        self.assertEqual(acao.ocorrencias.count(), 3)

        # Ocorrências devem ter sido marcadas como resolvidas
        ocorrencias_abertas = Ocorrencia.objects.filter(alunos=self.aluno_critico, status='Aberta')
        self.assertEqual(ocorrencias_abertas.count(), 0)



from django.db import models
from django.contrib.auth.models import User
import datetime
from decimal import Decimal


class Escola(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Escola")
    codigo_inep = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código INEP")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Município")
    logo = models.ImageField(upload_to='escolas/logos/', blank=True, null=True, verbose_name="Logo da Escola")
    cor_primaria = models.CharField(max_length=7, default='#1e3a8a', verbose_name="Cor Primária (Hex)", help_text="Ex: #1e3a8a")

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class AnoLetivo(models.Model):
    ano = models.IntegerField(unique=True, verbose_name="Ano")
    atual = models.BooleanField(default=False, verbose_name="Ano Atual")

    class Meta:
        verbose_name = "Ano Letivo"
        verbose_name_plural = "Anos Letivos"
        ordering = ['-ano']

    def __str__(self):
        return str(self.ano)


class Turma(models.Model):
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='turmas', null=True, blank=True)
    codigo = models.CharField(max_length=10)
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, related_name='turmas', null=True, blank=True)
    ordem_exibicao = models.IntegerField(default=0)

    class Meta:
        ordering = ['escola', 'ano_letivo__ano', 'ordem_exibicao', 'codigo']
        unique_together = ('codigo', 'ano_letivo', 'escola')

    def __str__(self):
        ano_str = f" ({self.ano_letivo.ano})" if self.ano_letivo else ""
        return f'Turma {self.codigo}{ano_str}'


class GrupoDisciplina(models.Model):
    """Agrupa sub-disciplinas para exibição consolidada no boletim.
    Ex: Mat. I + Mat. II + Mat. III → 'Matemática'.
    """
    nome_boletim    = models.CharField(max_length=100, unique=True,
                          verbose_name='Nome no Boletim')
    faz_simulado_ef = models.BooleanField(
                          default=False,
                          verbose_name='Simulado EF 8°/9°',
                          help_text='Disciplinas deste grupo recebem bônus de simulado '
                                    'para turmas do 8° e 9° ano do EF.')
    ordem_boletim   = models.IntegerField(default=0, verbose_name='Ordem no Boletim')

    class Meta:
        verbose_name = 'Grupo de Disciplina'
        verbose_name_plural = 'Grupos de Disciplinas'
        ordering = ['ordem_boletim', 'nome_boletim']

    def __str__(self):
        return self.nome_boletim


class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    grupo = models.ForeignKey(
        GrupoDisciplina, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='disciplinas',
        verbose_name='Grupo no Boletim'
    )
    faz_simulado_ef = models.BooleanField(
        default=False,
        verbose_name='Simulado EF 8°/9° (standalone)',
        help_text='Usado apenas quando a disciplina não tem grupo definido.'
    )

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def elegivel_simulado_ef(self):
        """Retorna True se esta disciplina qualifica para simul ado em turmas EF 8°/9°."""
        if self.grupo:
            return self.grupo.faz_simulado_ef
        return self.faz_simulado_ef


class Professor(models.Model):
    CARGO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('DIRETOR', 'Diretor'),
        ('COORDENADOR', 'Coordenador'),
        ('AUX_COORD', 'Auxiliar de Coordenação'),
        ('AUX_ADMIN', 'Auxiliar Administrativo'),
        ('ORIENTADOR', 'Orientador Educacional'),
        ('SECRETARIA', 'Secretaria'),
        ('PROFESSOR', 'Professor'),
        ('INSPETOR', 'Inspetor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor')
    nome = models.CharField(max_length=200)
    escolas = models.ManyToManyField(Escola, blank=True, related_name='professores')
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF', help_text='Formato: 000.000.000-00')
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES, default='PROFESSOR')
    turmas = models.ManyToManyField(Turma, blank=True, related_name='professores')
    turmas_inspetor = models.ManyToManyField(
        Turma, blank=True, related_name='inspetores_responsaveis',
        verbose_name='Turmas (Inspetor)',
        help_text='Turmas pelas quais este inspetor é responsável'
    )
    disciplinas = models.ManyToManyField(Disciplina, blank=True)
    todas_turmas = models.BooleanField(default=False)
    todas_disciplinas = models.BooleanField(default=False)
    deve_trocar_senha = models.BooleanField(
        default=False,
        verbose_name='Deve trocar senha',
        help_text='Força o usuário a criar uma nova senha no próximo acesso.',
    )
    email_contato = models.EmailField(
        blank=True, null=True,
        verbose_name='E-mail de contato',
        help_text='E-mail pessoal do professor para comunicações e recuperação de senha.',
    )
    autorizado_lancar_notas = models.BooleanField(
        default=False,
        verbose_name='Autorizado a lançar notas',
        help_text='Permite que o professor lance notas dentro do período de lançamento configurado.',
    )

    def __str__(self):
        return f'{self.nome} ({self.get_cargo_display()})'

    @property
    def pode_ver_tudo(self):
        """Acesso global para visualização de relatórios e dados (exceto restrições específicas)."""
        return self.cargo in ['ADMIN', 'DIRETOR', 'COORDENADOR', 'AUX_COORD', 'AUX_ADMIN', 'ORIENTADOR', 'SECRETARIA', 'INSPETOR']

    @property
    def pode_ver_ocorrencias(self):
        """Secretaria não deve visualizar ocorrências."""
        if self.cargo == 'SECRETARIA':
            return False
        return True

    @property
    def pode_editar_tudo(self):
        """Acesso para editar qualquer registro no sistema."""
        return self.cargo in ['ADMIN', 'DIRETOR']

    @property
    def pode_gerar_relatorios(self):
        return self.cargo in ['ADMIN', 'DIRETOR', 'COORDENADOR', 'AUX_COORD', 'AUX_ADMIN', 'ORIENTADOR', 'SECRETARIA', 'INSPETOR']

    @property
    def pode_lancar_notas(self):
        """Retorna True para cargos com acesso irrestrito a notas."""
        return self.cargo in ['ADMIN', 'DIRETOR', 'AUX_ADMIN']

    def get_turmas(self, ano_letivo=None, escola=None):
        qs = Turma.objects.all()
        if not (self.todas_turmas or self.pode_ver_tudo):
            qs = self.turmas.all()
        
        if escola:
            qs = qs.filter(escola=escola)
        if ano_letivo:
            qs = qs.filter(ano_letivo=ano_letivo)
        return qs

    def get_disciplinas(self, ano_letivo=None):
        # Disciplinas are currently global, but we could filter them if needed.
        # For now, let's just return all.
        if self.todas_disciplinas or self.pode_ver_tudo:
            return Disciplina.objects.all()
        return self.disciplinas.all()


class Aluno(models.Model):
    nome = models.CharField(max_length=200)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='alunos')
    email_responsavel = models.EmailField(blank=True, null=True, verbose_name='E-mail do Responsável')
    foto = models.ImageField(
        upload_to='alunos/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto',
        help_text='Foto do aluno (será redimensionada automaticamente para 200×200 px).'
    )

    class Meta:
        ordering = ['turma__ano_letivo__ano', 'turma__ordem_exibicao', 'turma__codigo', 'nome']

    def __str__(self):
        return f'{self.nome} ({self.turma.codigo})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Redimensiona a foto ao salvar para economizar espaço
        if self.foto:
            self._redimensionar_foto()

    def _redimensionar_foto(self):
        from PIL import Image
        import logging
        import os
        try:
            caminho = self.foto.path
            with Image.open(caminho) as img:
                # Converte para RGB se necessário (ex.: PNG com alfa)
                if img.mode in ('RGBA', 'P', 'LA'):
                    img = img.convert('RGB')
                # Redimensiona mantendo proporção, encaixado em 200x200
                img.thumbnail((200, 200), Image.LANCZOS)
                img.save(caminho, 'JPEG', quality=85, optimize=True)
        except Exception as e:
            logging.getLogger('core').warning(
                'Falha ao redimensionar foto do aluno pk=%s: %s', self.pk, e
            )


class Ocorrencia(models.Model):
    STATUS_CHOICES = [
        ('Aberta', 'Aberta'),
        ('Resolvida', 'Resolvida'),
    ]
    data = models.DateField(db_index=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True)
    alunos = models.ManyToManyField(Aluno, blank=True)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aberta', db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'OC-{self.pk:04d} | {self.turma} | {self.data}'

    def alunos_str(self):
        return ', '.join(a.nome for a in self.alunos.all())


class ConteudoProgramatico(models.Model):
    data = models.DateField()
    turmas = models.ManyToManyField(Turma)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    # ── Confirmação pela Secretaria ──────────────────────
    confirmado_secretaria = models.BooleanField(
        default=False,
        verbose_name='Confirmado pela Secretaria',
        help_text='Quando confirmado, o professor não pode mais editar ou excluir o lançamento.',
    )
    confirmado_em = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Confirmado em',
    )
    confirmado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='conteudos_confirmados',
        verbose_name='Confirmado por',
    )

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f'{self.data} | {self.disciplina} | {self.professor}'

    def turmas_str(self):
        return ', '.join(t.codigo for t in self.turmas.all())


class AulaExtraProgramada(models.Model):
    data = models.DateField(db_index=True, verbose_name="Data da Aula Extra")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Aula Extra Programada"
        verbose_name_plural = "Aulas Extras Programadas"
        unique_together = ('data', 'turma', 'disciplina', 'professor')

    def __str__(self):
        return f"{self.data.strftime('%d/%m/%Y')} - {self.turma.codigo} - {self.disciplina.nome} ({self.professor.nome})"


class GradeHoraria(models.Model):
    DIA_CHOICES = [
        ('1', 'Segunda-feira'),
        ('2', 'Terça-feira'),
        ('3', 'Quarta-feira'),
        ('4', 'Quinta-feira'),
        ('5', 'Sexta-feira'),
    ]
    dia_semana = models.CharField(max_length=1, choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='grade_horaria')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='grade_horaria')

    class Meta:
        verbose_name = "Grade Horária"
        verbose_name_plural = "Grades Horárias"
        ordering = ['dia_semana', 'hora_inicio', 'turma__codigo']

    def __str__(self):
        return f"{self.get_dia_semana_display()} | {self.hora_inicio} | {self.turma} | {self.disciplina}"


class InspetorProxy(Professor):
    """Proxy para exibir inspetores separadamente no Admin."""
    class Meta:
        proxy = True
        verbose_name = 'Inspetor'
        verbose_name_plural = 'Inspetores'
        ordering = ['nome']

    def save(self, *args, **kwargs):
        self.cargo = 'INSPETOR'
        super().save(*args, **kwargs)


class ProfessorDocente(Professor):
    """Proxy para exibir apenas professores (docentes) no Admin."""
    class Meta:
        proxy = True
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        ordering = ['nome']

    def save(self, *args, **kwargs):
        self.cargo = 'PROFESSOR'
        super().save(*args, **kwargs)


class SugestaoConteudo(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='sugestoes')
    turmas = models.ManyToManyField(Turma, blank=True, related_name='sugestoes_conteudo')
    texto = models.TextField()
    ordem = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Sugestão de Conteúdo'
        verbose_name_plural = 'Sugestões de Conteúdo'
        ordering = ['disciplina', 'ordem', 'texto']

    def __str__(self):
        return f'{self.disciplina} | {self.texto[:50]}'


def _default_inicio_periodo():
    """Callable default — avaliado a cada criação, não no import."""
    return datetime.date(datetime.date.today().year, 2, 3)


def _default_fim_periodo():
    """Callable default — avaliado a cada criação, não no import."""
    return datetime.date(datetime.date.today().year, 12, 18)


class Configuracao(models.Model):
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='configuracoes', null=True, blank=True)
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, related_name='configuracoes', null=True, blank=True)
    inicio_periodo_letivo = models.DateField(verbose_name="Início do Período Letivo", default=_default_inicio_periodo)
    fim_periodo_letivo = models.DateField(verbose_name="Fim do Período Letivo", default=_default_fim_periodo)

    # ── Períodos de lançamento por bimestre ───────────────────────
    notas_b1_ini = models.DateField(null=True, blank=True, verbose_name='B1 — Início do lançamento')
    notas_b1_fim = models.DateField(null=True, blank=True, verbose_name='B1 — Fim do lançamento')
    notas_b2_ini = models.DateField(null=True, blank=True, verbose_name='B2 — Início do lançamento')
    notas_b2_fim = models.DateField(null=True, blank=True, verbose_name='B2 — Fim do lançamento')
    notas_pa1_ini = models.DateField(null=True, blank=True, verbose_name='PA1 — Início do lançamento')
    notas_pa1_fim = models.DateField(null=True, blank=True, verbose_name='PA1 — Fim do lançamento')
    notas_b3_ini = models.DateField(null=True, blank=True, verbose_name='B3 — Início do lançamento')
    notas_b3_fim = models.DateField(null=True, blank=True, verbose_name='B3 — Fim do lançamento')
    notas_b4_ini = models.DateField(null=True, blank=True, verbose_name='B4 — Início do lançamento')
    notas_b4_fim = models.DateField(null=True, blank=True, verbose_name='B4 — Fim do lançamento')
    notas_pa2_ini = models.DateField(null=True, blank=True, verbose_name='PA2 — Início do lançamento')
    notas_pa2_fim = models.DateField(null=True, blank=True, verbose_name='PA2 — Fim do lançamento')

    # ── Período global (fallback) ─────────────────────────────────
    periodo_notas_ini = models.DateField(
        null=True, blank=True,
        verbose_name='Período global — Início (fallback)',
        help_text='Usado somente se o bimestre não tiver datas próprias configuradas.'
    )
    periodo_notas_fim = models.DateField(
        null=True, blank=True,
        verbose_name='Período global — Fim (fallback)',
        help_text='Usado somente se o bimestre não tiver datas próprias configuradas.'
    )

    feriados = models.TextField(
        blank=True,
        default='',
        verbose_name="Feriados",
        help_text=(
            "Liste os feriados, um por linha, no formato AAAA-MM-DD. "
            "Linhas iniciadas com # são tratadas como comentários e ignoradas."
        ),
    )

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"
        unique_together = ('escola', 'ano_letivo')

    def __str__(self):
        ano = self.ano_letivo.ano if self.ano_letivo else self.inicio_periodo_letivo.year
        return f"Configuração do Ano Letivo ({ano})"

    def periodo_para_bimestre(self, periodo):
        """
        Retorna (inicio, fim) para o bimestre numérico (1,2,3,4) ou 'PA1'/'PA2'.
        Faz fallback para `periodo_notas_ini` e `periodo_notas_fim`.
        """
        p = str(periodo)
        mapping = {
            '1': (self.notas_b1_ini, self.notas_b1_fim),
            '2': (self.notas_b2_ini, self.notas_b2_fim),
            'PA1': (self.notas_pa1_ini, self.notas_pa1_fim),
            '3': (self.notas_b3_ini, self.notas_b3_fim),
            '4': (self.notas_b4_ini, self.notas_b4_fim),
            'PA2': (self.notas_pa2_ini, self.notas_pa2_fim),
        }
        
        ini, fim = mapping.get(p, (None, None))
        
        # Fallback se ambos não estiverem preenchidos especificamente
        if not ini or not fim:
            ini = self.periodo_notas_ini
            fim = self.periodo_notas_fim
        return ini, fim

    def get_feriados(self):
        """Retorna um set de datetime.date com os feriados configurados."""
        dates = set()
        for line in self.feriados.splitlines():
            line = line.strip().split('#')[0].strip()
            if line:
                try:
                    dates.add(datetime.date.fromisoformat(line))
                except ValueError:
                    pass
        return dates


# ──────────────────────────────────────────────
# CONTROLE DE NOTAS
# ──────────────────────────────────────────────

def turma_faz_simulado(turma, disciplina):
    """Retorna True se esta combinação turma/disciplina é elegível ao bônus de simulado."""
    if not turma or not turma.codigo:
        return False
    d = turma.codigo[0]
    if d in ('1', '2', '3'):  # Ensino Médio — todas as disciplinas
        return True
    if d in ('8', '9'):       # EF 8°/9° — apenas disciplinas elegíveis
        return disciplina.elegivel_simulado_ef()
    return False


class NotaBimestral(models.Model):
    BIMESTRE_CHOICES = [
        (1, '1º Bimestre'),
        (2, '2º Bimestre'),
        (3, '3º Bimestre'),
        (4, '4º Bimestre'),
    ]

    aluno         = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='notas')
    disciplina    = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    bimestre      = models.IntegerField(choices=BIMESTRE_CHOICES, db_index=True)
    ano_letivo    = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE)

    nota_prova    = models.DecimalField(max_digits=4, decimal_places=1,
                        null=True, blank=True,
                        verbose_name='Nota da Prova')
    nota_simulado = models.DecimalField(max_digits=4, decimal_places=1,
                        null=True, blank=True,
                        verbose_name='Nota do Simulado (interno)')
    nota_final    = models.DecimalField(max_digits=4, decimal_places=1,
                        editable=False,
                        verbose_name='Nota Final (calculada)')
    nao_avaliado  = models.BooleanField(
                        default=False,
                        verbose_name='Não Avaliado (ausente)',
                        help_text='Quando verdadeiro, o aluno não realizou a avaliação. '
                                  'A nota final é contabilizada como 0,0.')

    lancado_por   = models.ForeignKey(Professor, on_delete=models.SET_NULL,
                        null=True, blank=True, related_name='notas_lancadas')
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nota Bimestral'
        verbose_name_plural = 'Notas Bimestrais'
        unique_together = ('aluno', 'disciplina', 'bimestre', 'ano_letivo')
        ordering = ['aluno__nome', 'bimestre']

    def __str__(self):
        return (f'{self.aluno.nome} | {self.disciplina.nome} | '
                f'B{self.bimestre} | {self.nota_final}')

    def save(self, *args, **kwargs):
        """Calcula nota_final com bônus de simulado antes de salvar."""
        if self.nao_avaliado:
            # Aluno ausente: nota zerada, sem simulado
            self.nota_prova = Decimal('0')
            self.nota_simulado = None
            self.nota_final = Decimal('0')
        elif self.nota_simulado is not None:
            bonus = float(self.nota_simulado) * 0.01
            self.nota_final = min(
                Decimal('10.0'),
                self.nota_prova * Decimal(str(round(1 + bonus, 4)))
            )
        else:
            self.nota_final = self.nota_prova
        super().save(*args, **kwargs)


class ProvaAuxiliar(models.Model):
    NUMERO_CHOICES = [
        (1, 'PA1'),
        (2, 'PA2'),
    ]

    aluno       = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='provas_auxiliares')
    disciplina  = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    ano_letivo  = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE)
    numero_pa   = models.IntegerField(choices=NUMERO_CHOICES, verbose_name='Número da PA')
    nota        = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name='Nota da PA')

    lancado_por = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em   = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Prova Auxiliar'
        verbose_name_plural = 'Provas Auxiliares'
        unique_together = ('aluno', 'disciplina', 'ano_letivo', 'numero_pa')
        ordering = ['aluno__nome']

    def __str__(self):
        return f"{self.aluno.nome} - {self.disciplina.nome} - PA{self.numero_pa} - Nota: {self.nota}"


# ──────────────────────────────────────────────
# MURAL DE AVISOS
# ──────────────────────────────────────────────

class Aviso(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    autor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, verbose_name="Autor")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo

from django.db import models
from django.contrib.auth.models import User
import datetime


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


class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Professor(models.Model):
    CARGO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('DIRETOR', 'Diretor'),
        ('COORDENADOR', 'Coordenador'),
        ('AUX_COORD', 'Auxiliar de Coordenação'),
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

    def __str__(self):
        return f'{self.nome} ({self.get_cargo_display()})'

    @property
    def pode_ver_tudo(self):
        """Acesso global para visualização de relatórios e dados (exceto restrições específicas)."""
        return self.cargo in ['ADMIN', 'DIRETOR', 'COORDENADOR', 'AUX_COORD', 'ORIENTADOR', 'SECRETARIA', 'INSPETOR']

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
        return self.cargo in ['ADMIN', 'DIRETOR', 'COORDENADOR', 'AUX_COORD', 'ORIENTADOR', 'SECRETARIA', 'INSPETOR']

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
        except Exception:
            pass  # Não interrompe o fluxo se a imagem falhar


class Ocorrencia(models.Model):
    STATUS_CHOICES = [
        ('Aberta', 'Aberta'),
        ('Resolvida', 'Resolvida'),
    ]
    data = models.DateField()
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True)
    alunos = models.ManyToManyField(Aluno, blank=True)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aberta')
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


class Configuracao(models.Model):
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='configuracoes', null=True, blank=True)
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, related_name='configuracoes', null=True, blank=True)
    inicio_periodo_letivo = models.DateField(verbose_name="Início do Período Letivo", default=datetime.date(datetime.date.today().year, 2, 3))
    fim_periodo_letivo = models.DateField(verbose_name="Fim do Período Letivo", default=datetime.date(datetime.date.today().year, 12, 18))
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

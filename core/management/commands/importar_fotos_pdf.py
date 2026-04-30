"""
Comando de management para importar fotos de alunos a partir do PDF "Carografo".

Uso:
    python manage.py importar_fotos_pdf <caminho_do_pdf> [--dry-run] [--turma 61]
    python manage.py importar_fotos_pdf <caminho_do_pdf> --turma 61 --criar-alunos

O PDF segue o padrao "Carografo" do Colegio EME:
  - Cada pagina tem cabecalho com codigo da turma
  - Grade 4xN de fotos com nome e RM abaixo de cada foto
  - Texto extraivel no formato: "N - Nome Completo - RM: XXXX" ou variacoes
"""
import os
import re
import io
import sys
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.db import transaction


class Command(BaseCommand):
    help = 'Importa fotos dos alunos a partir do PDF Carografo do Colegio EME.'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Caminho para o arquivo PDF')
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Simula a importacao sem salvar no banco'
        )
        parser.add_argument(
            '--turma', type=str, default=None,
            help='Importa apenas uma turma especifica (ex.: 61)'
        )
        parser.add_argument(
            '--sobrescrever', action='store_true',
            help='Sobrescreve fotos ja existentes'
        )
        parser.add_argument(
            '--criar-alunos', action='store_true',
            help='Cria o cadastro do aluno automaticamente se nao encontrado no banco '
                 '(usa nome e RM extraidos do PDF). Requer que a turma ja exista.'
        )

    def handle(self, *args, **options):
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise CommandError('PyMuPDF nao esta instalado. Execute: pip install PyMuPDF')

        try:
            from PIL import Image
        except ImportError:
            raise CommandError('Pillow nao esta instalado. Execute: pip install Pillow')

        from core.models import Aluno, Turma

        pdf_path = options['pdf_path']
        if not os.path.exists(pdf_path):
            raise CommandError(f'Arquivo nao encontrado: {pdf_path}')

        dry_run        = options['dry_run']
        filtro_turma   = options['turma']
        sobrescrever   = options['sobrescrever']
        criar_alunos   = options['criar_alunos']

        if dry_run:
            self.stdout.write(self.style.WARNING('[SIMULACAO] Nenhuma alteracao sera salva.\n'))
        if criar_alunos:
            self.stdout.write(self.style.WARNING('[CRIAR-ALUNOS] Alunos nao encontrados serao cadastrados automaticamente.\n'))

        doc = fitz.open(pdf_path)
        self.stdout.write(f'PDF aberto: {len(doc)} paginas\n')

        stats = {'encontrados': 0, 'salvos': 0, 'nao_encontrados': 0, 'pulados': 0, 'criados': 0}
        turma_atual = None

        for page_num, page in enumerate(doc):
            # Extrai codigo da turma do cabecalho da pagina
            turma_codigo = self._extrair_turma(page)
            if turma_codigo:
                turma_atual = turma_codigo

            if not turma_atual:
                continue

            # Filtra por turma se solicitado
            if filtro_turma and not turma_atual.startswith(filtro_turma):
                continue

            self.stdout.write(f'  Pagina {page_num + 1} -> Turma {turma_atual}')

            # Obtem pares (foto, aluno) a partir da posicao na grade
            pares = self._extrair_pares_foto_aluno(page)

            for nome_pdf, rm_pdf, imagem_bytes in pares:
                stats['encontrados'] += 1

                # Tenta encontrar o aluno no banco
                aluno = self._buscar_aluno(nome_pdf, rm_pdf, turma_atual)

                if aluno is None:
                    if criar_alunos:
                        # Tenta obter o objeto Turma
                        try:
                            turma_obj = Turma.objects.get(codigo=turma_atual)
                        except Turma.DoesNotExist:
                            self.stdout.write(
                                self.style.ERROR(f'    [ERRO] Turma {turma_atual} nao existe no banco. Crie a turma primeiro.')
                            )
                            stats['nao_encontrados'] += 1
                            continue

                        if not dry_run:
                            aluno, criado = Aluno.objects.get_or_create(
                                turma=turma_obj,
                                nome=nome_pdf,
                            )
                            if criado:
                                self.stdout.write(
                                    self.style.SUCCESS(f'    [NOVO] Cadastrado: {nome_pdf} (RM: {rm_pdf}, Turma: {turma_atual})')
                                )
                                stats['criados'] += 1
                            else:
                                self.stdout.write(f'    [JA EXISTE] {aluno.nome}')
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'    [SIM-NOVO] Seria cadastrado: {nome_pdf} (RM: {rm_pdf}, Turma: {turma_atual})')
                            )
                            stats['criados'] += 1
                            continue  # em dry-run nao salva foto
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'    [NAO ENCONTRADO] "{nome_pdf}" (RM: {rm_pdf}, Turma: {turma_atual})')
                        )
                        stats['nao_encontrados'] += 1
                        continue

                if aluno and aluno.foto and not sobrescrever:
                    self.stdout.write(f'    [PULADO - ja tem foto] {aluno.nome}')
                    stats['pulados'] += 1
                    continue

                if aluno and not dry_run:
                    # Converte para JPEG e salva
                    jpeg_bytes = self._converter_jpeg(imagem_bytes)
                    nome_arquivo = f'{turma_atual}_{re.sub(r"[^a-zA-Z0-9]", "_", aluno.nome.lower())}.jpg'

                    # Remove foto antiga se existir
                    if aluno.foto:
                        try:
                            old_path = aluno.foto.path
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        except Exception:
                            pass

                    aluno.foto.save(nome_arquivo, ContentFile(jpeg_bytes), save=True)

                prefixo = '[SIM] ' if dry_run else ''
                self.stdout.write(
                    self.style.SUCCESS(f'    [OK] {prefixo}{aluno.nome} (Turma {turma_atual})')
                )
                stats['salvos'] += 1

        doc.close()

        self.stdout.write('\n' + '-' * 50)
        self.stdout.write('Resultado da importacao:')
        self.stdout.write(f'   Fotos encontradas no PDF : {stats["encontrados"]}')
        self.stdout.write(self.style.SUCCESS(f'   Salvas com sucesso       : {stats["salvos"]}'))
        if criar_alunos:
            self.stdout.write(self.style.SUCCESS(f'   Alunos criados           : {stats["criados"]}'))
        self.stdout.write(self.style.WARNING(f'   Alunos nao encontrados   : {stats["nao_encontrados"]}'))
        self.stdout.write(f'   Puladas (ja tem foto)    : {stats["pulados"]}')

    def _extrair_turma(self, page):
        """Extrai o codigo da turma do cabecalho da pagina."""
        text = page.get_text()
        header = text[:300]
        # Padrao: "61 ." ou "63 A" — dois digitos seguidos de espaco e letra ou ponto
        # O texto do cabecalho tem \n antes e apos o codigo da turma
        m = re.search(r'(\d{2})\s*[A-Z.]', header)
        if m:
            return m.group(1)
        return None

    def _extrair_pares_foto_aluno(self, page):
        """
        Retorna lista de (nome, rm, imagem_bytes) para cada aluno na pagina.
        A correlacao e feita por posicao: a foto fica acima do texto, mesma coluna X.
        """
        # Coleta imagens de alunos (exclui logo: w > 80 e w < 200)
        fotos = []
        for img in page.get_images(full=True):
            xref, w, h = img[0], img[2], img[3]
            if not (80 < w < 200):
                continue
            rects = page.get_image_rects(xref)
            if not rects:
                continue
            rect = rects[0]
            fotos.append({
                'xref': xref,
                'rect': rect,
                'cx': (rect.x0 + rect.x1) / 2,
                'y_bottom': rect.y1,
            })

        # Coleta blocos de texto de alunos
        blocks = page.get_text('blocks')
        alunos_texto = []
        for b in blocks:
            txt = b[4].strip()
            if re.search(r'\d+ -', txt) and 'RM' in txt:
                entradas = re.findall(
                    r'(\d+)\s*-\s*(.+?)\s*-?\s*RM:?\s*(\d+)',
                    txt.replace('\n', ' ')
                )
                for num, nome, rm in entradas:
                    cx_bloco = (b[0] + b[2]) / 2
                    alunos_texto.append({
                        'nome': nome.strip(' -'),
                        'rm': rm,
                        'cx': cx_bloco,
                        'y_top': b[1],
                    })

        if not fotos or not alunos_texto:
            return []

        # Casa fotos com alunos: mesma coluna (X proximo), foto ACIMA do texto
        pares = []
        usados = set()

        for foto in fotos:
            melhor = None
            melhor_dist = float('inf')

            for i, aluno in enumerate(alunos_texto):
                if i in usados:
                    continue
                # A foto deve estar acima do texto
                if foto['y_bottom'] > aluno['y_top'] + 10:
                    continue
                dx = abs(foto['cx'] - aluno['cx'])
                dy = aluno['y_top'] - foto['y_bottom']
                if dx < 60 and dy < 80:
                    dist = dx + dy * 0.5
                    if dist < melhor_dist:
                        melhor_dist = dist
                        melhor = i

            if melhor is not None:
                aluno = alunos_texto[melhor]
                usados.add(melhor)
                try:
                    img_bytes = page.parent.extract_image(foto['xref'])['image']
                except Exception:
                    img_bytes = None
                if img_bytes:
                    pares.append((aluno['nome'], aluno['rm'], img_bytes))

        return pares

    def _buscar_aluno(self, nome_pdf, rm_pdf, turma_codigo):
        """
        Tenta encontrar o aluno no banco.
        Estrategia:
          1. Por turma + nome exato (normalizado sem acentos)
          2. Por turma + nome parcial (pelo menos 2 palavras em comum)
        """
        from core.models import Aluno
        import unicodedata

        def normalizar(s):
            s = unicodedata.normalize('NFD', s)
            s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
            return s.upper().strip()

        nome_norm = normalizar(nome_pdf)

        # Busca alunos da turma
        candidatos = list(Aluno.objects.filter(turma__codigo=turma_codigo))

        # Tenta match exato (normalizado)
        for aluno in candidatos:
            if normalizar(aluno.nome) == nome_norm:
                return aluno

        # Tenta match parcial
        palavras_pdf = set(nome_norm.split())
        for aluno in candidatos:
            palavras_banco = set(normalizar(aluno.nome).split())
            em_comum = palavras_pdf & palavras_banco
            if len(em_comum) >= 2 and len(em_comum) / max(len(palavras_pdf), 1) >= 0.6:
                return aluno

        return None

    def _converter_jpeg(self, imagem_bytes):
        """Converte os bytes da imagem extraida para JPEG otimizado."""
        from PIL import Image
        img_io = io.BytesIO(imagem_bytes)
        with Image.open(img_io) as img:
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.thumbnail((200, 200), Image.LANCZOS)
            out = io.BytesIO()
            img.save(out, format='JPEG', quality=85, optimize=True)
            return out.getvalue()

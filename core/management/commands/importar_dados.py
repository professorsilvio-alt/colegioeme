import json
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import (Aluno, Disciplina, Professor, Turma)


class Command(BaseCommand):
    help = 'Importa dados dos arquivos JSON para o banco de dados'

    def handle(self, *args, **kwargs):
        base_dir = r'C:\Users\cejar\OneDrive\Área de Trabalho\Sistema EME'

        # ── Alunos ──
        alunos_path = os.path.join(base_dir, 'alunos.json')
        if os.path.exists(alunos_path):
            with open(alunos_path, encoding='utf-8') as f:
                alunos_data = json.load(f)
            cont_alunos = 0
            for item in alunos_data:
                nome = item.get('nome', '').strip()
                turma_cod = str(item.get('turma', '')).strip()
                if not nome or not turma_cod:
                    continue
                turma, _ = Turma.objects.get_or_create(codigo=turma_cod)
                _, created = Aluno.objects.get_or_create(nome=nome, turma=turma)
                if created:
                    cont_alunos += 1
            self.stdout.write(self.style.SUCCESS(f'[OK] {cont_alunos} alunos importados'))
        else:
            self.stdout.write(self.style.WARNING('[AVISO] alunos.json não encontrado, pulando...'))

        # ── Disciplinas ──
        disc_path = os.path.join(base_dir, 'disciplina.json')
        if os.path.exists(disc_path):
            with open(disc_path, encoding='utf-8') as f:
                disc_data = json.load(f)
            nomes_disc = set(row.get('Disciplina', '').strip() for row in disc_data if row.get('Disciplina'))
            for nome in nomes_disc:
                Disciplina.objects.get_or_create(nome=nome)
            self.stdout.write(self.style.SUCCESS(f'[OK] {len(nomes_disc)} disciplinas importadas'))
        else:
            # fallback
            disciplinas_padrao = [
                "Matemática", "Física", "Química", "Biologia",
                "Geografia", "História", "Inglês", "Sociologia", "Estendido"
            ]
            for nome in disciplinas_padrao:
                Disciplina.objects.get_or_create(nome=nome)
            self.stdout.write(self.style.SUCCESS('[OK] Disciplinas padrão criadas'))

        # ── Professores / Usuários ──
        prof_path = os.path.join(base_dir, 'professores_usuarios.json')
        if os.path.exists(prof_path):
            with open(prof_path, encoding='utf-8') as f:
                prof_data = json.load(f)
        else:
            prof_data = [
                {"nome": "Silvio Freitas", "usuario": "silvio", "senha": "123",
                 "turmas": ["81", "82", "91", "92", "93", "21", "22", "23", "31", "32"],
                 "disciplinas": ["Matemática", "Estendido"]},
                {"nome": "Administrador", "usuario": "admin", "senha": "123",
                 "turmas": "TODAS", "disciplinas": "TODAS"},
            ]

        cont_prof = 0
        for p in prof_data:
            nome = p['nome']
            usuario = p['usuario']
            senha = p['senha']
            todas_turmas = p['turmas'] == 'TODAS'
            todas_disciplinas = p['disciplinas'] == 'TODAS'
            is_admin = usuario in ['admin', 'master']

            user, created = User.objects.get_or_create(username=usuario)
            if created or not user.has_usable_password():
                user.set_password(senha)
            user.first_name = nome
            # Update permissions regardless of creation to ensure integrity
            user.is_staff = is_admin
            user.is_superuser = is_admin
            user.save()

            prof, _ = Professor.objects.get_or_create(user=user, defaults={'nome': nome, 'todas_turmas': todas_turmas, 'todas_disciplinas': todas_disciplinas})
            prof.nome = nome
            prof.todas_turmas = todas_turmas
            prof.todas_disciplinas = todas_disciplinas
            prof.save()

            if not todas_turmas and isinstance(p['turmas'], list):
                for cod in p['turmas']:
                    t, _ = Turma.objects.get_or_create(codigo=str(cod))
                    prof.turmas.add(t)

            if not todas_disciplinas and isinstance(p['disciplinas'], list):
                for disc_nome in p['disciplinas']:
                    d, _ = Disciplina.objects.get_or_create(nome=disc_nome)
                    prof.disciplinas.add(d)

            cont_prof += 1

        self.stdout.write(self.style.SUCCESS(f'[OK] {cont_prof} professores/usuários importados'))
        self.stdout.write(self.style.SUCCESS('\nIMPORTACAO CONCLUIDA! Acesse com os usuarios do JSON.'))

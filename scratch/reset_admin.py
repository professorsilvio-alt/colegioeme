import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Professor, Escola

user = User.objects.filter(username='admin').first()
if user:
    user.set_password('admin123')
    user.save()
    print("Senha do usuário 'admin' resetada para 'admin123'.")
    
    # Garantir perfil de professor
    escola = Escola.objects.first()
    prof, created = Professor.objects.get_or_create(
        user=user,
        defaults={
            'nome': 'Administrador Local',
            'cargo': 'ADMIN',
        }
    )
    if created or not prof.escolas.exists():
        if escola:
            prof.escolas.add(escola)
            print("Perfil de Professor vinculado à escola.")
else:
    print("Usuário 'admin' não encontrado.")

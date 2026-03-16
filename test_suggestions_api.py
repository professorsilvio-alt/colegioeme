import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from core.models import Disciplina, Turma

def test_api():
    client = Client()
    mat1 = Disciplina.objects.get(nome='Mat. I')
    
    # Test without auth (should redirect or fail if login_required)
    response = client.get(f'/api/sugestoes/?turma=31&disciplina={mat1.pk}')
    print(f"Status sem login: {response.status_code}") # Should be 302 if login_required
    
    # Create a temp superuser to test
    from django.contrib.auth.models import User
    if not User.objects.filter(username='test_admin').exists():
        User.objects.create_superuser('test_admin', 'admin@example.com', 'pass123')
    
    client.login(username='test_admin', password='pass123')
    response = client.get(f'/api/sugestoes/?turma=31&disciplina={mat1.pk}')
    print(f"Status com login: {response.status_code}")
    if response.status_code == 200:
        print("API Response:")
        print(response.json())
    
    # Cleanup
    User.objects.filter(username='test_admin').delete()

if __name__ == '__main__':
    test_api()

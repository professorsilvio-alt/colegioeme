import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from django.contrib.auth.models import User

try:
    u = User.objects.get(username='admin')
    u.set_password('adm@123')
    u.save()
    print("Password for 'admin' set to 'adm@123'")
except User.DoesNotExist:
    print("User 'admin' does not exist.")

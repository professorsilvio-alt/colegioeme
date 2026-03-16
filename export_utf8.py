
import os
import django
from django.core.management import call_command
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

def export_data():
    print("Exporting data to db_fixture.json with explicit UTF-8 encoding...")
    output_path = 'db_fixture.json'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata', 
            exclude=['auth.permission', 'contenttypes'], 
            indent=4, 
            stdout=f
        )
    print("Done! Data exported successfully.")

if __name__ == "__main__":
    export_data()

import os
import django
import unicodedata

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eme_project.settings')
django.setup()

from django.contrib.auth.models import User

def remove_accents(input_str):
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', str(input_str))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def reset_passwords_and_usernames():
    users = User.objects.all()
    changed = 0
    
    for user in users:
        old_username = user.username
        
        # Clean username (remove accents and make lowercase)
        clean_username = remove_accents(old_username).lower()
        
        # Ensure we don't end up with an empty string
        if not clean_username:
            clean_username = old_username
            
        user.username = clean_username
        
        # Generate new password based on the clean username
        prefix = clean_username[:3]
        new_password = f"{prefix}@123"
        
        user.set_password(new_password)
        user.save()
        changed += 1
        
        if old_username != clean_username:
            print(f"Username cleaned: '{old_username}' -> '{clean_username}' | Password set to: {new_password}")
        else:
            print(f"User '{clean_username}' | Password set to: {new_password}")

    print(f"\nSuccessfully updated usernames and passwords for {changed} users.")

if __name__ == '__main__':
    reset_passwords_and_usernames()

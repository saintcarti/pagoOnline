import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import CustomUser

users = CustomUser.objects.all()
print(f'Total usuarios: {users.count()}')

for user in users:
    print(f'Usuario: {user.username}')
    print(f'  Nombre: "{user.first_name}"')
    print(f'  Apellido: "{user.last_name}"')
    print(f'  Full name: "{user.get_full_name()}"')
    print(f'  Email: {user.email}')
    print('---')

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import CustomUser

# Crear usuarios adicionales para probar paginación
test_users = [
    ('cliente1', 'Ana', 'Torres', 'ana.torres@test.com', '12.345.671-0', '+56912345671', 'Calle Test 1, Santiago'),
    ('cliente2', 'Luis', 'Vera', 'luis.vera@test.com', '12.345.672-9', '+56912345672', 'Calle Test 2, Valparaíso'),
    ('vendedor1', 'Carmen', 'Rojas', 'carmen.rojas@test.com', '12.345.673-7', '+56912345673', 'Calle Test 3, Concepción'),
    ('contador1', 'Roberto', 'Paz', 'roberto.paz@test.com', '12.345.674-5', '+56912345674', 'Calle Test 4, La Serena'),
    ('bodeguero1', 'Isabel', 'Luna', 'isabel.luna@test.com', '12.345.675-3', '+56912345675', 'Calle Test 5, Temuco'),
    ('cliente3', 'Fernando', 'Vega', 'fernando.vega@test.com', '12.345.676-1', '+56912345676', 'Calle Test 6, Iquique'),
    ('cliente4', 'Mónica', 'Cruz', 'monica.cruz@test.com', '12.345.677-K', '+56912345677', 'Calle Test 7, Antofagasta'),
    ('vendedor2', 'Andrés', 'Soto', 'andres.soto@test.com', '12.345.678-8', '+56912345678', 'Calle Test 8, Rancagua'),
    ('cliente5', 'Paola', 'Reyes', 'paola.reyes@test.com', '12.345.679-6', '+56912345679', 'Calle Test 9, Talca'),
    ('cliente6', 'Marcelo', 'Flores', 'marcelo.flores@test.com', '12.345.680-K', '+56912345680', 'Calle Test 10, Chillán'),
]

created = 0
for username, first_name, last_name, email, rut, telefono, direccion in test_users:
    if not CustomUser.objects.filter(username=username).exists():
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password='test123',
            first_name=first_name,
            last_name=last_name,
            rut=rut,
            telefono=telefono,
            direccion=direccion,
            rol='cliente'
        )
        print(f'Usuario creado: {username} - {first_name} {last_name}')
        created += 1
    else:
        print(f'Usuario ya existe: {username}')

print(f'\nUsuarios creados: {created}')
print(f'Total usuarios: {CustomUser.objects.count()}')
print('¡Ahora puedes probar la paginación!')

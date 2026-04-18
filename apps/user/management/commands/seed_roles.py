"""
python manage.py seed_roles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.user.models import User
from apps.gestor.models import Document, TextoParametrizable, DocumentSequence
from apps.metadata.models import MetadataSchema, MetadataField

class Command(BaseCommand):
    help = 'Crea roles (grupos) y usuarios de prueba'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando el seed de roles y usuarios...')

        # 1. Definir los permisos por grupo
        permissions_map = {
            'CATEDRAL': [
                # Documentos
                'view_document', 'add_document', 'change_document', 'delete_document',
                'index_document', 'send_document', 'sign_document',
                # MetaDatos
                'view_metadataschema', 'view_metadatafield',
                # Parametrización
                'manage_textos_parametrizables', 'manage_sequences',
            ],
            'CONSULTA': [
                'view_document',
            ],
            'ADMINISTRADOR': 'all' # Marcador para asignar todos los del sistema
        }

        # 2. Crear Grupos y asignar permisos
        all_perms = Permission.objects.all()
        
        for group_name, perms_list in permissions_map.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Grupo "{group_name}" creado.')
            else:
                self.stdout.write(f'Grupo "{group_name}" ya existe. Actualizando permisos...')

            if perms_list == 'all':
                group.permissions.set(all_perms)
            else:
                # Buscar los objetos Permission por codename
                target_perms = []
                for codename in perms_list:
                    perm = all_perms.filter(codename=codename).first()
                    if perm:
                        target_perms.append(perm)
                    else:
                        self.stdout.write(self.style.WARNING(f'Advertencia: Permiso "{codename}" no encontrado.'))
                
                group.permissions.set(target_perms)
            
            group.save()

        # 3. Crear Usuarios de prueba
        test_users = [
            {
                'email': 'catedral@example.com',
                'username': 'Usuario Catedral',
                'group': 'CATEDRAL'
            },
            {
                'email': 'consulta@example.com',
                'username': 'Usuario Consulta',
                'group': 'CONSULTA'
            },
            {
                'email': 'admin@example.com',
                'username': 'Usuario Administrador',
                'group': 'ADMINISTRADOR'
            }
        ]

        default_password = 'password123'

        for u_data in test_users:
            user, created = User.objects.get_or_create(
                email=u_data['email'],
                defaults={
                    'username': u_data['username'],
                    'gender': 'MASCULINO',
                    'is_active': True,
                    'is_staff': True if u_data['group'] == 'ADMINISTRADOR' else False
                }
            )
            
            if created:
                user.set_password(default_password)
                user.save()
                self.stdout.write(f'Usuario "{u_data["email"]}" creado.')
            else:
                self.stdout.write(f'Usuario "{u_data["email"]}" ya existe.')

            # Asignar al grupo
            group = Group.objects.get(name=u_data['group'])
            user.groups.set([group])
            user.save()

        # 4. Asignar permisos requeridos a los SubMódulos (para el menú dinámico)
        self.stdout.write('Configurando permisos requeridos para submódulos...')
        
        submodule_permissions = {
            'first-stept-upload': 'gestor.add_document',
            'send_email_link': 'gestor.send_document',
            'capture_document': 'gestor.add_document',
            'document_list': 'gestor.view_document',
            'metadataschema_list': 'metadata.view_metadataschema',
            'metadatafield_list': 'metadata.view_metadatafield',
            'texto_list': 'gestor.manage_textos_parametrizables',
            'module_list': 'home.view_module',
            'submodule_list': 'home.view_submodule',
            'sequence_list': 'gestor.manage_sequences',
            'user_list': 'user.view_user',
            'group_list': 'auth.view_group',
            'permission_list': 'auth.view_permission',
        }

        from apps.home.models import SubModule
        for url_name, perm in submodule_permissions.items():
            sub = SubModule.objects.filter(url_name=url_name).first()
            if sub:
                sub.permission_required = perm
                sub.save()
                self.stdout.write(f'Permiso "{perm}" asignado al submódulo "{sub.name}".')
            else:
                self.stdout.write(self.style.WARNING(f'Advertencia: SubMódulo con URL "{url_name}" no encontrado.'))

        self.stdout.write(self.style.SUCCESS('Seed completado con éxito.'))
        self.stdout.write(f'Contraseña por defecto para todos: {default_password}')

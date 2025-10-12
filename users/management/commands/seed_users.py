from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.apps import apps
from faker import Faker
import random
import unicodedata
import re


User = get_user_model()


def slugify_username(value: str) -> str:
    # Elimina accents i normalitza el text per fer-lo apte com a nom d'usuari
    value = unicodedata.normalize('NFKD', value)
    value = ''.join([c for c in value if not unicodedata.combining(c)])
    # Converteix a minúscules
    value = value.lower()
    # Substitueix espais per punts
    value = re.sub(r"\s+", '.', value)
    # Elimina caràcters no vàlids
    value = re.sub(r'[^a-z0-9._-]', '', value)
    # Redueix punts consecutius
    value = re.sub(r'\.{2,}', '.', value)
    # Retalla caràcters sobrants
    value = value.strip('.-_')
    if not value:
        value = 'usuari'
    return value


class Command(BaseCommand):
    help = 'Genera usuaris de prova realistes per a StreamEvents.'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Nombre d\'usuaris de prova a crear (per defecte: 10)')
        parser.add_argument('--clear', action='store_true', help='Elimina els usuaris existents (excepte superusuaris) abans de crear-ne de nous')
        parser.add_argument('--with-follows', action='store_true', help='Crea relacions de seguiment aleatòries entre els usuaris generats')

    def handle(self, *args, **options):
        faker = Faker('es_ES')
        count = options['users']
        do_clear = options['clear']
        with_follows = options['with_follows']

        self.stdout.write(self.style.NOTICE(f"Iniciant seed: {count} usuaris (clear={do_clear})"))

        # Crea els grups necessaris si no existeixen
        groups = {}
        for gname in ('Organitzadors', 'Participants', 'Moderadors'):
            group, created = Group.objects.get_or_create(name=gname)
            groups[gname] = group
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grup creat: {gname}'))

        # Elimina usuaris existents si s'ha especificat --clear
        if do_clear:
            users_to_delete = [u for u in User.objects.all() if not u.is_superuser]
            deleted_count = len(users_to_delete)
            for u in users_to_delete:
                u.delete()

        # Assegura l\'existència del superusuari admin
        admin_defaults = {
            'email': 'admin@streamevents.com',
            'is_staff': True,
            'is_superuser': True,
        }
        admin_user, created = User.objects.get_or_create(username='admin', defaults=admin_defaults)
        if created:
            admin_user.set_password('admin123')
            admin_user.display_name = '🔧 Administrador' if hasattr(admin_user, 'display_name') else None
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'StreamEvents'
            try:
                if hasattr(admin_user, 'avatar'):
                    setattr(admin_user, 'avatar', '')
            except Exception:
                pass
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Superusuari "admin" creat.'))
        else:
            # Actualitza permisos si cal
            changed = False
            if not admin_user.is_superuser or not admin_user.is_staff:
                admin_user.is_superuser = True
                admin_user.is_staff = True
                changed = True
            if changed:
                admin_user.save()
                self.stdout.write(self.style.SUCCESS('Superusuari "admin" actualitzat.'))
            else:
                self.stdout.write(self.style.NOTICE('Superusuari "admin" ja existeix.'))

        created_users = []

        with transaction.atomic():
            for i in range(1, count + 1):
                first = faker.first_name()
                last = faker.last_name()
                base_username = slugify_username(f"{first}.{last}")

                # Garanteix unicitat del nom d'usuari
                username = base_username
                suffix = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{suffix}"
                    suffix += 1

                email = f"{username}@streamevents.com"

                role = 'Participants'
                display_prefix = ''
                # Assignació de rol segons índex: cada 5è -> Organitzador, cada 3r -> Moderador
                if i % 5 == 0:
                    role = 'Organitzadors'
                    display_prefix = '🎯 '
                elif i % 3 == 0:
                    role = 'Moderadors'
                    display_prefix = '🛡️ '

                display_name = f"{display_prefix}{first} {last}"

                defaults = {
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                }

                user_obj, created = User.objects.get_or_create(username=username, defaults=defaults)
                if created:
                    user_obj.set_password('password123')
                    # Assigna camps personalitzats si existeixen
                    if hasattr(user_obj, 'display_name'):
                        try:
                            setattr(user_obj, 'display_name', display_name)
                        except Exception:
                            pass
                    if hasattr(user_obj, 'bio'):
                        try:
                            setattr(user_obj, 'bio', faker.sentence(nb_words=12))
                        except Exception:
                            pass
                    if hasattr(user_obj, 'avatar'):
                        try:
                            setattr(user_obj, 'avatar', faker.image_url())
                        except Exception:
                            pass
                    user_obj.save()
                    self.stdout.write(self.style.SUCCESS(f'Creat: {username} ({role})'))
                else:
                    # Actualitza camps bàsics si ja existeix
                    updated = False
                    for fld, val in (('email', email), ('first_name', first), ('last_name', last)):
                        if getattr(user_obj, fld, None) != val:
                            setattr(user_obj, fld, val)
                            updated = True
                    if hasattr(user_obj, 'display_name') and getattr(user_obj, 'display_name', '') != display_name:
                        try:
                            setattr(user_obj, 'display_name', display_name)
                            updated = True
                        except Exception:
                            pass
                    if updated:
                        user_obj.save()
                        self.stdout.write(self.style.NOTICE(f'Actualitzat: {username}'))
                    else:
                        self.stdout.write(f'· {username} ja existia')

                # Assigna el grup corresponent
                group = groups.get(role, groups['Participants'])
                user_obj.groups.clear()
                user_obj.groups.add(group)

                created_users.append(user_obj)

        total_created = len(created_users)
        self.stdout.write(self.style.SUCCESS(f'S\'han creat/actualitzat {total_created} usuaris de prova.'))

        # Opcional: creació de relacions de seguiment si existeix el model Follow
        if with_follows:
            try:
                Follow = apps.get_model('users', 'Follow')
            except LookupError:
                Follow = None

            if not Follow:
                self.stdout.write(self.style.WARNING('No s\'ha trobat el model Follow a users.Follow — saltant la creació de follows.'))
            else:
                # Busca dues FK que apuntin al model d'usuari
                fk_fields = [f for f in Follow._meta.get_fields() if getattr(f, 'related_model', None) == User]
                if len(fk_fields) < 2:
                    self.stdout.write(self.style.WARNING('El model Follow no sembla contenir dues FK cap a l\'usuari — saltant.'))
                else:
                    follower_field = fk_fields[0].name
                    following_field = fk_fields[1].name
                    created_rel = 0
                    for u in created_users:
                        targets = random.sample([x for x in created_users if x != u], k=min(len(created_users)-1, random.randint(0, 5)))
                        for t in targets:
                            lookup = {follower_field: u, following_field: t}
                            obj, rel_created = Follow.objects.get_or_create(**lookup)
                            if rel_created:
                                created_rel += 1
                    self.stdout.write(self.style.SUCCESS(f'S\'han creat {created_rel} relacions de seguiment aleatòries.'))

        # Resum final
        self.stdout.write(self.style.SUCCESS('Seed finalitzat.'))
        self.stdout.write('Resum:')
        self.stdout.write(f' - Superusuari: admin@streamevents.com (admin)')
        self.stdout.write(f' - Usuaris processats: {total_created}')
        self.stdout.write(f' - Grups assegurats: {", ".join(groups.keys())}')

# StreamEvents - Fixtures

Aquest document explica com carregar les dades inicials de grups i usuaris al projecte **StreamEvents**.

---

## Requisits previs

1. Tenir la base de dades MongoDB en funcionament.
2. Executar `generate_user_fixtures.py` a l'arrel del projecte.  
   > L'script per defecte apunta a la carpeta `users`. Si els teus usuaris es gestionen en una aplicació amb un nom diferent, comprova que les rutes dins l'script són correctes (Línies 37 i 134).
3. Haver migrat totes les migracions:

```bash
python manage.py migrate
```

---

## Flux ràpid de càrrega

1. **Genera les fixtures** automàticament amb l'script:

```bash
python scripts/generate_user_fixtures.py
```

> L'script crea automàticament:
> - `users/fixtures/01_groups.json`
> - `users/fixtures/02_users.json`

2. **Carrega les fixtures a la base de dades**:

```bash
python manage.py loaddata 01_groups 02_users
```

> ⚠️ Important: l'ordre és clau. Primer els grups (`01_groups`), després els usuaris (`02_users`).

---

## Comprovar que les dades s’han carregat

Pots utilitzar la shell de Django:

```bash
python manage.py shell
```

```python
from users.models import CustomUser
from django.contrib.auth.models import Group

print(CustomUser.objects.all())
print(Group.objects.all())
```

Hauries de veure tots els usuaris i grups carregats correctament.

---

## Notes addicionals

- Les contrasenyes dels usuaris ja estan hashades amb `make_password`.
- Aquestes fixtures són per **entorns de desenvolupament**; per producció, utilitza mètodes segurs per crear usuaris.
- Si canvies el nom de l'app d'usuaris (`users`), recorda actualitzar el `model` dins les fixtures (`users.customuser`) i les rutes de l'script.

---

## Resum visual del flux

```
Migrate (crea col·leccions)
       ↓
Generar fixtures amb generate_user_fixtures.py
       ↓
loaddata 01_groups 02_users
       ↓
Comprovar dades a la shell
```
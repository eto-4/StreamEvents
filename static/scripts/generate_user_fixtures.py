#!/usr/bin/env python3
import os
import sys
import json

# Ruta de settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
from django.utils import timezone
django.setup()

from django.contrib.auth.hashers import make_password

# -----------------------------
# 1️⃣ Grups
# -----------------------------
groups = [
    {
        "model": "auth.group",
        "pk": 1,
        "fields": {
            "name": "Organitzadors",
            "permissions": []
        }
    },
    {
        "model": "auth.group",
        "pk": 2,
        "fields": {
            "name": "Participants",
            "permissions": []
        }
    },
    {
        "model": "auth.group",
        "pk": 3,
        "fields": {
            "name": "Moderadors",
            "permissions": []
        }
    }
]

groups_output_path = "users/fixtures/01_groups.json"
os.makedirs(os.path.dirname(groups_output_path), exist_ok=True)
with open(groups_output_path, "w", encoding="utf-8") as f:
    json.dump(groups, f, indent=2, ensure_ascii=False)
print(f"Fixture de grups generada en: {groups_output_path}")

# -----------------------------
# 2️⃣ Usuaris
# -----------------------------
users = [
    {
        "model": "users.customuser",
        "pk": 1,
        "fields": {
            "username": "admin",
            "email": "admin@streamevents.com",
            "password": make_password("admin123"),
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "date_joined": timezone.now().isoformat(),
            "groups": [1],
            "user_permissions": []
        }
    },
    {
        "model": "users.customuser",
        "pk": 2,
        "fields": {
            "username": "organitzador1",
            "email": "org1@streamevents.com",
            "password": make_password("password123"),
            "is_staff": False,
            "is_superuser": False,
            "is_active": True,
            "date_joined": timezone.now().isoformat(),
            "groups": [1],
            "user_permissions": []
        }
    },
    {
        "model": "users.customuser",
        "pk": 3,
        "fields": {
            "username": "participant1",
            "email": "part1@streamevents.com",
            "password": make_password("password123"),
            "is_staff": False,
            "is_superuser": False,
            "is_active": True,
            "date_joined": timezone.now().isoformat(),
            "groups": [2],
            "user_permissions": []
        }
    },
    {
        "model": "users.customuser",
        "pk": 4,
        "fields": {
            "username": "participant2",
            "email": "part2@streamevents.com",
            "password": make_password("password123"),
            "is_staff": False,
            "is_superuser": False,
            "is_active": True,
            "date_joined": timezone.now().isoformat(),
            "groups": [2],
            "user_permissions": []
        }
    },
    {
        "model": "users.customuser",
        "pk": 5,
        "fields": {
            "username": "moderador1",
            "email": "mod1@streamevents.com",
            "password": make_password("password123"),
            "is_staff": False,
            "is_superuser": False,
            "is_active": True,
            "date_joined": timezone.now().isoformat(),
            "groups": [3],
            "user_permissions": []
        }
    }
]

users_output_path = "users/fixtures/02_users.json"
os.makedirs(os.path.dirname(users_output_path), exist_ok=True)
with open(users_output_path, "w", encoding="utf-8") as f:
    json.dump(users, f, indent=2, ensure_ascii=False)
print(f"Fixture d'usuaris generada en: {users_output_path}")

"""
Això crearà:

- users/fixtures/01_groups.json
- users/fixtures/02_users.json

Després les pots carregar amb:

python scripts/generate_user_fixtures.py
python manage.py loaddata 01_groups 02_users
"""
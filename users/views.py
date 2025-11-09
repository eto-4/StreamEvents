from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserUpdateForm
from django.contrib.auth import get_user_model
import os

# Obtenim el model d'usuari configurat a settings.AUTH_USER_MODEL
User = get_user_model()

# ------------------------------
# VISTA INICIAL / HOME
# ------------------------------
def home_view(request):
    # Renderitza la plantilla home.html
    return render(request, 'home.html')

# ------------------------------
# VISTA DE REGISTRE
# ------------------------------
def register_view(request):
    if request.method == 'POST':
        # Creem el formulari amb les dades enviades
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Guardem l'usuari i fem login automàtic
            user = form.save()
            login(request, user)
            # Missatge d'èxit
            messages.success(request, 'Benvingut/da! Registre correcte.')
            # Redirigim al perfil
            return redirect('users:profile')
        else:
            # Missatge d'error si el formulari és invàlid
            messages.error(request, 'Si us plau corregeix els errors del formulari.')
    else:
        # Si no és POST, mostrem un formulari buit
        form = CustomUserCreationForm()
    # Renderitzem la plantilla amb el formulari
    return render(request, 'registration/register.html', {'form': form})

# ------------------------------
# VISTA DE LOGIN
# ------------------------------
def login_view(request):
    if request.method == 'POST':
        # Creem el formulari amb les dades enviades
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Obtenim l'usuari autenticat i fem login
            user = form.get_user()
            login(request, user)
            # Missatge d'èxit
            messages.success(request, 'Has iniciat sessió correctament.')
            # Redirigim a l'URL següent o al perfil
            next_url = request.GET.get('next') or reverse('users:profile')
            return redirect(next_url)
        else:
            # Missatge d'error si les credencials són incorrectes
            messages.error(request, 'Credencials incorrectes, prova de nou.')
    else:
        # Si no és POST, mostrem un formulari buit
        form = CustomAuthenticationForm(request)
    return render(request, 'registration/login.html', {'form': form})

# ------------------------------
# VISTA DE LOGOUT
# ------------------------------
def logout_view(request):
    # Tanquem la sessió de l'usuari
    logout(request)
    # Missatge informatiu
    messages.info(request, 'Has tancat la sessió.')
    # Redirigim a la pàgina principal
    return redirect('/')

# ------------------------------
# VISTA DE PERFIL PRIVAT
# ------------------------------
@login_required
def profile_view(request):
    # Renderitza la plantilla de perfil amb l'usuari actual
    return render(request, 'users/profile.html', {'user': request.user})

# ------------------------------
# VISTA D'EDICIÓ DE PERFIL
# ------------------------------
@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        # Creem el formulari amb les dades POST i els fitxers (avatar)
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Guardem els canvis del perfil
            form.save()
            messages.success(request, 'Perfil actualitzat correctament.')
            return redirect('users:profile')
        else:
            messages.error(request, 'Si us plau corregeix els errors.')
    else:
        # Mostrem el formulari amb les dades de l'usuari actual
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

# ------------------------------
# VISTA DE PERFIL PÚBLIC
# ------------------------------
def public_profile_view(request, username):
    # Obtenim l'usuari pel username o retornem 404
    user = get_object_or_404(User, username=username)
    return render(request, 'users/public_profile.html', {'profile_user': user})

# ------------------------------
# VISTA PER ELIMINAR AVATAR
# ------------------------------
@login_required
def remove_avatar(request):
    """Permet a l'usuari eliminar la seva foto de perfil."""
    user = request.user

    if user.avatar:
        # Obtenim la ruta completa del fitxer al sistema
        avatar_path = user.avatar.path

        # Eliminem el fitxer si existeix
        if os.path.isfile(avatar_path):
            os.remove(avatar_path)

        # Netegem el camp avatar del model i guardem
        user.avatar = None
        user.save()

        messages.success(request, "El teu avatar s’ha eliminat correctament.")
    else:
        messages.info(request, "No tens cap avatar per eliminar.")

    # Redirigim a la pàgina d'edició de perfil
    return redirect('users:edit_profile')
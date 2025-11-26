# users/forms.py

from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Obtenim el model d'usuari definit a settings.AUTH_USER_MODEL
# Així podem utilitzar CustomUser si l'hem definit
User = get_user_model()

# Validador per al camp username: només permet lletres, números i @ . + - _
username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message="El nom d'usuari només pot contenir lletres, números i els caràcters @/./+/-/_"
)

# ------------------------------
# 1) FORMULARI DE CREACIÓ D'USUARI
# ------------------------------
class CustomUserCreationForm(forms.ModelForm):
    """
    Formulari per registrar nous usuaris.
    - Basat en ModelForm per aprofitar el model com a base.
    - Afegim manualment password1 i password2 per demanar i confirmar contrasenya.
    - Validacions inclouen:
        * Email únic (sense importar majúscules/minúscules)
        * Username amb format permès
        * Contrassenyes coincidents
        * Validació de complexitat amb validate_password de Django
    """

    # Camp de contrasenya
    password1 = forms.CharField(
        label='Contrasenya',
        widget=forms.PasswordInput,
        help_text='Introdueix la teva contrasenya'
    )

    # Camp de confirmació de contrasenya
    password2 = forms.CharField(
        label='Confirmar contrasenya',
        widget=forms.PasswordInput,
        help_text='Repeteix la contrasenya per confirmar'
    )

    class Meta:
        model = User
        # Camps que es mostraran i podran ser guardats (excepte la password que la gestionem manualment)
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        # Cridem al constructor del pare
        super().__init__(*args, **kwargs)
        # Afegim el validador de username al camp corresponent
        self.fields['username'].validators.append(username_validator)
        # Fem que l'email sigui obligatori
        self.fields['email'].required = True

        # Afegim classes CSS per a Bootstrap
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        """
        Validació: comprovar que no existeixi un altre usuari amb el mateix email.
        Case-insensitive.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ja existeix un usuari amb aquest correu electrònic.')
        return email

    def clean_password2(self):
        """
        Validació de la contrasenya:
        - Comprovar que password1 i password2 coincideixin.
        - Validar complexitat amb validate_password de Django.
        """
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')

        # Comprovem coincidència
        if p1 and p2 and p1 != p2:
            raise ValidationError('Les contrasenyes no coincideixen.')

        # Validem complexitat
        try:
            if p1:
                validate_password(p1, user=None)
        except ValidationError as e:
            # Re-lansem errors combinats
            raise ValidationError(e.messages)

        return p2

    def save(self, commit=True):
        """
        Guardem l'usuari amb password hash.
        - Creem la instància amb commit=False
        - assignem la contrasenya amb set_password()
        - guardem si commit=True
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


# ------------------------------
# 2) FORMULARI D'EDICIÓ DE PERFIL
# ------------------------------
class CustomUserUpdateForm(forms.ModelForm):
    """
    Formulari per editar perfil:
    - Camps: first_name, last_name, display_name, bio, avatar
    - Widgets especials:
        * bio: Textarea
        * avatar: ImageField + FileInput
    """
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    avatar = forms.ImageField(
        widget=forms.FileInput, 
        required=False
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'display_name', 'bio', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Afegim classes CSS de Bootstrap a tots els camps
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        # Placeholder per al camp bio
        self.fields['bio'].widget.attrs.update({'placeholder': 'Explica alguna cosa sobre el teu perfil...'})


# ------------------------------
# 3) FORMULARI D'AUTENTICACIÓ
# ------------------------------
class CustomAuthenticationForm(AuthenticationForm):
    """
    Extensió d'AuthenticationForm per permetre login amb username o email.
    - Reemplaça l'etiqueta del camp username per 'Username o Email'.
    - A clean(), intentem autenticar primer per username, si falla i és un email, busquem el username real.
    """
    username = forms.CharField(label='Username o Email')

    def clean(self):
        # Override del clean per permetre login amb email també
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Primer intent amb username
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                # Si falla, busquem un usuari amb email coincident
                possible = User.objects.filter(email__iexact=username).first()
                if possible:
                    # Intentem autenticar amb el username real
                    user = authenticate(self.request, username=possible.username, password=password)
            if user is None:
                # Si no s'autentica, error general
                raise ValidationError('Credencials invàlides. Revisa el nom d\'usuari/email i la contrasenya.')

            # Comprovació que Django fa per permetre login
            self.confirm_login_allowed(user)
            # Guardem l'usuari autenticat a l'instància
            self.user_cache = user

        return self.cleaned_data

    def get_user(self):
        """
        Retorna l'usuari autenticat (si existeix)
        """
        return getattr(self, 'user_cache', None)
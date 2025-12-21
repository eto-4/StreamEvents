from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Event

# ==============================
# 4.1 EventCreationForm
# ==============================

class EventCreationForm(forms.ModelForm):
    """
    Formulari per a la creació d'esdeveniments.
    
    Basat en ModelForm, genera automàticament camps segons el model Event.
    Inclou validacions personalitzades per títol, data programada i espectadors.
    """

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'scheduled_date',
            'thumbnail', 'max_viewers', 'tags', 'stream_url', 'status'
        ]
        widgets = {
            # Àrea de text per al títol
            'title': forms.Textarea(
              attrs={
                  'rows': 1,
                  'class': 'form-control',
                  'placeholder': 'Entra un títol per al teu esdeveniment'
              }  
            ),
            # Àrea de text per a la descripció
            'description': forms.Textarea(
                attrs={
                    'rows': 4, 
                    'class': 'form-control', 
                    'placeholder': 'De qué tracta aquest esdeveniment?'
                }
            ),
            # DateTimeInput amb atributs HTML5
            'scheduled_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local', 
                    'class': 'form-control'
                }
            ),
            # Camp de pujada d'arxius amb estils Bootstrap
            'thumbnail': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file'
                }
            ),
            'tags': forms.Textarea(
                attrs={                    
                    'rows': 2,
                    'class': 'form-control',
                    'placeholder': 'Separa els teus tags amb comes \',\'; p.ex: Tag1, Tag2, Tag3...'
                }
            ),
            'stream_url': forms.Textarea(
                attrs={                    
                    'rows': 1,
                    'class': 'form-control',
                    'placeholder': 'Entra l\'enllaç cap a l\'esdeveniment'
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        """
        Desa l'usuari que està creant l'esdeveniment.
        S'extreu del kwargs per a poder validar títols únics per usuari.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_scheduled_date(self):
        """
        Validació: la data no pot ser en el passat.
        """
        scheduled_date = self.cleaned_data['scheduled_date']
        if scheduled_date < timezone.now():
            raise forms.ValidationError('La data programada no pot ser en el passat.')
        return scheduled_date

    def clean_title(self):
        """
        Validació: l'usuari no pot tenir dos esdeveniments amb el mateix títol.
        """
        title = self.cleaned_data['title']
        if Event.objects.filter(title=title, creator=self.user).exists():
            raise forms.ValidationError('Ja tens un esdeveniment amb aquest títol.')
        return title

    def clean_max_viewers(self):
        """
        Validació: nombre màxim d'espectadors entre 1 i 1000.
        """
        max_viewers = self.cleaned_data['max_viewers']
        if not (1 <= max_viewers <= 1000):
            raise forms.ValidationError(
                "El nombre màxim d'espectadors ha d'estar entre 1 i 1000."
            )
        return max_viewers
    

# ==============================
# 4.2 EventUpdateForm
# ==============================

class EventUpdateForm(forms.ModelForm):
    """
    Formulari per actualitzar esdeveniments existents.
    
    Inclou validació per impedir canviar l'estat si no ets el creador,
    i impedeix modificar la data si l'esdeveniment ja és en directe.
    """

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'scheduled_date',
            'thumbnail', 'max_viewers', 'tags', 'stream_url', 'status'
        ]
        widgets = {
            # Àrea de text per al títol
            'title': forms.Textarea(
              attrs={
                  'rows': 1,
                  'class': 'form-control',
                  'placeholder': 'Entra un títol per al teu esdeveniment'
              }  
            ),
            # Àrea de text per a la descripció
            'description': forms.Textarea(
                attrs={
                    'rows': 4, 
                    'class': 'form-control', 
                    'placeholder': 'De qué tracta aquest esdeveniment?'
                }
            ),
            # DateTimeInput amb atributs HTML5
            'scheduled_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local', 
                    'class': 'form-control'
                }
            ),
            # Camp de pujada d'arxius amb estils Bootstrap
            'thumbnail': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file'
                }
            ),
            'tags': forms.Textarea(
                attrs={                    
                    'rows': 2,
                    'class': 'form-control',
                    'placeholder': 'Separa els teus tags amb comes \',\'; p.ex: Tag1, Tag2, Tag3...'
                }
            ),
            'stream_url': forms.Textarea(
                attrs={                    
                    'rows': 1,
                    'class': 'form-control',
                    'placeholder': 'Entra l\'enllaç cap a l\'esdeveniment'
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        """
        Desa l'usuari que està actualitzant l'esdeveniment.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    
    def clean_status(self):
        """
        Validació: només el creador pot canviar l'estat.
        """
        status = self.cleaned_data['status']
        if 'status' in self.changed_data and self.instance.creator != self.user:
            raise forms.ValidationError("Només el creador pot canviar l'estat.")
        return status
    
    def clean_scheduled_date(self):
        """
        Validació: no es pot canviar la data d'un esdeveniment en directe.
        """
        scheduled_date = self.cleaned_data['scheduled_date']
        if self.instance.is_live() and 'scheduled_date' in self.changed_data:
            raise forms.ValidationError(
                "No es pot canviar la data d'un esdeveniment que ja està en directe."
            )
        return scheduled_date
    

# ==============================
# 4.3 EventSearchForm
# ==============================

class EventSearchForm(forms.Form):
    """
    Formulari de cerca i filtratge d'esdeveniments.
    Camps opcionals per textos, categories, estat i rang de dates.
    """

    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Cercar...',
                'class': 'form-control'
            }
        )
    )
    
    CATEGORY_CHOICES = [('all', 'Totes')] + Event.CATEGORY_CHOICES
    STATUS_CHOICES = [('all', 'Tots')] + Event.STATUS_CHOICES
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )
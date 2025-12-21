from django import forms
from .models import ChatMessage
from .utils import contains_bad_words, empty_message, outof_length_range 
import re

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                
            
                                      'class': 'form-control',
                                      'rows': 2,
                                      'placeholder': 'Escriu un missatge...',
                                      'maxlength': 500,
                                      })
        }
    
    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()

        # Filtre de validacions
        if empty_message(msg): raise forms.ValidationError("El missatge no pot estar buit.")
        if outof_length_range(msg): raise forms.ValidationError("Missatge massa llarg. Número màxim de caracters: 500.")
        if contains_bad_words(msg): raise forms.ValidationError("El missatge conté llenguatge ofensiu.")
        
        # Si està net retornem el missatge
        return msg
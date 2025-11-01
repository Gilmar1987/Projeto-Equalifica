from django import forms
from .models import Entrevista

class EntrevistaForm(forms.ModelForm):
    class Meta:
        model = Entrevista
        fields = ['data_agendada', 'link_video', 'observacoes']
        widgets = {
            'data_agendada': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'link_video': forms.URLInput(attrs={'placeholder': 'Link para a entrevista por vídeo (opcional)'}),
            'observacoes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Observações adicionais sobre a entrevista'}),
        }
        help_texts = {
            'data_agendada': 'Selecione a data e hora da entrevista',
            'link_video': 'Informe o link para a entrevista por vídeo (se aplicável)',
            'observacoes': 'Adicione observações ou instruções para o candidato',
        }
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, PCDProfile

class PCDRegistrationForm(UserCreationForm):
    cpf = forms.CharField(max_length=14, help_text="Formato: XXX.XXX.XXX-XX ou XXXXXXXXXXX")
    disability = forms.ChoiceField(choices=PCDProfile.DISABILITY_CHOICES, label="Tipo de Deficiência")
    skills = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), label="Liste suas habilidades e competências (Separadas por Vírgula).")
    lgpd_consent = forms.BooleanField(required=True, label="Concordo com a política de privacidade (LGPD).")
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'cpf', 'disability', 'skills', 'lgpd_consent')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.user_type = 'pcd'
        if commit:
            user.save()
            pcd_profile = PCDProfile.objects.create(
                user=user,
                cpf=self.cleaned_data['cpf'],
                disability=self.cleaned_data['disability'],
                skills=self.cleaned_data['skills'],
                lgpd_consent=self.cleaned_data['lgpd_consent']
            )
        return user
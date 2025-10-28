from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from common.models import BaseModel
from common.validators import validate_cpf
from maching.extractor import extract_features


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('pcd', 'Pessoa com Deficiência'),
        ('recruiter', 'Recrutador'),
        ('admin', 'Administrador'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='pcd')
    # Sobrescrever campos para evitar conflito de related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # nome único
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # nome único
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] #Mantém username por compatibilidade
    
    def __str__(self):
        return self.email
    
class PCDProfile(BaseModel):
    DISABILITY_CHOICES = (
        ('visual', 'Deficiência Visual'),
        ('auditiva', 'Deficiência Auditiva'),
        ('fisica', 'Deficiência Física'),
        ('intelectual', 'Deficiência Intelectual'),
        ('multipla', 'Deficiência Múltipla'),
    )
# Create your models here.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pcd_profile')
    cpf = models.CharField(max_length=14, unique=True, validators=[validate_cpf, MinLengthValidator(11)],
          help_text="Formato: XXX.XXX.XXX-XX ou XXXXXXXXXXX")
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES)
    skills = models.TextField(blank=True, help_text="Liste suas habilidades e competências (Separadas por Vírgula).")   
    lgpd_consent = models.BooleanField(default=False, help_text="Concordo com a política de privacidade (LGPD).")   
    
    
        
        # Campos para armazenar vetores
    hard_skills_vetor = models.JSONField(default=list)
    soft_skills_vetor = models.JSONField(default=list)
    acessibilidade_vetor = models.JSONField(default=list)
    experiencia_total = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        from maching.extractor import extract_features
        # Corrigido: usar apenas campos existentes
        texto = (self.skills or "")
        attrs = extract_features(texto)
        
        self.hard_skills_vetor = list(attrs['hard_skills'])
        self.soft_skills_vetor = list(attrs['soft_skills'])
        self.acessibilidade_vetor = list(attrs['acessibilidade'])
        self.experiencia_total = attrs['experiencia']
        
        super().save(*args, **kwargs)
        def __str__(self):
            return f"PCD: {self.user.email} - {self.get_disability_display()}"
        
        
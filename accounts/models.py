from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from common.models import BaseModel
from common.validators import validate_cpf
from common.validators import validate_cnpj


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
    skills = models.TextField(help_text="Liste suas habilidades e competências (Separadas por Vírgula).")   
    lgpd_consent = models.BooleanField(default=False, help_text="Concordo com a política de privacidade (LGPD).")   
    
    def __str__(self):
        return f"PCD: {self.user.email} - {self.get_disability_display()}"
    
    
from django.db import models
from common.models import BaseModel
from common.validators import validate_cnpj

class Empresa(BaseModel):
    nome = models.CharField(max_length=255, verbose_name="Razão Social")
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        validators=[validate_cnpj],
        verbose_name="CNPJ",
        help_text="Formato: XX.XXX.XXX/0001-XX ou XXXXXXXXX0001XX"
    )
    endereco = models.TextField(blank=True, verbose_name="Endereço")

    def __str__(self):
        return f"Empresa: {self.nome} - {self.cnpj}"

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"


class Recrutador(BaseModel):
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'recruiter'},  # ← CORRIGIDO
        related_name='recruiter_profile'
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='recrutadores'
    )
    cargo = models.CharField(max_length=100, blank=True, verbose_name="Cargo")

    def __str__(self):
        return f"{self.user.email} - {self.empresa.nome}"

    class Meta:
        verbose_name = "Recrutador"
        verbose_name_plural = "Recrutadores"
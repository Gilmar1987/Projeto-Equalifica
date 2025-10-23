# recruitment/models.py
from django.db import models
from common.models import BaseModel

class Vaga(BaseModel):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    requisitos = models.TextField()
    acessibilidade = models.JSONField(
        default=dict,
        help_text="Ex: {'libras': true, 'legendas': true, 'descricao_alt': true}"
    )
    cnpj_empresa = models.CharField(max_length=18)  # preenchido automaticamente

    def __str__(self):
        return f"{self.titulo} - {self.cnpj_empresa}"

    class Meta:
        verbose_name = "Vaga"
        verbose_name_plural = "Vagas"

class Candidatura(BaseModel):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('entrevista', 'Entrevista Agendada'),
        ('rejeitado', 'Rejeitado'),
        ('contratado', 'Contratado'),
    ]
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='candidaturas')
    cpf_pcd = models.CharField(max_length=14)      # preenchido automaticamente
    cnpj_empresa = models.CharField(max_length=18)  # copiado da vaga
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    def __str__(self):
        return f"Candidatura de {self.cpf_pcd} à {self.vaga.titulo}"

    class Meta:
        verbose_name = "Candidatura"
        verbose_name_plural = "Candidaturas"
        unique_together = ('vaga', 'cpf_pcd')  # evita candidaturas duplicadas
# Create your models here.
# recruitment/models.py (adicione ao final)

class Entrevista(BaseModel):
    candidatura = models.OneToOneField(Candidatura, on_delete=models.CASCADE, related_name='entrevista')
    data_agendada = models.DateTimeField()
    link_video = models.URLField(blank=True, help_text="Link para sala de vídeo (ex: Zoom, Google Meet)")
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"Entrevista para {self.candidatura.vaga.titulo} - {self.candidatura.cpf_pcd}"
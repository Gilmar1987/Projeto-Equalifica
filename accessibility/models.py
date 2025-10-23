# accessibility/models.py
from django.db import models
from common.models import BaseModel

class LogAcessibilidade(BaseModel):
    TIPO_TRADUCAO_CHOICES = [
        ('libras_para_audio', 'Libras → Áudio'),
        ('audio_para_libras', 'Áudio → Libras'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_TRADUCAO_CHOICES)
    cpf_pcd = models.CharField(max_length=14)
    cnpj_empresa = models.CharField(max_length=18)
    conteudo_original = models.TextField(blank=True, help_text="Texto ou URL do áudio/vídeo original")
    conteudo_traduzido = models.TextField(blank=True, help_text="Texto traduzido ou URL do resultado")
    duracao_segundos = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cpf_pcd}"

    class Meta:
        verbose_name = "Log de Acessibilidade"
        verbose_name_plural = "Logs de Acessibilidade"

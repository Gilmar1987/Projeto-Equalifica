# recruitment/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Entrevista

@shared_task
def enviar_notificacoes_entrevista(entrevista_id):
    entrevista = Entrevista.objects.get(id=entrevista_id)
    pcd_email = entrevista.candidatura.cpf_pcd  # ou vincule ao User.email
    agora = timezone.now()
    diff = (entrevista.data_agendada - agora).total_seconds() / 60

    if diff <= 16 and diff > 14:
        send_mail(
            'Sua entrevista começa em 15 minutos',
            f'Entrevista para {entrevista.candidatura.vaga.titulo}',
            'noreply@equalifica.com',
            [pcd_email],
            fail_silently=False,
        )
    # Repetir para 10 e 5 minutos com lógica similar
    if diff <= 11 and diff > 9:
        send_mail(
            'Sua entrevista começa em 10 minutos',
            f'Entrevista para {entrevista.candidatura.vaga.titulo}',
            'noreply@equalifica.com',
            [pcd_email],
            fail_silently=False,
        )
    # Repetir para 10 e 5 minutos com lógica similar
    if diff <= 6 and diff > 4:
        send_mail(
            'Sua entrevista começa em 5 minutos',
            f'Entrevista para {entrevista.candidatura.vaga.titulo}',
            'noreply@equalifica.com',
            [pcd_email],
            fail_silently=False,
        )
     
#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equalifica_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from companies.models import Empresa, Recrutador
from recruitment.models import Vaga, Candidatura, Entrevista
from accounts.models import PCDProfile

print("=== E2E Flow: Recruiter creates job, PCD applies, Recruiter schedules interview ===")

client = Client()
User = get_user_model()

# 1) Ensure test company and users exist
empresa, _ = Empresa.objects.get_or_create(
    cnpj='12.345.678/0001-90',
    defaults={'nome': 'E2E Test Company', 'endereco': 'Rua Teste 123'}
)

recruiter_email = 'e2e.recruiter@example.com'
pcd_email = 'e2e.pcd@example.com'
password = 'Test12345!'

recruiter, created_r = User.objects.get_or_create(
    email=recruiter_email,
    defaults={'username': 'e2e.recruiter', 'user_type': 'recruiter'}
)
if created_r:
    recruiter.set_password(password)
    recruiter.save()

# Link recruiter profile to company
recruiter_profile, _ = Recrutador.objects.get_or_create(user=recruiter, defaults={'empresa': empresa})
if recruiter_profile.empresa_id != empresa.id:
    recruiter_profile.empresa = empresa
    recruiter_profile.save()

pcd_user, created_p = User.objects.get_or_create(
    email=pcd_email,
    defaults={'username': 'e2e.pcd', 'user_type': 'pcd'}
)
if created_p:
    pcd_user.set_password(password)
    pcd_user.save()

# Ensure PCD profile exists with a valid CPF
try:
    pcd_profile = pcd_user.pcd_profile
except PCDProfile.DoesNotExist:
    candidate_cpfs = [
        '111.444.777-35',
        '529.982.247-25',
        '153.585.380-13',
        '700.876.940-06',
    ]
    cpf_choice = None
    for cpf in candidate_cpfs:
        if not PCDProfile.objects.filter(cpf=cpf).exists():
            cpf_choice = cpf
            break
    if cpf_choice is None:
        raise RuntimeError('Não há CPF de teste disponível na lista. Limpe dados ou ajuste a lista.')
    pcd_profile = PCDProfile.objects.create(
        user=pcd_user,
        cpf=cpf_choice,
        disability='fisica',
        skills='Python, Django',
        lgpd_consent=True,
    )

# 2) Recruiter logs in and creates a job
print("\n[Recruiter] Logging in and creating a job...")
login_resp = client.post('/accounts/login/', {'username': recruiter_email, 'password': password}, follow=True)
print(f"Login status: {login_resp.status_code}")

vaga_title = f"E2E Vaga {datetime.utcnow().isoformat()}"
create_resp = client.post('/recruiter/vagas/new/', {
    'titulo': vaga_title,
    'descricao': 'Descrição E2E de vaga.',
    'requisitos': 'Requisitos E2E: Python, Django.',
}, follow=True)
print(f"Create vaga status: {create_resp.status_code}")

# Find the created job
vaga = Vaga.objects.filter(cnpj_empresa=empresa.cnpj, titulo=vaga_title).order_by('-created_at').first()
assert vaga, "Vaga não foi criada."
print(f"Vaga criada: id={vaga.id}, titulo='{vaga.titulo}'")

# 3) PCD logs in, views job, and applies
print("\n[PCD] Logging in, viewing job, and applying...")
client.get('/accounts/logout/', follow=True)
login_pcd_resp = client.post('/accounts/login/', {'username': pcd_email, 'password': password}, follow=True)
print(f"PCD login status: {login_pcd_resp.status_code}")

vaga_detail_resp = client.get(f'/vagas/{vaga.id}/', follow=True)
print(f"Vaga detail status: {vaga_detail_resp.status_code}")

candidatar_resp = client.post(f'/vagas/{vaga.id}/candidatar/', {}, follow=True)
print(f"Candidatar status: {candidatar_resp.status_code}")

candidatura = Candidatura.objects.filter(vaga=vaga, cpf_pcd=pcd_profile.cpf).order_by('-created_at').first()
assert candidatura, "Candidatura não foi criada."
print(f"Candidatura criada: id={candidatura.id}, cpf={candidatura.cpf_pcd}, status={candidatura.status}")

# 4) Recruiter schedules interview
print("\n[Recruiter] Scheduling interview...")
client.get('/accounts/logout/', follow=True)
login_resp2 = client.post('/accounts/login/', {'username': recruiter_email, 'password': password}, follow=True)
print(f"Recruiter re-login status: {login_resp2.status_code}")

schedule_resp = client.post(f'/recruiter/entrevistas/new/{candidatura.id}/', {
    'data_agendada': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
    'link_video': 'https://meet.example.com/e2e',
    'observacoes': 'Entrevista E2E autogerada.'
}, follow=True)
print(f"Schedule interview status: {schedule_resp.status_code}")

entrevista = Entrevista.objects.filter(candidatura=candidatura).first()
assert entrevista, "Entrevista não foi criada."
print(f"Entrevista criada: id={entrevista.id}, data={entrevista.data_agendada}, link={entrevista.link_video}")

# 5) View interview detail as recruiter and PCD
print("\n[Recruiter] Viewing entrevista detail...")
view_interview_recr = client.get(f'/vagas/entrevistas/{entrevista.id}/', follow=True)
print(f"Recruiter entrevista view status: {view_interview_recr.status_code}")

print("[PCD] Viewing entrevista detail...")
client.get('/accounts/logout/', follow=True)
login_pcd_resp2 = client.post('/accounts/login/', {'username': pcd_email, 'password': password}, follow=True)
view_interview_pcd = client.get(f'/vagas/entrevistas/{entrevista.id}/', follow=True)
print(f"PCD entrevista view status: {view_interview_pcd.status_code}")

print("\n=== E2E Flow Completed Successfully ===")
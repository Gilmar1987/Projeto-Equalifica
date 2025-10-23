#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equalifica_project.settings')
django.setup()

from accounts.models import User, PCDProfile

print("=== Verificação de Perfis PCD ===")
pcd_users = User.objects.filter(user_type='pcd')
print(f"Total de usuários PCD: {pcd_users.count()}")

for user in pcd_users:
    try:
        profile = user.pcd_profile
        print(f"✅ {user.email} - Tem perfil PCD (CPF: {profile.cpf})")
    except PCDProfile.DoesNotExist:
        print(f"❌ {user.email} - NÃO tem perfil PCD")

print("\n=== Verificação de Candidaturas ===")
from recruitment.models import Candidatura
candidaturas = Candidatura.objects.all()
print(f"Total de candidaturas: {candidaturas.count()}")
for candidatura in candidaturas:
    print(f"Candidatura: {candidatura.cpf_pcd} -> {candidatura.vaga.titulo}")
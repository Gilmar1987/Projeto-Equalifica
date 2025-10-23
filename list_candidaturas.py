#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equalifica_project.settings')
django.setup()

from recruitment.models import Candidatura

print("=== Lista de Candidaturas (ID, CPF, Vaga, Status) ===")
for c in Candidatura.objects.select_related('vaga').all():
    print(f"ID={c.id} | CPF={c.cpf_pcd} | Vaga='{c.vaga.titulo}' | Status={c.status}")

print("\nUse um destes IDs na URL: /recruiter/entrevistas/new/<candidatura_id>/")
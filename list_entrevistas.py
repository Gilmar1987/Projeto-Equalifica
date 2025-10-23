#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equalifica_project.settings')
django.setup()

from recruitment.models import Entrevista

print("=== Lista de Entrevistas (ID, CandidaturaID, Vaga, Data, Link) ===")
for e in Entrevista.objects.select_related('candidatura__vaga').all():
    vaga_titulo = e.candidatura.vaga.titulo if e.candidatura and e.candidatura.vaga else '-'
    print(f"ID={e.id} | CandidaturaID={e.candidatura_id} | Vaga='{vaga_titulo}' | Data={e.data_agendada} | Link={e.link_video or '-'}")
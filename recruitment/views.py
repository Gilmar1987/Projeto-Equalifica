# recruitment/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vaga, Candidatura
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Entrevista
from django.core.exceptions import PermissionDenied

def vagas_list(request):
    """Lista pública de todas as vagas (PCD vê todas)"""
    vagas = Vaga.objects.all()
    return render(request, 'recruitment/vagas_list.html', {'vagas': vagas})

def vaga_detail(request, id):
    """Detalhe público de uma vaga"""
    vaga = get_object_or_404(Vaga, id=id)
    ja_candidatado = False
    tem_perfil_pcd = False
    
    if request.user.is_authenticated and request.user.user_type == 'pcd':
        try:
            ja_candidatado = Candidatura.objects.filter(
                vaga=vaga,
                cpf_pcd=request.user.pcd_profile.cpf
            ).exists()
            tem_perfil_pcd = True
        except:
            # Usuário PCD sem perfil - não pode ter se candidatado
            ja_candidatado = False
            tem_perfil_pcd = False
    
    return render(request, 'recruitment/vaga_detail.html', {
        'vaga': vaga,
        'ja_candidatado': ja_candidatado,
        'tem_perfil_pcd': tem_perfil_pcd
    })

@login_required
def candidatar(request, vaga_id):
    """PCD se candidata a uma vaga"""
    if request.user.user_type != 'pcd':
        messages.error(request, "Apenas PCDs podem se candidatar.")
        return redirect('vagas_list')

    # Verificar se o usuário tem perfil PCD
    try:
        cpf_pcd = request.user.pcd_profile.cpf
    except:
        messages.error(request, "Você precisa completar seu perfil PCD antes de se candidatar.")
        return redirect('vaga_detail', id=vaga_id)

    vaga = get_object_or_404(Vaga, id=vaga_id)

    # Evita duplicidade
    if Candidatura.objects.filter(vaga=vaga, cpf_pcd=cpf_pcd).exists():
        messages.warning(request, "Você já se candidatou a esta vaga.")
    else:
        Candidatura.objects.create(
            vaga=vaga,
            cpf_pcd=cpf_pcd,
            cnpj_empresa=vaga.cnpj_empresa
        )
        messages.success(request, "Candidatura realizada com sucesso!")

    return redirect('vaga_detail', id=vaga_id)

login_required
def entrevista_view(request, entrevista_id):
    entrevista = get_object_or_404(
        Entrevista.objects.select_related('candidatura__vaga'),
        id=entrevista_id
    )
    # Verificação de permissão: só PCD da candidatura ou recrutador da empresa
    candidatura = entrevista.candidatura
    user = request.user

    if user.user_type == 'pcd':
        if candidatura.cpf_pcd != user.pcd_profile.cpf:
            raise PermissionDenied("Você não tem acesso a esta entrevista.")
    elif user.user_type == 'recruiter':
        if candidatura.cnpj_empresa != user.recruiter_profile.empresa.cnpj:
            raise PermissionDenied("Você não tem acesso a esta entrevista.")
    else:
        raise PermissionDenied()

    return render(request, 'recruitment/entrevista.html', {
        'entrevista': entrevista,
        'candidatura': candidatura,
    })
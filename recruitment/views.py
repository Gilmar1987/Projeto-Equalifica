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
from .utils import calculate_match_score_from_vectors
from django.contrib.auth import get_user_model

User = get_user_model()

def vagas_list(request):
    """Lista de vagas.
    - PCDs e visitantes veem todas as vagas.
    - Recrutadores veem apenas vagas da sua empresa (isolamento por CNPJ).
    """
    vagas = Vaga.objects.all()
    user = request.user
    if user.is_authenticated and getattr(user, 'user_type', None) == 'recruiter':
        try:
            cnpj = user.recruiter_profile.empresa.cnpj
            vagas = vagas.filter(cnpj_empresa=cnpj)
        except Exception:
            # Sem empresa vinculada ao perfil do recrutador: não mostrar vagas
            vagas = Vaga.objects.none()
    return render(request, 'recruitment/vagas_list.html', {'vagas': vagas})

def vaga_detail(request, id):
    """Detalhe de uma vaga.
    - Público para PCDs e visitantes.
    - Recrutadores só podem ver vagas da sua empresa (isolamento por CNPJ).
    """
    vaga = get_object_or_404(Vaga, id=id)
    # Se for recrutador, aplicar isolamento por CNPJ
    if request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'recruiter':
        try:
            cnpj = request.user.recruiter_profile.empresa.cnpj
            if vaga.cnpj_empresa != cnpj:
                raise PermissionDenied("Você não tem acesso ao detalhe desta vaga.")
        except Exception:
            raise PermissionDenied("Perfil de recrutador sem empresa vinculada.")
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

@login_required
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
    
# Etapas de recomendação Matchmaking  
@login_required
def vagas_recomendadas(request):
    if request.user.user_type != 'pcd':
        return redirect('home')
    
    pcd = request.user.pcd_profile
    vagas = Vaga.objects.all()
    recomendacoes = [
        (vaga, calculate_match_score_from_vectors(vaga, pcd))
        for vaga in vagas
    ]
    recomendacoes = [(v, s) for v, s in recomendacoes if s > 0]
    recomendacoes.sort(key=lambda x: x[1], reverse=True)
    
    return render(request, 'recruitment/vagas_recomendadas.html', {
        'recomendacoes': recomendacoes[:10]
    })

@login_required
def candidatos_recomendados(request, vaga_id):
    if request.user.user_type != 'recruiter':
        return redirect('home')
    
    vaga = get_object_or_404(Vaga, id=vaga_id, cnpj_empresa=request.user.recruiter_profile.empresa.cnpj)
    from accounts.models import PCDProfile
    pcds = PCDProfile.objects.filter(
        user__is_active=True
    )
    
    recomendacoes = []
    for pcd in pcds:
        score = calculate_match_score_from_vectors(vaga, pcd)
        if score > 0:
            recomendacoes.append((pcd.user, score))
    
    recomendacoes.sort(key=lambda x: x[1], reverse=True)
    return render(request, 'recruitment/candidatos_recomendados.html', {
        'vaga': vaga,
        'recomendacoes': recomendacoes[:10]
    })
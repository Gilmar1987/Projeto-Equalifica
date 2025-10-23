# accessibility/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import LogAcessibilidade

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def libras_to_audio(request):
    """
    Simula tradução de Libras (vídeo) para áudio/texto.
    Espera: {"video_url": "https://exemplo.com/video.mp4"} ou {"texto": "Olá"}
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    user = request.user
    cpf_pcd = None
    cnpj_empresa = None

    if user.user_type == 'pcd' and hasattr(user, 'pcd_profile'):
        cpf_pcd = user.pcd_profile.cpf
    elif user.user_type == 'recruiter' and hasattr(user, 'recruiter_profile'):
        cnpj_empresa = user.recruiter_profile.empresa.cnpj
    else:
        return JsonResponse({'error': 'Usuário não autorizado'}, status=403)

    # Simular resultado
    conteudo_original = data.get('video_url') or data.get('texto', '')
    conteudo_traduzido = "Texto traduzido do vídeo em Libras: 'Olá, estou participando da entrevista.'"
    duracao = 10

    # Salvar log
    LogAcessibilidade.objects.create(
        tipo='libras_para_audio',
        cpf_pcd=cpf_pcd or '',
        cnpj_empresa=cnpj_empresa or '',
        conteudo_original=conteudo_original,
        conteudo_traduzido=conteudo_traduzido,
        duracao_segundos=duracao
    )

    return JsonResponse({
        'success': True,
        'tipo': 'libras_para_audio',
        'texto_traduzido': conteudo_traduzido,
        'duracao_segundos': duracao
    })

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def audio_to_libras(request):
    """
    Simula tradução de áudio/texto para Libras (vídeo ou avatar).
    Espera: {"texto": "Olá, meu nome é João"}
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    user = request.user
    cpf_pcd = None
    cnpj_empresa = None

    if user.user_type == 'pcd' and hasattr(user, 'pcd_profile'):
        cpf_pcd = user.pcd_profile.cpf
    elif user.user_type == 'recruiter' and hasattr(user, 'recruiter_profile'):
        cnpj_empresa = user.recruiter_profile.empresa.cnpj
    else:
        return JsonResponse({'error': 'Usuário não autorizado'}, status=403)

    texto = data.get('texto', '')
    if not texto:
        return JsonResponse({'error': 'Campo "texto" é obrigatório'}, status=400)

    # Simular resultado: URL de vídeo gerado ou avatar
    video_libras_url = "https://vlibras.gov.br/mock-video-libras.mp4"

    # Salvar log
    LogAcessibilidade.objects.create(
        tipo='audio_para_libras',
        cpf_pcd=cpf_pcd or '',
        cnpj_empresa=cnpj_empresa or '',
        conteudo_original=texto,
        conteudo_traduzido=video_libras_url,
        duracao_segundos=len(texto.split()) * 2  # estimativa
    )

    return JsonResponse({
        'success': True,
        'tipo': 'audio_para_libras',
        'video_libras_url': video_libras_url,
        'descricao': 'Vídeo em Libras gerado com sucesso'
    })
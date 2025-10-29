# accessibility/views.py
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import LogAcessibilidade
from .whisper_service import transcribe_audio
from django.core.files.storage import default_storage



@csrf_exempt
@login_required
def audio_to_libras(request):
    if 'audio' not in request.FILES:
        return JsonResponse({'error': 'Áudio não enviado'}, status=400)

    audio_file = request.FILES['audio']
    user = request.user
    cpf_pcd = user.pcd_profile.cpf if hasattr(user, 'pcd_profile') else ''
    cnpj_empresa = user.recruiter_profile.empresa.cnpj if hasattr(user, 'recruiter_profile') else ''

    file_name = default_storage.save(f"temp/{audio_file.name}", audio_file)
    file_path = os.path.join(default_storage.location, file_name)

    try:
        texto = transcribe_audio(file_path)
        LogAcessibilidade.objects.create(
            tipo='audio_para_libras',
            cpf_pcd=cpf_pcd,
            cnpj_empresa=cnpj_empresa,
            texto_original=texto
        )
        
         # Salvar log
        LogAcessibilidade.objects.create(
        tipo='audio_para_libras',
        cpf_pcd=cpf_pcd or '',
        cnpj_empresa=cnpj_empresa or '',
        conteudo_original=texto,
        #conteudo_traduzido=video_libras_url,
        duracao_segundos=len(texto.split()) * 2  # estimativa
    )

        return JsonResponse({'texto': texto})
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        default_storage.delete(file_name)
   
   
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .whisper_service import transcribe_audio
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from channels.db import database_sync_to_async
from recruitment.models import Entrevista

class EntrevistaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.entrevista_id = self.scope['url_route']['kwargs']['entrevista_id']
        self.room_group_name = f'entrevista_{self.entrevista_id}'
        self.user = self.scope["user"]

        if not await self.is_user_allowed():
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        # Apenas o recrutador pode enviar áudio
        if self.user.user_type != 'recruiter':
            return

        if bytes_data:
            # Salva o áudio temporariamente
            file_name = f"temp/audio_{self.channel_name}.webm"
            file_path = default_storage.save(file_name, ContentFile(bytes_data))
            full_path = os.path.join(default_storage.location, file_path)

            try:
                # Transcreve o áudio
                texto_transcrito = transcribe_audio(full_path)

                # Envia a mensagem para o grupo
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': texto_transcrito,
                        'sender': self.user.user_type
                    }
                )
            finally:
                # Limpa o arquivo temporário
                default_storage.delete(file_name)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event.get('sender', 'unknown')

        # Envia a mensagem para o WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @database_sync_to_async
    def is_user_allowed(self):
        try:
            entrevista = Entrevista.objects.get(id=self.entrevista_id)
            if self.user.user_type == 'pcd':
                return entrevista.candidatura.cpf_pcd == self.user.pcd_profile
            elif self.user.user_type == 'recruiter':
                return entrevista.candidatura.vaga.cnpj_empresa == self.user.recruiter_profile.empresa
            return False
        except Entrevista.DoesNotExist:
            return False
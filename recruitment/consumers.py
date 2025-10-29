import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Entrevista, Candidatura


class EntrevistaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.entrevista_id = self.scope['url_route']['kwargs']['entrevista_id']
        self.room_group_name = f'entrevista_{self.entrevista_id}'
        
        # Verificar se o usuário tem permissão para acessar esta entrevista
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
            
        has_permission = await self.check_entrevista_permission(user, self.entrevista_id)
        if not has_permission:
            await self.close()
            return

        # Juntar ao grupo da entrevista
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Enviar informações do usuário para o grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': user.id,
                'user_type': 'recruiter' if getattr(user, 'user_type', None) == 'recruiter' else 'pcd',
                'username': getattr(user, 'username', '')
            }
        )

    async def disconnect(self, close_code):
        # Sair do grupo da entrevista
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receber mensagem do WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'audio_transcription':
            # Áudio transcrito do recrutador para o PCD
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'audio_transcription_message',
                    'message': text_data_json['message'],
                    'sender_id': self.scope["user"].id,
                    'sender_type': 'recruiter',
                    'timestamp': text_data_json.get('timestamp')
                }
            )
        elif message_type == 'text_response':
            # Resposta em texto do PCD para o recrutador
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'text_response_message',
                    'message': text_data_json['message'],
                    'sender_id': self.scope["user"].id,
                    'sender_type': 'pcd',
                    'timestamp': text_data_json.get('timestamp')
                }
            )

    # Handlers para diferentes tipos de mensagem
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'user_type': event['user_type'],
            'username': event['username']
        }))

    async def audio_transcription_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'audio_transcription',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_type': event['sender_type'],
            'timestamp': event['timestamp']
        }))

    async def text_response_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'text_response',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_type': event['sender_type'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def check_entrevista_permission(self, user, entrevista_id):
        """Verificar se o usuário tem permissão para acessar esta entrevista"""
        try:
            entrevista = Entrevista.objects.get(id=entrevista_id)

            # Recrutador: empresa do usuário deve coincidir com CNPJ da vaga/candidatura
            if getattr(user, 'user_type', None) == 'recruiter' and hasattr(user, 'recruiter_profile'):
                recruiter_cnpj = getattr(user.recruiter_profile.empresa, 'cnpj', None)
                return recruiter_cnpj == entrevista.candidatura.cnpj_empresa

            # PCD: CPF do perfil deve coincidir com CPF da candidatura
            if getattr(user, 'user_type', None) == 'pcd' and hasattr(user, 'pcd_profile'):
                user_cpf = getattr(user.pcd_profile, 'cpf', None)
                return user_cpf == entrevista.candidatura.cpf_pcd

            return False
        except Entrevista.DoesNotExist:
            return False
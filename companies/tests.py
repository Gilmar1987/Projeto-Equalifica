from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model

from companies.models import Empresa, Recrutador
from recruitment.models import Vaga, Candidatura, Entrevista
from accounts.models import PCDProfile


class RecruiterRoutesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        # Empresa e recrutador
        cls.empresa = Empresa.objects.create(
            cnpj='99.999.999/0001-99', nome='Empresa Teste Rotas', endereco='Rua Rotas 123'
        )
        cls.recruiter_email = 'rotas.recruiter@example.com'
        cls.recruiter_password = 'Test12345!'
        cls.recruiter = cls.User.objects.create_user(
            username='rotas.recruiter', email=cls.recruiter_email, password=cls.recruiter_password, user_type='recruiter'
        )
        cls.recruiter_profile = Recrutador.objects.create(user=cls.recruiter, empresa=cls.empresa)

        # Usuário PCD
        cls.pcd_email = 'rotas.pcd@example.com'
        cls.pcd_password = 'Test12345!'
        cls.pcd_user = cls.User.objects.create_user(
            username='rotas.pcd', email=cls.pcd_email, password=cls.pcd_password, user_type='pcd'
        )
        cls.pcd_profile = PCDProfile.objects.create(
            user=cls.pcd_user,
            cpf='222.333.444-55',
            disability='fisica',
            skills='Django',
            lgpd_consent=True,
        )

    def setUp(self):
        self.client = Client()

    def test_recruiter_dashboard_access(self):
        # Login como recrutador e acessar dashboard
        resp_login = self.client.post('/accounts/login/', {
            'username': self.recruiter_email,
            'password': self.recruiter_password
        }, follow=True)
        self.assertEqual(resp_login.status_code, 200)
        # Acessar diretamente
        resp = self.client.get('/recruiter/dashboard/', follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Dashboard do Recrutador', resp.content)
        self.assertIn(self.empresa.nome.encode(), resp.content)

    def test_pcd_cannot_schedule_interview(self):
        # Cria vaga e candidatura
        vaga = Vaga.objects.create(
            titulo='Vaga Rotas',
            descricao='Desc',
            requisitos='Reqs',
            acessibilidade={},
            cnpj_empresa=self.empresa.cnpj,
        )
        candidatura = Candidatura.objects.create(
            vaga=vaga,
            cpf_pcd=self.pcd_profile.cpf,
            cnpj_empresa=self.empresa.cnpj,
        )

        # Login PCD
        self.client.post('/accounts/login/', {
            'username': self.pcd_email,
            'password': self.pcd_password
        }, follow=True)
        # Tentar agendar entrevista deve redirecionar para dashboard do recrutador com erro
        schedule_resp = self.client.post(f'/recruiter/entrevistas/new/{candidatura.id}/', {
            'data_agendada': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        }, follow=True)
        self.assertEqual(schedule_resp.status_code, 200)
        # Não deve criar entrevista
        self.assertFalse(Entrevista.objects.filter(candidatura=candidatura).exists())

    def test_recruiter_can_schedule_interview(self):
        # Cria vaga e candidatura
        vaga = Vaga.objects.create(
            titulo='Vaga Entrevista',
            descricao='Desc',
            requisitos='Reqs',
            acessibilidade={},
            cnpj_empresa=self.empresa.cnpj,
        )
        candidatura = Candidatura.objects.create(
            vaga=vaga,
            cpf_pcd=self.pcd_profile.cpf,
            cnpj_empresa=self.empresa.cnpj,
        )

        # Login recrutador
        self.client.post('/accounts/login/', {
            'username': self.recruiter_email,
            'password': self.recruiter_password
        }, follow=True)
        # Agendar entrevista
        data_agendada = timezone.now().strftime('%Y-%m-%dT%H:%M')
        schedule_resp = self.client.post(f'/recruiter/entrevistas/new/{candidatura.id}/', {
            'data_agendada': data_agendada,
            'link_video': 'https://meet.example.com/test',
            'observacoes': 'Teste',
        }, follow=True)
        self.assertEqual(schedule_resp.status_code, 200)
        entrevista = Entrevista.objects.filter(candidatura=candidatura).first()
        self.assertIsNotNone(entrevista)
        self.assertEqual(entrevista.link_video, 'https://meet.example.com/test')

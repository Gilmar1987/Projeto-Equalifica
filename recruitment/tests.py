from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime

from companies.models import Empresa, Recrutador
from recruitment.models import Vaga, Candidatura, Entrevista
from accounts.models import PCDProfile


class E2EFlowTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()

        # Empresa e recrutador
        cls.empresa = Empresa.objects.create(
            cnpj='12.345.678/0001-90', nome='Empresa Teste', endereco='Rua Teste 123'
        )
        cls.recruiter_email = 'test.recruiter@example.com'
        cls.recruiter_password = 'Test12345!'
        cls.recruiter = cls.User.objects.create_user(
            username='test.recruiter', email=cls.recruiter_email, password=cls.recruiter_password, user_type='recruiter'
        )
        cls.recruiter_profile = Recrutador.objects.create(user=cls.recruiter, empresa=cls.empresa)

        # Usuário PCD e perfil
        cls.pcd_email = 'test.pcd@example.com'
        cls.pcd_password = 'Test12345!'
        cls.pcd_user = cls.User.objects.create_user(
            username='test.pcd', email=cls.pcd_email, password=cls.pcd_password, user_type='pcd'
        )
        cls.pcd_profile = PCDProfile.objects.create(
            user=cls.pcd_user,
            cpf='111.444.777-35',
            disability='fisica',
            skills='Python, Django',
            lgpd_consent=True,
        )

    def test_full_e2e_flow(self):
        client = Client()

        # 1) Recrutador faz login e cria vaga
        login_resp = client.post('/accounts/login/', {
            'username': self.recruiter_email, 'password': self.recruiter_password
        }, follow=True)
        self.assertEqual(login_resp.status_code, 200, 'Login do recrutador deve retornar 200')

        vaga_title = f"E2E Vaga {datetime.utcnow().isoformat()}"
        create_resp = client.post('/recruiter/vagas/new/', {
            'titulo': vaga_title,
            'descricao': 'Descrição E2E de vaga.',
            'requisitos': 'Requisitos E2E: Python, Django.',
        }, follow=True)
        self.assertEqual(create_resp.status_code, 200, 'Criação de vaga deve retornar 200')

        vaga = Vaga.objects.filter(titulo=vaga_title).order_by('-created_at').first()
        self.assertIsNotNone(vaga, 'Vaga deve ser criada')

        # 2) PCD faz login, visualiza vaga e se candidata
        client.get('/accounts/logout/', follow=True)
        login_pcd_resp = client.post('/accounts/login/', {
            'username': self.pcd_email, 'password': self.pcd_password
        }, follow=True)
        self.assertEqual(login_pcd_resp.status_code, 200, 'Login do PCD deve retornar 200')

        vaga_detail_resp = client.get(f'/vagas/{vaga.id}/', follow=True)
        self.assertEqual(vaga_detail_resp.status_code, 200, 'Detalhe da vaga deve retornar 200')
        self.assertIn(vaga.titulo.encode(), vaga_detail_resp.content, 'Detalhe da vaga deve conter o título')
        # Asserts de UI para PCD: botão de candidatura visível
        self.assertIn(b'Candidatar-se', vaga_detail_resp.content, 'PCD deve ver botão Candidatar-se')
        self.assertIn(f'/vagas/{vaga.id}/candidatar/'.encode(), vaga_detail_resp.content, 'Form de candidatura deve estar presente')
        candidatar_resp = client.post(f'/vagas/{vaga.id}/candidatar/', {}, follow=True)
        self.assertEqual(candidatar_resp.status_code, 200, 'Candidatar deve retornar 200')

        candidatura = Candidatura.objects.filter(vaga=vaga, cpf_pcd=self.pcd_profile.cpf).order_by('-created_at').first()
        self.assertIsNotNone(candidatura, 'Candidatura deve ser criada')
        self.assertEqual(candidatura.status, 'pendente', 'Candidatura deve iniciar como pendente')

        # 3) Recrutador agenda entrevista
        client.get('/accounts/logout/', follow=True)
        re_login_resp = client.post('/accounts/login/', {
            'username': self.recruiter_email, 'password': self.recruiter_password
        }, follow=True)
        self.assertEqual(re_login_resp.status_code, 200, 'Re-login do recrutador deve retornar 200')
        # Asserts de UI para recrutador na lista de vagas: link Criar nova vaga
        vagas_list_resp = client.get('/vagas/', follow=True)
        self.assertEqual(vagas_list_resp.status_code, 200)
        self.assertIn(b'+ Criar nova vaga', vagas_list_resp.content, 'Recrutador deve ver link Criar nova vaga')
        # Asserts de UI para recrutador no detalhe da vaga: não deve ver botão Candidatar-se
        vaga_detail_recr = client.get(f'/vagas/{vaga.id}/', follow=True)
        self.assertEqual(vaga_detail_recr.status_code, 200)
        self.assertNotIn(b'Candidatar-se', vaga_detail_recr.content, 'Recrutador não deve ver botão Candidatar-se')
        self.assertNotIn(f'/vagas/{vaga.id}/candidatar/'.encode(), vaga_detail_recr.content, 'Form de candidatura não deve estar presente para recrutador')

        data_agendada = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        schedule_resp = client.post(f'/recruiter/entrevistas/new/{candidatura.id}/', {
            'data_agendada': data_agendada,
            'link_video': 'https://meet.example.com/e2e',
            'observacoes': 'Entrevista E2E autogerada.'
        }, follow=True)
        self.assertEqual(schedule_resp.status_code, 200, 'Agendamento de entrevista deve retornar 200')

        entrevista = Entrevista.objects.filter(candidatura=candidatura).first()
        self.assertIsNotNone(entrevista, 'Entrevista deve ser criada')
        self.assertEqual(entrevista.link_video, 'https://meet.example.com/e2e', 'Link da entrevista deve ser aplicado')

        # 4) Visualização da entrevista por recrutador e PCD
        view_interview_recr = client.get(f'/vagas/entrevistas/{entrevista.id}/', follow=True)
        self.assertEqual(view_interview_recr.status_code, 200, 'Recrutador deve ver detalhes da entrevista')
        self.assertIn(vaga.titulo.encode(), view_interview_recr.content, 'Template deve conter título da vaga')
        # Asserts de UI entrevista (recrutador): link de voltar ao dashboard e botões de acessibilidade
        self.assertIn(b'Voltar ao Dashboard', view_interview_recr.content)
        self.assertIn(b'/recruiter/dashboard/', view_interview_recr.content)
        self.assertIn('Áudio para Libras'.encode('utf-8'), view_interview_recr.content)
        self.assertIn('Libras para Áudio'.encode('utf-8'), view_interview_recr.content)

        client.get('/accounts/logout/', follow=True)
        re_login_pcd = client.post('/accounts/login/', {
            'username': self.pcd_email, 'password': self.pcd_password
        }, follow=True)
        self.assertEqual(re_login_pcd.status_code, 200, 'Re-login do PCD deve retornar 200')

        view_interview_pcd = client.get(f'/vagas/entrevistas/{entrevista.id}/', follow=True)
        self.assertEqual(view_interview_pcd.status_code, 200, 'PCD deve ver detalhes da entrevista')
        self.assertIn(vaga.titulo.encode(), view_interview_pcd.content, 'Template deve conter título da vaga para PCD')
        # Asserts de UI entrevista (PCD): link de voltar ao dashboard PCD e botões de acessibilidade
        self.assertIn(b'Voltar ao Dashboard', view_interview_pcd.content)
        self.assertIn(b'/pcd/dashboard/', view_interview_pcd.content)
        self.assertIn('Áudio para Libras'.encode('utf-8'), view_interview_pcd.content)
        self.assertIn('Libras para Áudio'.encode('utf-8'), view_interview_pcd.content)

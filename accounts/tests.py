from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        # Cria usuários de cada tipo
        self.recruiter = self.User.objects.create_user(
            username='recruiter.user', email='recruiter@example.com', password='Test12345!', user_type='recruiter'
        )
        from companies.models import Empresa, Recrutador
        self.empresa = Empresa.objects.create(cnpj='00.000.000/0001-00', nome='Empresa X', endereco='Rua X')
        self.recruiter_profile = Recrutador.objects.create(user=self.recruiter, empresa=self.empresa)

        self.pcd = self.User.objects.create_user(
            username='pcd.user', email='pcd@example.com', password='Test12345!', user_type='pcd'
        )
        from accounts.models import PCDProfile
        self.pcd_profile = PCDProfile.objects.create(
            user=self.pcd, cpf='123.456.789-00', disability='fisica', skills='Python', lgpd_consent=True
        )

        self.client = Client()

    def test_login_redirects_to_correct_dashboard(self):
        # Login recrutador
        resp_recruiter = self.client.post('/accounts/login/', {
            'username': 'recruiter@example.com',
            'password': 'Test12345!'
        }, follow=True)
        self.assertEqual(resp_recruiter.status_code, 200)
        # Deve estar no dashboard do recrutador
        self.assertIn(b'Dashboard do Recrutador', resp_recruiter.content)
        self.assertIn('/recruiter/dashboard/', resp_recruiter.request['PATH_INFO'])

        # Logout
        self.client.get('/accounts/logout/', follow=True)

        # Login PCD
        resp_pcd = self.client.post('/accounts/login/', {
            'username': 'pcd@example.com',
            'password': 'Test12345!'
        }, follow=True)
        self.assertEqual(resp_pcd.status_code, 200)
        # Deve estar no dashboard PCD
        self.assertIn(b'Perfil do Candidato PCD', resp_pcd.content)
        self.assertIn('/pcd/dashboard/', resp_pcd.request['PATH_INFO'])

# accounts/views.py
from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from .forms import PCDRegistrationForm
from recruitment.models import Candidatura, Entrevista

# --- Views existentes ---
class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = PCDRegistrationForm
    success_url = reverse_lazy('login')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'pcd':
            return reverse('pcd_dashboard')
        elif user.user_type == 'recruiter':
            return reverse('recruiter_dashboard')
        return '/admin/'

# --- Nova view: Dashboard PCD ---
class PCDDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pcd/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.user_type != 'pcd':
            return context

        cpf_pcd = user.pcd_profile.cpf
        candidaturas = Candidatura.objects.filter(cpf_pcd=cpf_pcd).select_related('vaga')
        entrevistas = Entrevista.objects.filter(
            candidatura__cpf_pcd=cpf_pcd
        ).select_related('candidatura__vaga')

        proxima_entrevista = entrevistas.filter(
            data_agendada__gte=timezone.now()
        ).first()

        context.update({
            'candidaturas': candidaturas,
            'proxima_entrevista': proxima_entrevista,
        })
        return context
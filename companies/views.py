# companies/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from recruitment.models import Vaga, Candidatura
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from recruitment.models import Entrevista

class RecruiterDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'recruiter/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.user_type != 'recruiter':
            return context

        cnpj_empresa = user.recruiter_profile.empresa.cnpj
        vagas = Vaga.objects.filter(cnpj_empresa=cnpj_empresa)
        candidaturas = Candidatura.objects.filter(
            cnpj_empresa=cnpj_empresa
        ).select_related('vaga')

        context.update({
            'vagas': vagas,
            'candidaturas': candidaturas,
            'empresa': user.recruiter_profile.empresa,
        })
        return context


@login_required
def create_vaga(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Apenas recrutadores podem criar vagas.')
        return redirect('recruiter_dashboard')

    empresa = request.user.recruiter_profile.empresa

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        requisitos = request.POST.get('requisitos', '').strip()

        if not titulo:
            messages.error(request, 'Informe o título da vaga.')
        elif not descricao:
            messages.error(request, 'Informe a descrição da vaga.')
        elif not requisitos:
            messages.error(request, 'Informe os requisitos da vaga.')
        else:
            vaga = Vaga.objects.create(
                titulo=titulo,
                descricao=descricao,
                requisitos=requisitos,
                acessibilidade={},
                cnpj_empresa=empresa.cnpj,
            )
            messages.success(request, 'Vaga criada com sucesso!')
            return redirect('recruiter_dashboard')

    return render(request, 'recruitment/vaga_form.html', {
        'empresa': empresa,
    })

@login_required
def schedule_interview(request, candidatura_id):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Apenas recrutadores podem agendar entrevistas.')
        return redirect('recruiter_dashboard')

    empresa = request.user.recruiter_profile.empresa
    candidatura = get_object_or_404(Candidatura, id=candidatura_id)

    # Garantir que a candidatura é da empresa do recrutador
    if candidatura.cnpj_empresa != empresa.cnpj:
        messages.error(request, 'Você não tem permissão para esta candidatura.')
        return redirect('recruiter_dashboard')

    if hasattr(candidatura, 'entrevista'):
        messages.warning(request, 'Esta candidatura já possui entrevista agendada.')
        return redirect('recruiter_dashboard')

    if request.method == 'POST':
        data_agendada_str = request.POST.get('data_agendada')
        link_video = request.POST.get('link_video', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()

        data_agendada = parse_datetime(data_agendada_str) if data_agendada_str else None
        if not data_agendada:
            messages.error(request, 'Informe a data e hora da entrevista.')
        else:
            entrevista = Entrevista.objects.create(
                candidatura=candidatura,
                data_agendada=data_agendada,
                link_video=link_video,
                observacoes=observacoes,
            )
            candidatura.status = 'entrevista'
            candidatura.save(update_fields=['status'])
            messages.success(request, 'Entrevista agendada com sucesso!')
            return redirect('recruiter_dashboard')

    return render(request, 'recruitment/entrevista_form.html', {
        'empresa': empresa,
        'candidatura': candidatura,
    })
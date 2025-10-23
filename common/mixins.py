from django.core.exceptions import PermissionDenied

class AutoPersistMixin:
    """
    Mixin to automatically save the model instance after form validation.
    """

    def perform_create(self, serializer):
        user = self.request.user
        extra_data = {}
        
        if hasattr(user, 'user_type'):
            if user.user_type == 'pcd' and hasattr(user, 'pcd_profile'):
                extra_data['cpf_pcd'] = user.pcd_profile.cpf
            elif user.user_type == 'recruiter' and hasattr(user, 'recruiter_profile'):
                extra_data['cnpj_empresa'] = user.recruiter_profile.empresa.cnpj
                
        #Evita gravação se não for PCD/Recrutador Válido
        if not extra_data and not user.is_staff:
            raise PermissionDenied("Você não tem permissão para criar este registro.")
        
        serializer.save(**extra_data)
              
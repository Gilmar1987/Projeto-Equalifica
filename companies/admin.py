from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import Empresa, Recrutador
from accounts.models import User

# Register your models here.
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'created_at' )
    search_fields = ('nome', 'cnpj')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
    
class RecrutadorAdmin(admin.ModelAdmin):
    list_display = ('user', 'empresa', 'cargo', 'created_at' )
    list_filter = ('empresa',)  
    search_fields = ('user__email', 'empresa__nome', 'cargo')
    readonly_fields = ('created_at', 'updated_at')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs["queryset"] = User.objects.filter(user_type='recruiter')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_add_permission(self, request):
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
    
# Register the admin classes with the associated models
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Recrutador, RecrutadorAdmin)

#Opcional: Remover o modelo Group do admin se não for necessário
admin.site.unregister(Group)
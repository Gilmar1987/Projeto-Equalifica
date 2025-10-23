# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PCDProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Tipo de Usuário', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações', {'fields': ('email', 'user_type')}),
    )
    ordering = ('email',)

@admin.register(PCDProfile)
class PCDProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'disability', 'created_at')
    search_fields = ('cpf', 'user__email')
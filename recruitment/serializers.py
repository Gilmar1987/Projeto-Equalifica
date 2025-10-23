# recruitment/serializers.py
from rest_framework import serializers
from .models import Vaga, Candidatura

class VagaSerializer(serializers.ModelSerializer):
    cnpj_empresa = serializers.CharField(read_only=True)

    class Meta:
        model = Vaga
        fields = '__all__'

class CandidaturaSerializer(serializers.ModelSerializer):
    cpf_pcd = serializers.CharField(read_only=True)
    cnpj_empresa = serializers.CharField(read_only=True)

    class Meta:
        model = Candidatura
        fields = '__all__'
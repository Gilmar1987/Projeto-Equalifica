import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "equalifica_project.settings")
django.setup()

from maching.extractor import preprocess_text, extract_skills, extract_experience, extract_features
from maching.dictionaries import HARD_SKILLS, SOFT_SKILLS, ACESSIBILIDADE_TERMS
from recruitment.models import Vaga
from accounts.models import PCDProfile, User


def print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def test_extractor_functions():
    texto_vaga = (
        "Desenvolvedor Python com 3 anos de experiência. "
        "Conhecimentos em Django, REST, testes unitários e acessibilidade: libras, legendas."
    )

    print_header("Extractor: preprocess, skills, experience, features")
    clean = preprocess_text(texto_vaga)
    print("clean:", clean)

    hs = extract_skills(clean, HARD_SKILLS)
    ss = extract_skills(clean, SOFT_SKILLS)
    ac = extract_skills(clean, ACESSIBILIDADE_TERMS)
    exp = extract_experience(texto_vaga)

    print("hard_skills:", sorted(hs))
    print("soft_skills:", sorted(ss))
    print("acessibilidade:", sorted(ac))
    print("experiencia:", exp)

    feats = extract_features(texto_vaga)
    print("features:", {k: sorted(list(v)) if isinstance(v, set) else v for k, v in feats.items()})


def test_models_save():
    print_header("Models: Vaga.save() e PCDProfile.save() populam vetores")
    # Criar usuário e perfil PCD temporário
    user = User.objects.create(username="tempuser", email="tempuser@example.com")
    pcd = PCDProfile.objects.create(
        user=user,
        cpf="12345678900",
        disability="fisica",
        skills="Django, Python, Trabalho em equipe, libras",
        lgpd_consent=True,
    )
    print("PCDProfile experiencia_total:", pcd.experiencia_total)
    print("PCDProfile hard_skills_vetor:", pcd.hard_skills_vetor)
    print("PCDProfile soft_skills_vetor:", pcd.soft_skills_vetor)
    print("PCDProfile acessibilidade_vetor:", pcd.acessibilidade_vetor)

    # Criar vaga temporária
    vaga = Vaga.objects.create(
        titulo="Dev Python",
        descricao="Precisa de profissional com 2 anos de experiência em Django e REST.",
        requisitos="Testes, boas práticas, trabalho em equipe",
        acessibilidade={"libras": True, "legendas": True},
        cnpj_empresa="00.000.000/0000-00",
    )
    print("Vaga experiencia_minima:", vaga.experiencia_minima)
    print("Vaga hard_skills_vetor:", vaga.hard_skills_vetor)
    print("Vaga soft_skills_vetor:", vaga.soft_skills_vetor)
    print("Vaga acessibilidade_vetor:", vaga.acessibilidade_vetor)

    # limpeza: remover registros temporários
    vaga.delete()
    pcd.delete()
    user.delete()


if __name__ == "__main__":
    test_extractor_functions()
    test_models_save()
    print("\nSmoke test do maching finalizado com sucesso.")
# recruitment/utils.py

def calculate_match_score_from_vectors(vaga, pcd):
    """
    Match rápido usando vetores PRÉ-CALCULADOS.
    """
    # Filtro de corte: acessibilidade
    necessidades = set(pcd.acessibilidade_vetor)
    recursos = set(vaga.acessibilidade_vetor)
    if necessidades and not necessidades.issubset(recursos):
        return 0

    # Match de habilidades
    req_hard = set(vaga.hard_skills_vetor)
    req_soft = set(vaga.soft_skills_vetor)
    cand_hard = set(pcd.hard_skills_vetor)
    cand_soft = set(pcd.soft_skills_vetor)

    hard_match = len(req_hard & cand_hard) / len(req_hard) if req_hard else 1.0
    soft_match = len(req_soft & cand_soft) / len(req_soft) if req_soft else 1.0

    habilidades_score = (0.7 * hard_match + 0.3 * soft_match) * 70
    return min(100, round(habilidades_score + 30))
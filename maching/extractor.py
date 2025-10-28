# recruitment/matching/extractor.py
import re
# Import spaCy apenas quando necessário (lazy loading)
# from .dictionaries import HARD_SKILLS, SOFT_SKILLS, ACESSIBILIDADE_TERMS
from .dictionaries import HARD_SKILLS, SOFT_SKILLS, ACESSIBILIDADE_TERMS

# Variável global para o modelo spaCy
_nlp = None

def _get_nlp():
    """Carrega o modelo spaCy sob demanda (lazy loading)"""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("pt_core_news_sm")
        except (ImportError, OSError):
            # Fallback simples: sem processamento NLP
            # Permite que o app inicie mesmo sem spaCy
            import logging
            logging.warning("spaCy ou modelo pt_core_news_sm não encontrado. Usando fallback simples.")
            _nlp = None
    return _nlp

def preprocess_text(text):
    """Etapa 1: Pré-processamento conforme mach.docx"""
    if not text:
        return ""
    # 1. Lowercasing
    text = text.lower()
    # 2. Limpeza: manter apenas letras e espaços
    text = re.sub(r'[^a-záàâãéèêíïóôõöúçñ\s]', ' ', text)
    
    # 3. Tokenização + remoção de stopwords + lematização (se spaCy disponível)
    nlp = _get_nlp()
    if nlp:
        doc = nlp(text)
        tokens = [
            token.lemma_.strip()
            for token in doc
            if not token.is_stop and not token.is_punct and len(token.lemma_) > 2
        ]
        return " ".join(tokens)
    else:
        # Fallback simples: apenas divide por espaços e filtra palavras curtas
        tokens = [word.strip() for word in text.split() if len(word.strip()) > 2]
        return " ".join(tokens)

def extract_skills(text, skill_set):
    """Extrai habilidades com base em dicionário.
    Suporta termos simples (tokens) e compostos (substrings com espaços).
    """
    if not text:
        return set()
    words = set(text.split())
    matches = set()
    for term in skill_set:
        if ' ' in term:
            # termo composto: match por substring
            if term in text:
                matches.add(term)
        else:
            if term in words:
                matches.add(term)
    return matches

def extract_experience(text):
    """Etapa 2B: Extrai experiência com Regex (anos)."""
    if not text:
        return 0
    # Procura por "X anos" ou "X ano"
    match = re.search(r'(\d+)\s+(?:ano|anos)', text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def extract_features(text):
    """
    Etapa 2: Extração de atributos estruturados a partir de texto livre.
    Retorna dict com sets e valores numéricos.
    """
    clean_text = preprocess_text(text)
    
    return {
        'hard_skills': extract_skills(clean_text, HARD_SKILLS),
        'soft_skills': extract_skills(clean_text, SOFT_SKILLS),
        'acessibilidade': extract_skills(clean_text, ACESSIBILIDADE_TERMS),
        'experiencia': extract_experience(text)  # mantém o texto original para Regex
    }
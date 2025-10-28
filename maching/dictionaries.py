# recruitment/matching/dictionaries.py

# Dicionário de Hard Skills (habilidades técnicas)
HARD_SKILLS = {
    'python', 'django', 'flask', 'javascript', 'typescript', 'react', 'vue', 'angular',
    'html', 'css', 'sass', 'bootstrap', 'tailwind',
    'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
    'git', 'github', 'gitlab', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
    'linux', 'bash', 'shell', 'rest', 'api', 'json', 'xml',
    'excel', 'power bi', 'tableau', 'figma', 'photoshop', 'illustrator',
    'teste', 'qa', 'automacao', 'automatizacao', 'selenium', 'pytest', 'unittest',
    'scrum', 'kanban', 'jira', 'trello'
}

# Dicionário de Soft Skills (comportamentais) — incluir formas sem acento (lemmas)
SOFT_SKILLS = {
    'comunicacao', 'comunicação', 'lideranca', 'liderança', 'proatividade',
    'trabalho', 'equipe', 'colaboracao', 'colaboração', 'resolucao', 'resolução', 'problema', 'problemas',
    'adaptabilidade', 'empatia', 'organizacao', 'organização',
    'pontualidade', 'responsabilidade', 'criatividade', 'iniciativa'
}

# Dicionário de Termos de Acessibilidade — incluir formas lematizadas
ACESSIBILIDADE_TERMS = {
    # Termos simples (lemmas)
    'libra', 'libras', 'legenda', 'legendas',
    'braille', 'rampa', 'elevador', 'banheiro', 'acessivel', 'acessível', 'adaptado', 'adaptada',
    'descricao', 'descrição', 'alternativa', 'alt', 'texto',
    'transcricao', 'transcrição', 'reconhecimento', 'fala', 'voz',
    # Leitores de tela
    'nvda', 'jaws', 'orca', 'narrador',
    # Tipos de deficiência
    'visual', 'auditiva', 'fisica', 'física', 'intelectual', 'multipla', 'múltipla'
}
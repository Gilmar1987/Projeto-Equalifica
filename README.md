
# Equalifica

## Sobre o Equalifica

O **Equalifica** é uma plataforma web open-source voltada para a **inclusão profissional de pessoas com deficiência (PCD)**, conectando talentos a empresas comprometidas com a diversidade. Desenvolvido com foco em **acessibilidade digital**, o sistema oferece suporte nativo a:

- 🖐️ **Tradução automática para Libras** via [**VLibras**](https://vlibras.gov.br/app)  
- 🔊 **Leitura de tela (TTS)** com Web Speech API  
- 📝 **Legendas em tempo real**  
- 🔒 **Isolamento seguro de dados** por perfil (PCD, Recrutador, Admin)

### Tecnologia e Acessibilidade

O Equalifica integra a **Suíte VLibras** — um conjunto de ferramentas de código aberto desenvolvido pelo **Ministério do Planejamento e Gestão (MP)** em parceria com a **Universidade Federal da Paraíba (UFPB)** — que traduz conteúdos digitais (texto, áudio e vídeo) para a **Língua Brasileira de Sinais (Libras)**, tornando a web verdadeiramente acessível para pessoas surdas.

Além disso, a plataforma segue as diretrizes da **LGPD** e das **WCAG**, garantindo privacidade, navegação por teclado, contraste adequado e compatibilidade com leitores de tela.

### Propósito

> **"Acessibilidade não é adaptação — é direito. E talento não tem barreiras."**

O Equalifica nasce para **quebrar barreiras na empregabilidade**, usando tecnologia ética, inteligência artificial responsável e design inclusivo.

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.10+
- Docker e Docker Compose (opcional)
- Git

### Instalação Local

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd ProjetoEqualifica
```

2. **Crie e ative o ambiente virtual:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Execute as migrações:**
```bash
python manage.py migrate
```

6. **Crie um superusuário:**
```bash
python manage.py createsuperuser
```

7. **Inicie o servidor:**
```bash
python manage.py runserver
```

### Instalação com Docker

#### Desenvolvimento (SQLite)
```bash
docker-compose -f docker-compose.dev.yml up --build
```

#### Produção (PostgreSQL + Redis + Celery)
```bash
docker-compose up --build
```

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django 5.2, Django REST Framework
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados:** SQLite (dev), PostgreSQL (prod)
- **Cache/Queue:** Redis, Celery
- **Containerização:** Docker, Docker Compose
- **IA/ML:** spaCy, OpenAI Whisper
- **Acessibilidade:** VLibras, Web Speech API

## 📁 Estrutura do Projeto

```
ProjetoEqualifica/
├── accounts/          # Autenticação e perfis de usuário
├── companies/         # Gestão de empresas e recrutadores
├── recruitment/       # Vagas e processo seletivo
├── accessibility/     # Recursos de acessibilidade
├── maching/          # Sistema de matching IA
├── templates/        # Templates HTML
├── static/           # Arquivos estáticos
├── requirements.txt  # Dependências Python
├── docker-compose.yml # Configuração Docker (produção)
├── docker-compose.dev.yml # Configuração Docker (desenvolvimento)
└── .env.example      # Exemplo de variáveis de ambiente
```

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

- `DEBUG`: True para desenvolvimento
- `SECRET_KEY`: Chave secreta do Django
- `DATABASE_URL`: URL do banco de dados
- `REDIS_URL`: URL do Redis (para cache e Celery)
- `EMAIL_*`: Configurações de email para recuperação de senha

### Comandos Úteis

```bash
# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Executar Celery (em terminal separado)
celery -A equalifica_project worker --loglevel=info
```

## 🌐 Acesso ao Sistema

- **Aplicação:** http://localhost:8000
- **Admin Django:** http://localhost:8000/admin
- **API REST:** http://localhost:8000/api/ (se configurada)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte, entre em contato através dos issues do GitHub.

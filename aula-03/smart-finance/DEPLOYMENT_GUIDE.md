# Guia de Implantação (Deployment) - SmartFinance

Este guia descreve os passos gerais para implantação da aplicação em ambientes de produção (ex: Heroku, Render, AWS, Railway).

## Pré-requisitos

Certifique-se de que o provedor suporte:

- Python >= 3.12
- PostgreSQL
- NodeJS (para compilação do Tailwind, embora a recomendação seja compilar no pipeline CI/CD).

## Variáveis de Ambiente de Produção

No ambiente de produção, configure as variáveis sensíveis. O arquivo `.env` **nunca** deve ser commitado no repositório.

- `DEBUG`: Deve ser **sempre** configurado como `False` (`DEBUG=False`).
- `SECRET_KEY`: Gere uma chave segura aleatória e armazene.
- `ALLOWED_HOSTS`: Domínios permitidos (ex: `.smartfinance.com.br, smartfinance.onrender.com`).
- `DATABASE_URL`: String de conexão fornecida pelo serviço do PostgreSQL (ex: Heroku Postgres, Supabase).
- `GROQ_API_KEY`: Chave da API usada para os serviços de Inteligência Artificial.

## Compilação de Assets Estáticos

### 1. Tailwind CSS

O Tailwind precisa gerar o arquivo CSS final minimizado para uso em produção. No processo de build, você deve executar:

```bash
uv run manage.py tailwind build
```

Este comando criará uma versão otimizada dos seus estilos. Se você não conseguir executar o NodeJS no seu servidor final, você pode rodar este comando localmente e enviar o CSS buildado, mas a prática recomendada é realizar este processo no container/pipeline (Docker, Github Actions, ou Render build script).

### 2. Arquivos Estáticos (Collectstatic)

Depois de gerar o CSS, o Django precisa coletar todos os arquivos estáticos:

```bash
uv run manage.py collectstatic --noinput
```

*(Lembre-se de configurar e usar bibliotecas como `whitenoise` em middlewares se quiser que a aplicação Django sirva arquivos estáticos em produção diretamente)*

## Migrações de Banco de Dados

Ao realizar a implantação ou ao atualizar o código no servidor, não se esqueça de aplicar as migrações:

```bash
uv run manage.py migrate
```

## Servidor Web Recomendado

Não utilize o `runserver` padrão do Django em produção. Utilize um servidor WSGI compatível para Python:

Exemplo usando **Gunicorn**:

```bash
uv pip install gunicorn
uv run gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```

## Resumo: Exemplo de Script de Build (Render/Railway)

Um script de build típico (`build.sh`) na raiz do projeto se pareceria com:

```bash
#!/usr/bin/env bash
# Saia no primeiro erro
set -o errexit

# Instalação rápida via UV
pip install uv
uv sync

# Construir os estilos finais do Tailwind
cd aula-03/smart-finance
uv run manage.py tailwind build

# Coletar estáticos e migrar banco
uv run manage.py collectstatic --no-input
uv run manage.py migrate
```

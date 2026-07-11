# Guia de Desenvolvimento - SmartFinance

## Visão Geral

SmartFinance é uma aplicação financeira em Django que ajuda usuários a controlarem receitas, despesas e obter insights através de Inteligência Artificial usando Groq.

## Tecnologias Principais

- **Backend:** Django 5.0+, Python 3.12+
- **Frontend:** Tailwind CSS v4, Vanilla JavaScript
- **Banco de Dados:** PostgreSQL (via psycopg2)
- **Gerenciamento de Dependências:** [uv](https://github.com/astral-sh/uv)
- **IA:** Integração com LLMs usando `groq`

## Configuração do Ambiente

1. **Clonar e Inicializar o Ambiente**
   O projeto utiliza `uv` para gerenciar dependências de forma rápida e eficiente.
   Na pasta raiz do repositório (`curso-python-smart-finance`), sincronize as dependências:

   ```bash
   uv sync
   ```

   Isso criará automaticamente o ambiente virtual (`.venv`) e instalará as bibliotecas necessárias.

2. **Ativação do Ambiente Virtual**
   Para ativar o ambiente virtual:
   - No Windows: `.\.venv\Scripts\activate`
   - No Linux/Mac: `source .venv/bin/activate`

3. **Configuração de Variáveis de Ambiente**
   Crie um arquivo `.env` na raiz do projeto Django (`aula-03/smart-finance`) com as seguintes variáveis:

   ```env
   SECRET_KEY=sua_secret_key
   DEBUG=True
   GROQ_API_KEY=sua_chave_groq
   DATABASE_URL=postgres://user:password@localhost:5432/smartfinance
   ```

4. **Migrações de Banco de Dados**
   Com o ambiente ativado, execute as migrações:

   ```bash
   uv run manage.py migrate
   ```

5. **Configuração do Tailwind CSS (Tema Frontend)**
   O projeto usa a biblioteca `django-tailwind` configurada no app `theme`.
   Para instalar as dependências do NodeJS necessárias para o Tailwind (execute dentro de `aula-03/smart-finance`):

   ```bash
   uv run manage.py tailwind install
   ```

6. **Geração de Arquivos Estáticos (Deploy/Produção)**
   O diretório `staticfiles/` não é versionado pelo Git (conforme configurado no `.gitignore`).
   Antes de realizar o deploy ou para testar os estáticos localmente em modo de produção, você precisará gerar o CSS minimizado do Tailwind e então coletar todos os arquivos estáticos do Django:

   ```bash
   # Construir o CSS final do Tailwind
   uv run manage.py tailwind build

   # Coletar os arquivos estáticos
   uv run manage.py collectstatic --no-input
   ```

## Fluxo de Desenvolvimento Local

Para executar o ambiente localmente de forma otimizada (servidor Django + compilação automática do Tailwind), recomendamos executar dois processos paralelos:

1. **Iniciar o servidor do Django:**

   ```bash
   uv run manage.py runserver
   ```

2. **Iniciar o watcher do Tailwind CSS (em outro terminal):**

   ```bash
   uv run manage.py tailwind start
   ```

Isso garantirá que as alterações feitas nos arquivos `.html` apliquem o Tailwind automaticamente através do `django_browser_reload`.

## Estrutura de Pastas e Aplicativos

- `core/`: Configurações principais do projeto (settings.py, urls.py).
- `dashboard/`: Páginas iniciais, resumos métricos e relatórios visuais (gráficos).
- `finance/`: Modelos e lógicas para gerenciar transações (receitas e despesas).
- `intelligence/`: Integração com serviços de LLM (Groq) e insights financeiros da IA.
- `users/`: Gerenciamento de autenticação, login e cadastro de usuários.
- `theme/`: O app base do `django-tailwind` que contém a base de CSS (`styles.css`) e configurações do Frontend.

## Padrões de Código e Linting

O projeto inclui regras de linting para qualidade do código:

- Utilize o `pre-commit` para validar alterações antes de commitar.
- `djlint` é usado para linters de templates HTML (ajusta padronização do Django Template).
- Utilize o modo escuro (`dark mode`) do Tailwind gerenciado com a classe seletora `.dark` na flag root, conforme configurado em `theme/static_src/src/styles.css`.

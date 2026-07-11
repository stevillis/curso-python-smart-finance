import os
import json
import ast
import operator
from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from dotenv import load_dotenv, find_dotenv
from groq import Groq
from finance.models import Transaction

load_dotenv(find_dotenv())


def evaluate_math_expression(expr):
    """Safely evaluates a basic mathematical expression string."""
    try:
        if not expr:
            return 0.0

        # Replace comma with dot for Brazilian decimal formatting if needed
        expr = str(expr).replace(",", ".")

        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
        }

        def eval_node(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                return operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                return operators[type(node.op)](operand)
            else:
                raise TypeError(node)

        node = ast.parse(expr, mode="eval").body
        return float(eval_node(node))
    except Exception:
        return 0.0


@login_required(login_url="/users/login/")
def chat_view(request):
    return render(request, "chat.html")


@login_required(login_url="/users/login/")
def quick_add_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método inválido"}, status=400)

    user_message = request.POST.get("message", "")
    today = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""
Você é o SmartFinance AI, assistente financeiro.
Sua principal tarefa é extrair registros financeiros (gastos ou ganhos) da mensagem do usuário.
O usuário pode enviar uma única transação (ex: "ganhei 50 reais de mesada", "gastei 20 no ifood") ou uma lista de itens de uma compra (ex: "tomate: 2.75, cenoura: 3.75, bolacha: 3.99*4").

NÃO faça o cálculo matemático final. Em vez disso, retorne a expressão matemática exata no campo "math_expression" (ex: "3.99 * 4" ou "50").
ATENÇÃO: O campo "math_expression" DEVE conter APENAS números, pontos e operadores matemáticos válidos (*, /, +, -). NÃO inclua palavras, símbolos de moeda (R$, $) ou textos como "reais".

Você DEVE classificar cada item em uma das seguintes categorias: "Salário", "Alimentação", "Transporte", "Lazer", "Moradia" ou "Outros".
O campo "type" DEVE ser "despesa" (para gastos/compras) ou "receita" (para ganhos/dinheiro recebido).

Retorne SEMPRE um JSON com a seguinte estrutura:
{{
  "transactions": [
    {{
      "description": "Nome do item ou origem do ganho",
      "math_expression": "Valor exato sem texto (ex: 2.75 ou 50)",
      "date": "{today}",
      "category": "Alimentação",
      "type": "despesa ou receita"
    }}
  ],
  "reply": "Sua resposta amigável de confirmação. (Use HTML para formatar, ex: <b>negrito</b>)"
}}

Se a mensagem não contiver NENHUMA intenção de registro financeiro, retorne a lista "transactions" vazia e responda amigavelmente em "reply".
"""

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        return JsonResponse(
            {
                "reply": (
                    "Erro: configure a variável de ambiente GROQ_API_KEY com "
                    "sua chave da Groq para usar o Agente Financeiro IA."
                )
            },
            status=503,
        )

    try:
        client = Groq(api_key=groq_api_key)

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        transactions_data = result.get("transactions", [])

        created_transactions = []
        total_amount = 0.0

        for tx_data in transactions_data:
            amount = evaluate_math_expression(tx_data.get("math_expression", "0"))

            # Ignore 0 or negative values as requested
            if amount <= 0:
                continue

            total_amount += amount

            tx = Transaction.objects.create(
                user=request.user,
                description=tx_data.get("description", "Automático").title(),
                amount=amount,
                date=tx_data.get("date", today),
                category=tx_data.get("category", "Outros"),
                type=tx_data.get("type", "despesa"),
            )

            # Ensure date is a datetime object for consistent formatting
            date_str = str(tx.date)
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d %b %Y")
            except ValueError:
                formatted_date = date_str

            created_transactions.append(
                {
                    "id": tx.id,
                    "description": tx.description,
                    "amount": float(tx.amount),
                    "date": formatted_date,
                    "category": tx.category,
                    "type": tx.type,
                }
            )

        ai_reply = result.get("reply", "")

        if created_transactions:
            ai_reply += f"<br><br><b>Total Registrado:</b> R$ {total_amount:.2f}"

        return JsonResponse({"reply": ai_reply, "transactions": created_transactions})

    except Exception as e:
        return JsonResponse({"reply": f"Erro: {str(e)}"})


@login_required(login_url="/users/login/")
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método inválido"}, status=400)

    user_message = request.POST.get("message", "")

    system_prompt = f"""
Você é o SmartFinance AI, um analista financeiro de dados mestre em SQL (PostgreSQL).
Sua tarefa é analisar a solicitação do usuário e gerar uma query SQL para encontrar a resposta exata.

O banco de dados possui a tabela `finance_transaction`.
Esquema da tabela:
- id (INTEGER)
- user_id (INTEGER) - ID do usuário. Sempre filtre por este campo!
- description (VARCHAR) - Descrição do item (ex: 'Tomate', 'Bolacha')
- amount (DECIMAL) - Valor da transação
- date (DATE) - Data da transação no formato YYYY-MM-DD
- category (VARCHAR) - Categoria (ex: 'Alimentação', 'Lazer')
- type (VARCHAR) - Tipo ('receita' ou 'despesa')

Você DEVE retornar um JSON rigorosamente com a seguinte estrutura:
{{
  "query": "Sua query SQL começando com SELECT. EXTREMAMENTE IMPORTANTE: Você DEVE incluir a cláusula WHERE user_id = {{user_id}} para segurança. (ex: SELECT SUM(amount) FROM finance_transaction WHERE user_id = {{user_id}} AND description ILIKE '%tomate%')",
  "reply": "O texto da sua resposta em formato amigável (use HTML para formatar, ex: <b>negrito</b>, <br>). Use a tag {{result}} onde o resultado numérico da query deve ser injetado. (ex: Você gastou um total de <b>R$ {{result}}</b> com tomate.)"
}}

Se a pergunta não precisar de uma consulta ao banco de dados, deixe "query" vazio ("") e responda normalmente em "reply".
Sempre faça buscas insensíveis a maiúsculas/minúsculas usando ILIKE '%termo%' quando procurar por descrições.
"""

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        return JsonResponse(
            {"reply": "Erro: configure a variável GROQ_API_KEY."}, status=503
        )

    try:
        client = Groq(api_key=groq_api_key)

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        query = result.get("query", "").strip()
        ai_reply = result.get("reply", "Desculpe, não consegui processar a resposta.")

        if query:
            # Basic SQL injection protection: Ensure it's a SELECT query
            if not query.upper().startswith("SELECT"):
                return JsonResponse(
                    {
                        "reply": "<b>Erro de Segurança:</b> Apenas consultas de leitura (SELECT) são permitidas.",
                        "transactions": [],
                    }
                )

            # Inject tenancy
            query = query.replace("{user_id}", str(request.user.id))

            # Execute query securely
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    row = cursor.fetchone()

                    if row and row[0] is not None:
                        val = row[0]
                        if isinstance(val, (int, float)):
                            # Format nicely to Brazilian currency style
                            val_str = (
                                f"{val:,.2f}".replace(",", "X")
                                .replace(".", ",")
                                .replace("X", ".")
                            )
                        else:
                            val_str = str(val)
                    else:
                        val_str = "0,00"

                    ai_reply = ai_reply.replace("{result}", val_str)
            except Exception as e:
                ai_reply = f"<b>Erro ao consultar banco de dados:</b> {str(e)}<br><small>Query gerada: {query}</small>"

        return JsonResponse({"reply": ai_reply, "transactions": []})

    except Exception as e:
        return JsonResponse({"reply": f"Erro: {str(e)}"})

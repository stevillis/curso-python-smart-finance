import json
import os
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from intelligence.views import (
    chat_api,
    quick_add_api,
    chat_view,
    evaluate_math_expression,
)
from finance.models import Transaction


class MathExpressionTests(TestCase):
    def test_evaluate_math_expression(self):
        self.assertEqual(evaluate_math_expression("2 + 2"), 4.0)
        self.assertEqual(evaluate_math_expression("10.5 - 2.5"), 8.0)
        self.assertEqual(evaluate_math_expression("3 * 4"), 12.0)
        self.assertEqual(evaluate_math_expression("10 / 2"), 5.0)
        self.assertEqual(evaluate_math_expression("-5 + 10"), 5.0)
        self.assertEqual(evaluate_math_expression("3.99 * 4"), 15.96)

        # Test comma replacing
        self.assertEqual(evaluate_math_expression("3,99 * 4"), 15.96)

        # Test empty or invalid
        self.assertEqual(evaluate_math_expression(""), 0.0)
        self.assertEqual(evaluate_math_expression("invalid"), 0.0)
        self.assertEqual(evaluate_math_expression(None), 0.0)


class IntelligenceViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="secret123",
        )

    def test_chat_view(self):
        request = self.factory.get("/intelligence/chat/")
        request.user = self.user
        response = chat_view(request)
        self.assertEqual(response.status_code, 200)

    @patch.dict(os.environ, {}, clear=True)
    def test_returns_clear_error_when_groq_key_is_missing(self):
        request = self.factory.post("/intelligence/api/chat/", {"message": "teste"})
        request.user = self.user

        response = chat_api(request)

        self.assertEqual(response.status_code, 503)
        payload = json.loads(response.content)
        self.assertIn("GROQ_API_KEY", payload["reply"])

    @patch.dict(os.environ, {}, clear=True)
    def test_quick_add_returns_clear_error_when_groq_key_is_missing(self):
        request = self.factory.post(
            "/intelligence/api/quick-add/", {"message": "teste"}
        )
        request.user = self.user

        response = quick_add_api(request)

        self.assertEqual(response.status_code, 503)
        payload = json.loads(response.content)
        self.assertIn("GROQ_API_KEY", payload["reply"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    def test_quick_add_api_invalid_method(self):
        request = self.factory.get("/intelligence/api/quick-add/")
        request.user = self.user
        response = quick_add_api(request)
        self.assertEqual(response.status_code, 400)

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_quick_add_api_success(self, MockGroq):
        mock_client = MagicMock()
        MockGroq.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "transactions": [
                                {
                                    "description": "Tomate",
                                    "math_expression": "2.50 * 2",
                                    "date": "2026-07-10",
                                    "category": "Alimentação",
                                    "type": "despesa",
                                },
                                {
                                    "description": "Zero",
                                    "math_expression": "0",
                                    "date": "2026-07-10",
                                    "category": "Outros",
                                    "type": "despesa",
                                },
                                {
                                    "description": "Sem Data",
                                    "math_expression": "10",
                                    "category": "Outros",
                                    "type": "despesa",
                                },
                            ],
                            "reply": "Transação registrada",
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        request = self.factory.post(
            "/intelligence/api/quick-add/", {"message": "comprei tomate 2.50 * 2"}
        )
        request.user = self.user

        response = quick_add_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Transação registrada", payload["reply"])
        self.assertIn("Total Registrado:", payload["reply"])

        self.assertEqual(len(payload["transactions"]), 2)  # Zero amount ignored
        self.assertEqual(payload["transactions"][0]["amount"], 5.0)

        # Check DB
        self.assertEqual(Transaction.objects.count(), 2)
        tx = Transaction.objects.get(description="Tomate")
        self.assertEqual(tx.amount, 5.0)

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_quick_add_api_exception(self, MockGroq):
        mock_client = MagicMock()
        MockGroq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        request = self.factory.post(
            "/intelligence/api/quick-add/", {"message": "teste"}
        )
        request.user = self.user

        response = quick_add_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Erro: API Error", payload["reply"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    def test_chat_api_invalid_method(self):
        request = self.factory.get("/intelligence/api/chat/")
        request.user = self.user
        response = chat_api(request)
        self.assertEqual(response.status_code, 400)

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_chat_api_success(self, MockGroq):
        Transaction.objects.create(
            user=self.user,
            description="Tomate",
            amount=10.0,
            date="2026-07-10",
            category="Alimentação",
            type="despesa",
        )

        mock_client = MagicMock()
        MockGroq.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "query": "SELECT SUM(amount) FROM finance_transaction WHERE user_id = {user_id}",
                            "reply": "Total é {result}",
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        request = self.factory.post(
            "/intelligence/api/chat/", {"message": "qual meu total?"}
        )
        request.user = self.user

        response = chat_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Total é 10,00", payload["reply"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_chat_api_success_no_result(self, MockGroq):
        mock_client = MagicMock()
        MockGroq.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "query": "SELECT SUM(amount) FROM finance_transaction WHERE user_id = {user_id}",
                            "reply": "Total é {result}",
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        request = self.factory.post(
            "/intelligence/api/chat/", {"message": "qual meu total?"}
        )
        request.user = self.user

        response = chat_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Total é 0,00", payload["reply"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_chat_api_success_string_result(self, MockGroq):
        mock_client = MagicMock()
        MockGroq.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "query": "SELECT description FROM finance_transaction WHERE user_id = {user_id}",
                            "reply": "Descrição é {result}",
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        Transaction.objects.create(
            user=self.user,
            description="Tomate",
            amount=10.0,
            date="2026-07-10",
            category="Alimentação",
            type="despesa",
        )

        request = self.factory.post("/intelligence/api/chat/", {"message": "teste?"})
        request.user = self.user

        response = chat_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Descrição é Tomate", payload["reply"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_chat_api_security_error(self, MockGroq):
        mock_client = MagicMock()
        MockGroq.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "query": "DROP TABLE finance_transaction",
                            "reply": "Tabela deletada",
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        request = self.factory.post(
            "/intelligence/api/chat/", {"message": "deleta tudo"}
        )
        request.user = self.user

        response = chat_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Erro de Segurança", payload["reply"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_chat_api_db_error(self, MockGroq):
        mock_client = MagicMock()
        MockGroq.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "query": "SELECT SUM(non_existent_column) FROM finance_transaction WHERE user_id = {user_id}",
                            "reply": "Total é {result}",
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        request = self.factory.post(
            "/intelligence/api/chat/", {"message": "qual meu total?"}
        )
        request.user = self.user

        response = chat_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Erro ao consultar banco de dados", payload["reply"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}, clear=True)
    @patch("intelligence.views.Groq")
    def test_chat_api_exception(self, MockGroq):
        mock_client = MagicMock()
        MockGroq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        request = self.factory.post("/intelligence/api/chat/", {"message": "teste"})
        request.user = self.user

        response = chat_api(request)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("Erro: API Error", payload["reply"])

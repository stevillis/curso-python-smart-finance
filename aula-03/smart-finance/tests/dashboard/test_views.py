from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from finance.models import Transaction


class DashboardViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.login_url = reverse("users:login")

    def test_home_redirects_if_not_logged_in(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(
            response, f"{self.login_url}?next={reverse('dashboard:home')}"
        )

    def test_home_view(self):
        self.client.login(username="testuser", password="testpassword")
        Transaction.objects.create(
            user=self.user,
            description="Salary",
            amount=1000,
            date="2023-01-01",
            category="Income",
            type="receita",
        )
        Transaction.objects.create(
            user=self.user,
            description="Food",
            amount=200,
            date="2023-01-02",
            category="Expense",
            type="despesa",
        )

        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertEqual(response.context["total_income"], 1000)
        self.assertEqual(response.context["total_expense"], 200)
        self.assertEqual(response.context["current_balance"], 800)

    def test_insight_api_with_expenses(self):
        self.client.login(username="testuser", password="testpassword")
        Transaction.objects.create(
            user=self.user,
            description="Salary",
            amount=1000,
            date="2023-01-01",
            category="Income",
            type="receita",
        )
        Transaction.objects.create(
            user=self.user,
            description="Food",
            amount=200,
            date="2023-01-02",
            category="Expense",
            type="despesa",
        )
        response = self.client.get(reverse("dashboard:insight"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Você gastou 20.0% das receitas.", response.json()["insight"])

    def test_insight_api_no_transactions(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("dashboard:insight"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["insight"], "Registre algumas transações para análise."
        )

    def test_insight_api_expenses_greater_than_income(self):
        self.client.login(username="testuser", password="testpassword")
        Transaction.objects.create(
            user=self.user,
            description="Salary",
            amount=100,
            date="2023-01-01",
            category="Income",
            type="receita",
        )
        Transaction.objects.create(
            user=self.user,
            description="TV",
            amount=200,
            date="2023-01-02",
            category="Expense",
            type="despesa",
        )
        response = self.client.get(reverse("dashboard:insight"))
        self.assertIn("Atenção: Suas despesas > receitas!", response.json()["insight"])

    def test_insight_api_no_expenses(self):
        self.client.login(username="testuser", password="testpassword")
        Transaction.objects.create(
            user=self.user,
            description="Salary",
            amount=1000,
            date="2023-01-01",
            category="Income",
            type="receita",
        )
        response = self.client.get(reverse("dashboard:insight"))
        self.assertIn("Sem despesas registradas!", response.json()["insight"])

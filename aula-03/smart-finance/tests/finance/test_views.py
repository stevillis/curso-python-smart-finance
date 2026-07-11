from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from finance.models import Transaction


class FinanceViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.login_url = reverse("users:login")

    def test_finance_list_redirects_if_not_logged_in(self):
        response = self.client.get(reverse("finance:list"))
        self.assertRedirects(
            response, f"{self.login_url}?next={reverse('finance:list')}"
        )

    def test_finance_list_view(self):
        self.client.login(username="testuser", password="testpassword")
        Transaction.objects.create(
            user=self.user,
            description="Salary",
            amount=1000,
            date="2023-01-01",
            category="Income",
            type="receita",
        )
        response = self.client.get(reverse("finance:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "finance_list.html")
        self.assertEqual(len(response.context["transactions"]), 1)

    def test_finance_add_get(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("finance:add"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "finance_add.html")

    def test_finance_add_post(self):
        self.client.login(username="testuser", password="testpassword")
        data = {
            "description": "Freelance",
            "amount": "500.00",
            "date": "2023-01-10",
            "category": "Job",
            "type": "receita",
        }
        response = self.client.post(reverse("finance:add"), data)
        self.assertRedirects(response, reverse("dashboard:home"))
        self.assertEqual(Transaction.objects.count(), 1)

    def test_finance_list_filters(self):
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

        # Test search filter
        response = self.client.get(reverse("finance:list") + "?search=Food")
        self.assertEqual(len(response.context["transactions"]), 1)
        self.assertEqual(response.context["transactions"][0].description, "Food")

        # Test type filter
        response = self.client.get(reverse("finance:list") + "?type=receita")
        self.assertEqual(len(response.context["transactions"]), 1)
        self.assertEqual(response.context["transactions"][0].type, "receita")

        # Test start_date filter
        response = self.client.get(reverse("finance:list") + "?start_date=2023-01-02")
        self.assertEqual(len(response.context["transactions"]), 1)
        self.assertEqual(
            response.context["transactions"][0].date.strftime("%Y-%m-%d"), "2023-01-02"
        )

        # Test end_date filter
        response = self.client.get(reverse("finance:list") + "?end_date=2023-01-01")
        self.assertEqual(len(response.context["transactions"]), 1)
        self.assertEqual(
            response.context["transactions"][0].date.strftime("%Y-%m-%d"), "2023-01-01"
        )

    def test_finance_list_ajax(self):
        self.client.login(username="testuser", password="testpassword")
        Transaction.objects.create(
            user=self.user,
            description="Salary",
            amount=1000,
            date="2023-01-01",
            category="Income",
            type="receita",
        )

        response = self.client.get(reverse("finance:list") + "?ajax=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transactions", data)
        self.assertEqual(len(data["transactions"]), 1)
        self.assertEqual(data["transactions"][0]["description"], "Salary")
        self.assertIn("pagination", data)


class FinanceModelsTests(TestCase):
    def test_transaction_str(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        tx = Transaction(
            user=user,
            description="Salary",
            amount="1000.00",
            date="2023-01-01",
            category="Income",
            type="receita",
        )
        self.assertEqual(str(tx), "Salary - R$ 1000.00")

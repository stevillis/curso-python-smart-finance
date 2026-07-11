from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch


class UsersViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_login_view_get(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_view_post_success(self):
        response = self.client.post(
            reverse("users:login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_login_view_redirects_if_authenticated(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("users:login"))
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_register_view_get(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_logout_view(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, reverse("users:login"))

    def test_login_view_post_invalid(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Usuário ou senha inválidos.")

    def test_register_view_redirects_if_authenticated(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("users:register"))
        self.assertRedirects(response, reverse("dashboard:home"))

    @patch("users.views.UserCreationForm")
    def test_register_view_post_success(self, MockForm):
        mock_form_instance = MockForm.return_value
        mock_form_instance.is_valid.return_value = True
        new_user = User.objects.create_user(username="newuser", password="newpassword")
        mock_form_instance.save.return_value = new_user

        response = self.client.post(reverse("users:register"), {"some": "data"})
        self.assertRedirects(response, reverse("dashboard:home"))

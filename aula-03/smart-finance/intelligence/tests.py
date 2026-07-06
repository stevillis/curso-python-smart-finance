import json
import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import chat_api


class ChatApiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="secret123",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_returns_clear_error_when_groq_key_is_missing(self):
        request = self.factory.post("/intelligence/api/chat/", {"message": "teste"})
        request.user = self.user

        response = chat_api(request)

        self.assertEqual(response.status_code, 503)
        payload = json.loads(response.content)
        self.assertIn("GROQ_API_KEY", payload["reply"])

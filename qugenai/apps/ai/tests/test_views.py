import json
import re
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from django.urls import reverse

from qugenai.apps.ai.forms import QGenForm

pytestmark = pytest.mark.django_db

HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_FOUND = 302
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500


class TestGenerateExamQuestionsView:
    def test_generate_exam_questions_get(self, client, user):
        client.force_login(user)
        response = client.get(reverse("ai:generate_exam_questions"))
        assert response.status_code == HTTP_STATUS_OK
        context = response.context
        assert "form" in context
        assert isinstance(context["form"], QGenForm)
        assert context["exam_questions"] is None

    def test_generate_exam_questions_post_invalid_form(self, client, user):
        client.force_login(user)
        data = {"subject": ""}
        response = client.post(reverse("ai:generate_exam_questions"), data)
        assert response.status_code == HTTP_STATUS_BAD_REQUEST
        assert json.loads(response.content) == {"error": "Invalid form data"}

    def test_generate_exam_questions_post_not_logged_in(self, client):
        response = client.post(reverse("ai:generate_exam_questions"))
        assert response.status_code == HTTP_STATUS_FOUND
        assert re.match(r"^/accounts/login/\?next=", response.url)

    @patch("qugenai.apps.ai.views.client.beta.chat.completions.parse")
    def test_generate_exam_questions_api_refusal(self, mock_parse, client, user):
        client.force_login(user)
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(refusal="Content violation")),
        ]
        mock_parse.return_value = mock_response

        data = {"subject": "Math"}
        response = client.post(reverse("ai:generate_exam_questions"), data)
        assert response.status_code == HTTP_STATUS_BAD_REQUEST
        assert json.loads(response.content) == {"error": "Content violation"}

    @patch("qugenai.apps.ai.views.client.beta.chat.completions.parse")
    def test_generate_exam_questions_valid_response(self, mock_parse, client, user):
        client.force_login(user)

        # Mocking the OpenAI response object structure
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(
            {
                "subject": "Math",
                "questions": [
                    {
                        "question": "What is 2+2?",
                        "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                        "correct_option": "B",
                        "rationale": "2+2 equals 4.",
                        "tags": ["math", "addition"],
                    },
                ],
            },
        )
        mock_choice.message.refusal = None  # Ensure this is JSON-serializable
        mock_parse.return_value = MagicMock(choices=[mock_choice])

        # Sending a POST request with valid data
        data = {"subject": "Math"}
        response = client.post(reverse("ai:generate_exam_questions"), data)

        # Asserting the response
        assert response.status_code == HTTP_STATUS_OK
        assert "exam_questions" in response.context
        exam_questions = response.context["exam_questions"]
        assert exam_questions["subject"] == "Math"
        assert len(exam_questions["questions"]) == 1
        assert exam_questions["questions"][0]["question"] == "What is 2+2?"

    @patch("qugenai.apps.ai.views.client.beta.chat.completions.parse")
    def test_generate_exam_questions_parsing_error(self, mock_parse, client, user):
        client.force_login(user)

        # Mocking a response with invalid JSON content
        mock_choice = MagicMock()
        mock_choice.message.content = "invalid JSON"
        mock_choice.message.refusal = None  # Ensure this is JSON-serializable
        mock_parse.return_value = MagicMock(choices=[mock_choice])

        # Sending a POST request with valid data
        data = {"subject": "Math"}
        response = client.post(reverse("ai:generate_exam_questions"), data)

        # Asserting the response
        assert response.status_code == HTTP_STATUS_INTERNAL_SERVER_ERROR
        assert json.loads(response.content) == {"error": "Failed to parse response"}

from django.test import TestCase
from unittest.mock import patch
from events.services import create_event
from workflows.tasks import process_event
from dashboard.models import Workspace


class WorkflowTest(TestCase):

    @patch("workflows.tasks.ollama_generate")
    @patch("workflows.tasks.create_room")
    @patch("workflows.tasks.post_message")
    @patch("workflows.tasks.EmailMessage")
    def test_workflow_success(
        self, mock_email, mock_post, mock_room, mock_ollama
    ):
        mock_room.return_value = "!room123"
        mock_ollama.return_value = {
            "response": '{"summary":"ok","answer_to_user":"done","answer_items":[],"next_action":"NONE","steps":[],"risks":[]}'
        }

        payload = {
            "message": "Test",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "intake_id": 1,
            "request_type": "SUPPORT_REQUEST"
        }

        event = create_event("SUPPORT_REQUEST", payload)

        process_event(event.id)

        ws = Workspace.objects.get(correlation_id=event.correlation_id)

        self.assertEqual(ws.status, "DONE")
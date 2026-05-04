from django.test import TestCase
from events.services import create_event
from events.models import OperationalEvent


class EventTest(TestCase):

    def test_create_event(self):
        payload = {"message": "Test"}

        event = create_event("SUPPORT_REQUEST", payload)

        self.assertEqual(event.status, "PENDING")
        self.assertEqual(OperationalEvent.objects.count(), 1)
        self.assertIsNotNone(event.correlation_id)
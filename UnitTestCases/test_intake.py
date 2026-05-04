from django.test import TestCase
from intake.forms import IntakeRequestForm


class IntakeTest(TestCase):

    def test_valid_form(self):
        form = IntakeRequestForm(data={
            "request_type": "SUPPORT_REQUEST",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@gmail.com",
            "message": "Help me"
        })

        self.assertTrue(form.is_valid())

    def test_invalid_message_length(self):
        form = IntakeRequestForm(data={
            "request_type": "SUPPORT_REQUEST",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@gmail.com",
            "message": "x" * 1001
        })

        self.assertFalse(form.is_valid())
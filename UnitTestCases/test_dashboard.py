from django.test import TestCase
from dashboard.models import Workspace
from team.models import TeamMember


class DashboardTest(TestCase):

    def test_workspace_creation(self):
        ws = Workspace.objects.create(
            event_type="SUPPORT_REQUEST",
            status="READY"
        )

        self.assertEqual(ws.status, "READY")

    def test_owner_assignment(self):
        member = TeamMember.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            is_active=True
        )

        ws = Workspace.objects.create(
            event_type="SUPPORT_REQUEST",
            owner_name="None"
        )


        ws.owner_member = member
        ws.owner_name = member.full_name
        ws.save()

        self.assertEqual(ws.owner_name, "John Doe")
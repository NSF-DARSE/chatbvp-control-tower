from django.test import TestCase
from team.models import TeamMember


class TeamTest(TestCase):

    def test_create_member(self):
        member = TeamMember.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@test.com"
        )

        self.assertEqual(member.full_name, "Alice Smith")
        self.assertTrue(member.is_active)
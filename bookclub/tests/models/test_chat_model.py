"""Unit tests for the Chat model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Chat

class ChatModelTestCase(TestCase):
    """Unit tests for the Chat model."""

    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_chat.json',
    ]

    def setUp(self):
        self.chat = Chat.objects.get(id=1)

    def _assert_chat_is_valid(self):
        try:
            self.chat.full_clean()
        except (ValidationError):
            self.fail('Test chat should be valid')

    def _assert_chat_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.chat.full_clean()

    def test_chat_created(self):
        self.assertEqual(1, Chat.objects.count())

    def test_valid_chat(self):
        self._assert_chat_is_valid()

    def test_message_may_be_not_blank(self):
        self.chat.message = ""
        self._assert_chat_is_invalid()

    def test_message_may_be_not_null(self):
        self.chat.message = None
        self._assert_chat_is_invalid()

    def test_no_chat_for_non_members(self):
        self.chat.user = User.objects.get(id=4)
        self._assert_chat_is_invalid()

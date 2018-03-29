from io import StringIO
from django.core.management import call_command
from django.test import TestCase

class createTransactionTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command('create_transaction', stdout=out)
       # self.assertIn('', out.getValue())

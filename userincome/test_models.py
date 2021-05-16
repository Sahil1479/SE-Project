from django.test import TestCase
from django.contrib.auth.models import User
from userincome.models import UserIncome, Source


class TestSourceModel(TestCase):

    def setUp(self):
        self.data1 = Source.objects.create(name='django')

    def test_source_model_entry(self):
        """
        Test Source model data insertion/type/field attributes
        """
        data = self.data1
        self.assertTrue(isinstance(data, Source))

    def test_source_model_entry_return(self):
        """
        Test Source model default name
        """
        data = self.data1
        self.assertEqual(str(data), 'django')


class TestUserIncomeModel(TestCase):

    def setUp(self):
        self.owner = User.objects.create(username='admin')
        self.data1 = UserIncome.objects.create(amount=1, description='test description',
                                               owner=self.owner, source="django")

    def test_source_model_entry(self):
        """
        Test Source model data insertion/type/field attributes
        """
        data = self.data1
        self.assertTrue(isinstance(data, UserIncome))
        self.assertEqual(str(data), 'django')

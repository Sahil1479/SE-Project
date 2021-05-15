from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from userincome.models import UserIncome, Source
from django.test import Client
import datetime


class TestUserIncome(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("sahil", "sahilharpal1234@gmail.com", "password123")
        self.user2 = User.objects.create_user("sahil2", "sahilharpal12345@gmail.com", "password1234")
        self.source = Source.objects.create(name='django')
        self.view_income_url = reverse('income')
        self.add_income_url = reverse('add-income')
        self.income = {
            'amount': 1000,
            'description': "Hello World",
            'date': datetime.date.today(),
            'source': 'RENT',
            'owner': User.objects.first(),
        }
        self.updated_income = {'amount': 500,
                               'description': 'Updated name',
                               'date': datetime.date.today()}

    def create_income(self):
        ex = UserIncome(amount=1000,
                        description="Hello World",
                        date=datetime.date.today(),
                        source='RENT',
                        owner=User.objects.first())
        ex.save()

    def test_show_income_page_if_no_auth(self):
        response = self.client.get(reverse('income'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login?next=/income/')

    def test_show_income_page_if_auth(self):
        self.client.login(username='sahil', password='password123')
        response = self.client.get(reverse('income'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/index.html')

    def test_get_add_income_if_no_auth(self):
        response = self.client.get(reverse('add-income'))
        self.assertEqual(response.status_code, 302)

    def test_get_add_income_if_auth(self):
        self.client.login(username='sahil', password='password123')
        response = self.client.get(reverse('add-income'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/add_income.html')

    def test_post_add_income_if_auth(self):
        self.client.login(username='sahil', password='password123')
        response = self.client.post(reverse('add-income'), {
                'amount': 1000,
                'description': "Hello World",
                'income_date': datetime.date.today(),
                'source': 'RENT',
                'owner': self.user,
            }, format='text/html')
        created_income = UserIncome.objects.filter(owner=self.user).order_by('-id')
        print("create income", created_income[0].owner)
        print("create income", self.user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(created_income[0].owner, self.user)
        self.assertEqual(created_income[0].amount, 1000)
        self.assertEqual(created_income[0].description, 'Hello World')
        self.assertEqual(created_income[0].source, 'RENT')

    def test_get_edit_others_income(self):
        self.client.login(username='sahil2', password='password1234')
        # create income object associated with user(username=sahil)
        self.create_income()
        # retrieve that income object
        income_obj = UserIncome.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(reverse('income-edit', kwargs={'id': income_obj[0].id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/income/')

    def test_get_edit_own_income(self):
        self.client.login(username='sahil', password='password123')
        # create income object associated with user(username=sahil)
        self.create_income()
        # retrieve that income object
        income_obj = UserIncome.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(reverse('income-edit', kwargs={'id': income_obj[0].id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income/edit_income.html')

    def test_post_edit_income_if_auth(self):
        self.client.login(username='sahil', password='password123')
        self.create_income()
        income_obj = UserIncome.objects.filter(owner=self.user).order_by('-id')

        response = self.client.post(reverse('income-edit', kwargs={'id': income_obj[0].id}), {
                'amount': 500,
                'description': "Update Hello World",
                'income_date': datetime.date.today(),
                'source': 'RENT',
                'owner': self.user,
            }, format='text/html')
        updated_income = UserIncome.objects.filter(owner=self.user).order_by('-id')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(updated_income[0].owner, self.user)
        self.assertEqual(updated_income[0].amount, 500)
        self.assertEqual(updated_income[0].description, 'Update Hello World')
        self.assertEqual(updated_income[0].source, 'RENT')
        self.assertEqual(updated_income[0].date, datetime.date.today())

    def test_delete_own_income(self):
        self.client.login(username='sahil', password='password123')
        self.create_income()
        income_obj = UserIncome.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(
            reverse('income-delete', kwargs={'id': income_obj[0].id}),
            format='json')
        income_obj_after_delete = UserIncome.objects.filter(owner=self.user).order_by('-id')

        self.assertEqual(0, len(income_obj_after_delete))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/income/')

    def test_delete_others_income(self):
        self.client.login(username='sahil2', password='password1234')
        self.create_income()
        income_obj = UserIncome.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(
            reverse('income-delete', kwargs={'id': income_obj[0].id}),
            format='json')
        income_obj_after_delete = UserIncome.objects.filter(owner=self.user).order_by('-id')

        self.assertEqual(1, len(income_obj_after_delete))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/income/')

    def test_should_not_create_income_with_an_inactive_account(self):
        user = self.user
        user.is_active = False
        user.save()
        response = self.client.get(
            self.add_income_url, data=self.income, format='json')

        self.assertEqual(response.status_code, 302)

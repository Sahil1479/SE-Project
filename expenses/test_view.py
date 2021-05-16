from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from expenses.models import Expense, Category
from django.test import Client
import datetime


class TestExpense(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("sahil", "sahilharpal1234@gmail.com", "password123")
        self.user2 = User.objects.create_user("sahil2", "sahilharpal12345@gmail.com", "password1234")
        self.source = Category.objects.create(name='django')
        self.view_expense_url = reverse('expenses')
        self.add_expense_url = reverse('add-expenses')

        self.expense = {
              'amount': 1000,
              'description': "Hello World",
              'date': datetime.date.today(),
              'category': 'RENT',
              'owner': User.objects.first(),
        }
        self.updated_expense = {'amount': 500,
                                'description': 'Updated name',
                                'date': datetime.date.today()}

    def create_expense(self):
        ex = Expense(amount=1000,
                     description="Hello World",
                     date=datetime.date.today(),
                     category='RENT',
                     owner=self.user)
        ex.save()

    def test_show_expense_page_if_no_auth(self):
        response = self.client.get(reverse('expenses'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login?next=/expenses/')

    def test_show_expense_page_if_auth(self):
        self.client.login(username='sahil', password='password123')
        response = self.client.get(reverse('expenses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/index.html')

    def test_get_add_expense_if_no_auth(self):
        response = self.client.get(reverse('add-expenses'))
        self.assertEqual(response.status_code, 302)

    def test_get_add_expense_if_auth(self):
        self.client.login(username='sahil', password='password123')
        response = self.client.get(reverse('add-expenses'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/add_expense.html')

    def test_post_add_expense_if_auth(self):
        self.client.login(username='sahil', password='password123')
        response = self.client.post(reverse('add-expenses'), {
                'amount': 1000,
                'description': "Hello World",
                'expense_date': datetime.date.today(),
                'category': 'RENT',
                'owner': self.user,
            }, format='text/html')
        created_expense = Expense.objects.filter(owner=self.user).order_by('-id')
        print("create expense", created_expense[0].owner)
        print("create expense", self.user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(created_expense[0].owner, self.user)
        self.assertEqual(created_expense[0].amount, 1000)
        self.assertEqual(created_expense[0].description, 'Hello World')
        self.assertEqual(created_expense[0].category, 'RENT')

    def test_get_edit_others_expense(self):
        self.client.login(username='sahil2', password='password1234')
        # create expense object associated with user(username=sahil)
        self.create_expense()
        # retrieve that expense object
        expense_obj = Expense.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(reverse('expense-edit', kwargs={'id': expense_obj[0].id}))
        self.assertEqual(response.status_code, )
        self.assertRedirects(response, '/expenses/')

    def test_get_edit_own_expense(self):
        self.client.login(username='sahil', password='password123')
        # create expense object associated with user(username=sahil)
        self.create_expense()
        # retrieve that expense object
        expense_obj = Expense.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(reverse('expense-edit', kwargs={'id': expense_obj[0].id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/edit-expense.html')

    def test_post_edit_expense_if_auth(self):
        self.client.login(username='sahil', password='password123')
        self.create_expense()
        expense_obj = Expense.objects.filter(owner=self.user).order_by('-id')

        response = self.client.post(reverse('expense-edit', kwargs={'id': expense_obj[0].id}), {
                'amount': 500,
                'description': "Update Hello World",
                'expense_date': datetime.date.today(),
                'category': 'RENT',
                'owner': self.user,
            }, format='text/html')
        updated_expense = Expense.objects.filter(owner=self.user).order_by('-id')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(updated_expense[0].owner, self.user)
        self.assertEqual(updated_expense[0].amount, 500)
        self.assertEqual(updated_expense[0].description, 'Update Hello World')
        self.assertEqual(updated_expense[0].category, 'RENT')
        self.assertEqual(updated_expense[0].date, datetime.date.today())

    def test_delete_own_expense(self):
        self.client.login(username='sahil', password='password123')
        self.create_expense()
        expense_obj = Expense.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(
            reverse('expense-delete', kwargs={'id': expense_obj[0].id}),
            format='json')
        expense_obj_after_delete = Expense.objects.filter(owner=self.user).order_by('-id')

        self.assertEqual(0, len(expense_obj_after_delete))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/expenses/')

    def test_delete_others_expense(self):
        self.client.login(username='sahil2', password='password1234')
        self.create_expense()
        expense_obj = Expense.objects.filter(owner=self.user).order_by('-id')

        response = self.client.get(
            reverse('expense-delete', kwargs={'id': expense_obj[0].id}),
            format='json')
        expense_obj_after_delete = Expense.objects.filter(owner=self.user).order_by('-id')

        self.assertEqual(1, len(expense_obj_after_delete))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/expenses/')

    def test_should_not_create_expense_with_an_inactive_account(self):
        user = self.user
        user.is_active = False
        user.save()
        response = self.client.get(
            self.add_expense_url, data=self.expense, format='json')

        self.assertEqual(response.status_code, 302)

    def test_should_render_expense_correctly(self):
        self.client.login(username='sahil', password='password123')
        self.create_expense()
        created_expense = Expense.objects.filter(owner=self.user).order_by('-id')
        # print(created_expense[0])
        # print(created_expense)
        res = self.client.get(reverse('expense',
                                      kwargs={'id': int(created_expense.id)}),
                              format='json')
        self.assertEqual(res.data['id'], created_expense.id)
        self.assertEqual(res.status_code, 200)

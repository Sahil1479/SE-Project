from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.utils import token_generator


class RegistrationView(TestCase):

    def test_can_view_page_correctly(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_should_signup_user(self):
        self.user = {
            "username": "username",
            "email": "email@hmail2.com",
            "password": "password",
        }
        response = self.client.post(reverse("register"), self.user)
        self.assertEquals(response.status_code, 200)

    def test_should_not_signup_with_invalid_password(self):
        self.user = {
            "username": "username",
            "email": "email@hmail2.com",
            "password": "pass",
        }
        response = self.client.post(reverse("register"), self.user)
        self.assertEquals(response.status_code, 302)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Password too short",
                      list(map(lambda x: x.message, storage)))

    def test_should_not_signup_with_same_username(self):
        self.user = {
            "username": "username",
            "email": "email@hmail23.com",
            "password": "password",
        }

        self.user2 = {
            "username": "username",
            "email": "email@hmail23.com",
            "password": "password",
        }
        self.client.post(reverse("register"), self.user)
        response = self.client.post(reverse("register"), self.user2)
        self.assertEquals(response.status_code, 409)

        storage = get_messages(response.wsgi_request)

        self.assertIn("This username is already registered",
                      list(map(lambda x: x.message, storage)))

    def test_should_not_signup_user_with_taken_email(self):

        self.user = {
            "username": "username1",
            "email": "email@hmail2.com",
            "password": "password",
        }

        self.test_user2 = {
            "username": "username11",
            "email": "email@hmail2.com",
            "password": "password",
        }

        self.client.post(reverse("register"), self.user)
        response = self.client.post(reverse("register"), self.test_user2)
        self.assertEquals(response.status_code, 409)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Email address is already registered",
                      list(map(lambda x: x.message, storage)))

    def test_should_login_successfully(self):
        self.user = {
            "username": "username",
            "password": "password",
        }
        response = self.client.post(reverse("login"), self.user)
        self.assertEquals(response.status_code, 200)


class LoginView(TestCase):
    def test_should_show_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_success(self):
        self.user = {
            "username": "username",
            "email": "email@hmail2.com",
            "password": "password",
        }
        self.client.post(reverse('register'), self.user, format='text/html')
        user = User.objects.filter(email=self.user['email']).first()
        user.is_active = True
        user.save()
        response = self.client.post(reverse('login'), self.user, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_cannot_login_with_unverified_email(self):
        self.user = {
            "username": "username",
            "email": "email@hmail2.com",
            "password": "password",
        }
        self.client.post(reverse('register'), self.user, format='text/html')
        response = self.client.post(reverse('login'), self.user, format='text/html')
        self.assertEqual(response.status_code, 302)
        storage = get_messages(response.wsgi_request)

        self.assertIn("Account is not active, Please check your email",
                      list(map(lambda x: x.message, storage)))

    def test_cantlogin_with_no_username(self):
        response = self.client.post(reverse('login'), {'password': 'passwped', 'username': ''}, format='text/html')
        self.assertEqual(response.status_code, 302)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Please fill all fields",
                      list(map(lambda x: x.message, storage)))

    def test_cantlogin_with_no_password(self):
        response = self.client.post(reverse('login'), {'username': 'passwped', 'password': ''}, format='text/html')
        self.assertEqual(response.status_code, 302)
        storage = get_messages(response.wsgi_request)
        self.assertIn("Please fill all fields",
                      list(map(lambda x: x.message, storage)))


class VerificationView(TestCase):
    def test_user_ctivates_success(self):
        user = User.objects.create_user('testuser', 'test@gmail.com')
        user.set_password('tetetebvghhhhj')
        user.is_active = False
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='test@gmail.com')
        self.assertTrue(user.is_active)

    def test_user_cant_activates_succesfully(self):
        user = User.objects.create_user('testuser', 'test@gmail.com')
        user.set_password('tetetebvghhhhj')
        user.is_active = False
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='test@gmail.com')
        self.assertFalse(user.is_active)

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
# from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.urls import reverse
from .utils import token_generator
from django.contrib import auth
# Create your views here.


class RegistrationView(View):
    def get(self, request):
        return render(request, 'accounts/register.html')

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.warning(request, 'Password too short')
                    return render(request, 'accounts/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                activate_url = 'http://'+domain+link
                EmailSub = 'Activate your ExpenseTracker account'
                EmailBody = 'Hi ' + user.username + " Please use this link to verify your account\n" + activate_url
                email_temp = EmailMessage(
                    EmailSub,
                    EmailBody,
                    'djproject77@gmail.com',
                    [email],
                )
                email_temp.send(fail_silently=False)
                messages.success(request, 'Account successfully created')
                return render(request, 'accounts/register.html')
            else:
                messages.warning(request, 'Email address is already registered')
                return render(request, 'accounts/register.html')
        messages.warning(request, 'This username is already registered')
        return render(request, 'accounts/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:  # noqa: F841
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            try:
                user = User.objects.get(username=username)
            except:  # noqa: E722
                user = None
            if user:
                if user.is_active:
                    auth.login(request, user)
                    # messages.success(request, "Welcome, "+user.username+" you are now logged in")
                    return redirect('main')

                messages.warning(request, "Account is not active, Please check your email")
                return render(request, 'accounts/login.html')

            messages.warning(request, "Invalid credentials, try again")
            return render(request, 'accounts/login.html')

        messages.warning(request, "Please fill all fields")
        return render(request, 'accounts/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out")
        return redirect('login')

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
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
                    #messages.error(request, 'Password too short')
                    return render(request, 'accounts/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.save()
                return render(request, 'accounts/register.html')

        return render(request, 'accounts/register.html')

from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
# from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
import datetime
from django.http import JsonResponse


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/auth/login')
def index(request):
    '''categories = Source.objects.all()'''
    income = UserIncome.objects.filter(owner=request.user).order_by('-id')
    paginator = Paginator(income, 7)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'income': income,
        'page_obj': page_obj,
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/auth/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/auth/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        requested_user = request.user
        if income.owner == requested_user:
            return render(request, 'income/edit_income.html', context)
        else:
            return redirect('income')
    if request.method == 'POST':
        amount = request.POST['amount']

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    requested_user = request.user
    if income.owner == requested_user:
        income.delete()
        messages.success(request, 'Income removed')
    return redirect('income')


def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_source(income):
        return income.source
    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in incomes:
        for y in source_list:
            finalrep[y] = get_income_source_amount(y)

    return JsonResponse({'income_source_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'income/stats.html')

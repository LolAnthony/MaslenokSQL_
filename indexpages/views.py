from django.shortcuts import render

from scripts.db_initialize import initialize_products
from scripts.sbis_script import get_products


def index(request):
    return render(request, 'indexpages/index.html', {'title': 'Главная'})


def about(request):
    return render(request, 'indexpages/about.html', {'title': 'О нас'})


def contacts(request):
    return render(request, 'indexpages/contacts.html', {'title': 'Контакты'})

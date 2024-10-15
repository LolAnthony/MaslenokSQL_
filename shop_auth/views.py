from django.db import connection
from django.shortcuts import render, redirect


def get_shop_employee_data(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT e.last_name, e.first_name, e.middle_name, '
                       'e.phone_number, e.email, e.`function`, ad.subject, ad.town, ad.street, ad.house '
                       'FROM employee_of_shop e '
                       'JOIN address ad ON ad.address_id = (SELECT address_id FROM shop WHERE shop.shop_id = e.shop_id)  '
                       'WHERE e.employee_id =%s',
                       (request.session['shop_employee_id'],))
        current_user = cursor.fetchone()
    keys = ('last_name', 'first_name', 'middle_name', 'phone_number', 'email', 'function', 'subject', 'town',
            'street', 'house')
    return dict(zip(keys, current_user))


def sh_profile(request):
    try:
        if request.session['shop_employee_id']:
            try:
                context = get_shop_employee_data(request)
                context.update({'title': 'Профиль'})
                return render(request, 'shop_auth/profile.html', context)
            except:
                request.session.clear()
                return redirect('sh_login')
        else:
            return redirect('sh_login')
    except KeyError:
        return redirect('sh_login')


def sh_login(request):
    try:
        if request.POST:
            email = request.POST.get('email', )
            password = request.POST.get('password', )
            with connection.cursor() as cursor:
                cursor.execute('SELECT employee_id '
                               'FROM employee_of_shop '
                               'WHERE email =%s AND password = %s',
                               (email, password))
                raw = cursor.fetchone()
                if raw:
                    request.session.clear()
                    request.session['shop_employee_id'] = raw[0]
                else:
                    return render(request, 'shop_auth/login.html', {'title': 'Вход', 'error': 1})
        if request.session['shop_employee_id']:
            return redirect('sh_profile')
        else:
            return render(request, 'shop_auth/login.html', {'title': 'Вход'})
    except KeyError:
        return render(request, 'shop_auth/login.html', {'title': 'Вход'})


def sh_logout(request):
    request.session.clear()
    return redirect('sh_login')


def sh_change_profile_data(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute('SELECT password '
                            'FROM employee_of_shop '
                            'WHERE employee_id = %s',
                            (request.session['shop_employee_id'],))
            raw = cursor.fetchone()
        if request.POST.get('password') == raw[0]:
            email = request.POST.get('email', )
            first_name = request.POST.get('first_name', )
            last_name = request.POST.get('last_name', )
            middle_name = request.POST.get('middle_name', )
            phone_number = request.POST.get('phone_number', )
            with connection.cursor() as cursor:
                cursor.execute('UPDATE employee_of_shop '
                                'SET email=%s, first_name=%s, last_name=%s, '
                                'middle_name=%s, phone_number=%s WHERE employee_id=%s',
                                (email, first_name, last_name, middle_name, phone_number,
                                request.session['shop_employee_id']))
            return redirect('sh_profile')
        else:
            context = get_shop_employee_data(request)
            context.update({'title': 'Редактирование профиля', 'error': 1})
            return render(request, 'shop_auth/change_profile_data.html', context)
    else:
        context = get_shop_employee_data(request)
        context.update({'title': 'Редактирование профиля'})
        return render(request, 'shop_auth/change_profile_data.html', context)


def sh_change_password(request):
    if request.method == 'POST':
        if request.POST.get('password_new1') == request.POST.get('password_new2'):
            with connection.cursor() as cursor:
                cursor.execute('SELECT password '
                                'FROM employee_of_shop '
                                'WHERE employee_id = %s',
                                (request.session['shop_employee_id'],))
                raw = cursor.fetchone()
            if request.POST.get('password_old') == raw[0]:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE employee_of_shop '
                                   'SET password=%s '
                                   'WHERE employee_id = %s',
                                   (request.POST.get('password_new1'),
                                    request.session['shop_employee_id'],))
                    return redirect('sh_profile')
            else:
                return render(request, 'shop_auth/change_password.html', {'title': 'Смена пароля', 'error_old': 1})
        else:
            return render(request, 'shop_auth/change_password.html', {'title': 'Смена пароля', 'error': 1})
    else:
        return render(request, 'shop_auth/change_password.html', {'title': 'Смена пароля'})

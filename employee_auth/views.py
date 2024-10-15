from django.db import connection
from django.shortcuts import render, redirect


def emp_index(request):
    return render(request, 'employee_auth/emp_index.html', {'title': 'Сотрудникам'})


def get_storage_employee_data(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT last_name, first_name, middle_name, '
                       'phone_number, email, `function` FROM employee_of_storage '
                       'WHERE employee_of_storage_id =%s',
                       (request.session['employee_id'],))
        current_user = cursor.fetchone()
    keys = ('last_name', 'first_name', 'middle_name', 'phone_number', 'email', 'function')
    return dict(zip(keys, current_user))


def emp_profile(request):
    try:
        if request.session['employee_id']:
            try:
                context = get_storage_employee_data(request)
                context.update({'title': 'Профиль'})
                return render(request, 'employee_auth/profile.html', context)
            except:
                request.session.clear()
                return redirect('emp_login')
        else:
            return redirect('emp_login')
    except KeyError:
        return redirect('emp_login')


def emp_login(request):
    try:
        if request.POST:
            email = request.POST.get('email', )
            password = request.POST.get('password', )
            with connection.cursor() as cursor:
                cursor.execute('SELECT employee_of_storage_id '
                               'FROM employee_of_storage '
                               'WHERE email =%s AND password = %s',
                               (email, password))
                raw = cursor.fetchone()
                if raw:
                    request.session.clear()
                    request.session['employee_id'] = raw[0]
                else:
                    return render(request, 'employee_auth/login.html', {'title': 'Вход', 'error': 1})
        if request.session['employee_id']:
            return redirect('emp_profile')
        else:
            return render(request, 'employee_auth/login.html', {'title': 'Вход'})
    except KeyError:
        return render(request, 'employee_auth/login.html', {'title': 'Вход'})


def emp_logout(request):
    request.session.clear()
    return redirect('emp_login')


def emp_change_profile_data(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute('SELECT password '
                            'FROM employee_of_storage '
                            'WHERE employee_of_storage_id = %s',
                            (request.session['employee_id'],))
            raw = cursor.fetchone()
        if request.POST.get('password') == raw[0]:
            email = request.POST.get('email', )
            first_name = request.POST.get('first_name', )
            last_name = request.POST.get('last_name', )
            middle_name = request.POST.get('middle_name', )
            phone_number = request.POST.get('phone_number', )
            with connection.cursor() as cursor:
                cursor.execute('UPDATE employee_of_storage '
                                'SET email=%s, first_name=%s, last_name=%s, '
                                'middle_name=%s, phone_number=%s WHERE employee_of_storage_id=%s',
                                (email, first_name, last_name, middle_name, phone_number,
                                request.session['employee_id']))
            return redirect('emp_profile')
        else:
            context = get_storage_employee_data(request)
            context.update({'title': 'Редактирование профиля', 'error': 1})
            return render(request, 'employee_auth/change_profile_data.html', context)
    else:
        context = get_storage_employee_data(request)
        context.update({'title': 'Редактирование профиля'})
        return render(request, 'employee_auth/change_profile_data.html', context)


def emp_change_password(request):
    if request.method == 'POST':
        if request.POST.get('password_new1') == request.POST.get('password_new2'):
            with connection.cursor() as cursor:
                cursor.execute('SELECT password '
                                'FROM employee_of_storage '
                                'WHERE employee_of_storage_id = %s',
                                (request.session['employee_id'],))
                raw = cursor.fetchone()
            if request.POST.get('password_old') == raw[0]:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE employee_of_storage '
                                   'SET password=%s '
                                   'WHERE employee_of_storage_id = %s',
                                   (request.POST.get('password_new1'),
                                    request.session['employee_id'],))
                    return redirect('emp_profile')
            else:
                return render(request, 'employee_auth/change_password.html', {'title': 'Смена пароля', 'error_old': 1})
        else:
            return render(request, 'employee_auth/change_password.html', {'title': 'Смена пароля', 'error': 1})
    else:
        return render(request, 'employee_auth/change_password.html', {'title': 'Смена пароля'})

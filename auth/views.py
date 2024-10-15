from django.db import connection
from django.shortcuts import render, redirect


def get_user_data(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT last_name, first_name, middle_name, '
                       'phone_number, email FROM platform_user '
                       'WHERE platform_user_id =%s',
                       (request.session['platform_user_id'],))
        current_user = cursor.fetchone()
    keys = ('last_name', 'first_name', 'middle_name', 'phone_number', 'email')
    return dict(zip(keys, current_user))


def profile(request):
    try:
        if request.session['platform_user_id']:
            try:
                context = get_user_data(request)
                context.update({'title': 'Профиль'})
                return render(request, 'auth/profile.html', context)
            except:
                request.session.clear()
                return redirect('login')
        else:
            return redirect('login')
    except KeyError:
        return redirect('login')


def login(request):
    try:
        if request.POST:
            email = request.POST.get('email', )
            password = request.POST.get('password', )
            with connection.cursor() as cursor:
                cursor.execute('SELECT platform_user_id '
                               'FROM platform_user '
                               'WHERE email =%s AND password = %s',
                               (email, password))
                raw = cursor.fetchone()
                if raw:
                    request.session.clear()
                    request.session['platform_user_id'] = raw[0]
                else:
                    return render(request, 'auth/login.html', {'title': 'Вход', 'error': 1})
        if request.session['platform_user_id']:
            return redirect('profile')
        else:
            return render(request, 'auth/login.html', {'title': 'Вход'})
    except KeyError:
        return render(request, 'auth/login.html', {'title': 'Вход'})


def logout(request):
    request.session.clear()
    return redirect('login')


def registration(request):
    try:
        if request.POST:
            email = request.POST.get('email', )
            password = request.POST.get('password', )
            first_name = request.POST.get('first_name', )
            last_name = request.POST.get('last_name', )
            middle_name = request.POST.get('middle_name', )
            phone_number = request.POST.get('phone_number', )
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO platform_user '
                               '(email, password, first_name, last_name, '
                               'middle_name, phone_number) '
                               'values (%s, %s, %s, %s, %s, %s)',
                               [email, password, first_name, last_name, middle_name, phone_number])
                inserted_id = cursor.lastrowid
                request.session['platform_user_id'] = inserted_id
        if request.session['platform_user_id']:
            return redirect('profile')
        else:
            return render(request, 'auth/registration.html', {'title': 'Регистрация'})
    except KeyError:
        return render(request, 'auth/registration.html', {'title': 'Регистрация'})


def change_profile_data(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute('SELECT password '
                            'FROM platform_user '
                            'WHERE platform_user_id = %s',
                            (request.session['platform_user_id'],))
            raw = cursor.fetchone()
        if request.POST.get('password') == raw[0]:
            email = request.POST.get('email', )
            first_name = request.POST.get('first_name', )
            last_name = request.POST.get('last_name', )
            middle_name = request.POST.get('middle_name', )
            phone_number = request.POST.get('phone_number', )
            with connection.cursor() as cursor:
                cursor.execute('UPDATE platform_user '
                                'SET email=%s, first_name=%s, last_name=%s, '
                                'middle_name=%s, phone_number=%s WHERE platform_user_id=%s',
                                (email, first_name, last_name, middle_name, phone_number,
                                request.session['platform_user_id']))
            return redirect('profile')
        else:
            context = get_user_data(request)
            context.update({'title': 'Редактирование профиля', 'error': 1})
            return render(request, 'auth/change_profile_data.html', context)
    else:
        context = get_user_data(request)
        context.update({'title': 'Редактирование профиля'})
        return render(request, 'auth/change_profile_data.html', context)


def change_password(request):
    if request.method == 'POST':
        if request.POST.get('password_new1') == request.POST.get('password_new2'):
            with connection.cursor() as cursor:
                cursor.execute('SELECT password '
                                'FROM platform_user '
                                'WHERE platform_user_id = %s',
                                (request.session['platform_user_id'],))
                raw = cursor.fetchone()
            if request.POST.get('password_old') == raw[0]:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE platform_user '
                                   'SET password=%s '
                                   'WHERE platform_user_id = %s',
                                   (request.POST.get('password_new1'),
                                    request.session['platform_user_id'],))
                    return redirect('profile')
            else:
                return render(request, 'auth/change_password.html', {'title': 'Смена пароля', 'error_old': 1})
        else:
            return render(request, 'auth/change_password.html', {'title': 'Смена пароля', 'error': 1})
    else:
        return render(request, 'auth/change_password.html', {'title': 'Смена пароля'})

from django.db import connection

from django.shortcuts import render, redirect


def admin_menu(request):
    if request.session.get('shop_employee_id') or request.session.get('employee_id'):
        params = {}
        cost = {}
        params['weight'] = request.GET.get('weight')
        find_name = request.GET.get('name')
        params['brand_name'] = request.GET.get('brand_name')
        params['country'] = request.GET.get('country')
        page_number = int(request.GET.get('page_number', 0)) * 40
        cost['min_cost'] = request.GET.get('min_cost')
        cost['max_cost'] = request.GET.get('max_cost')
        emp = 0
        with connection.cursor() as cursor:
            if request.session.get('employee_id'):
                emp = 0
                query = ('SELECT p.product_id, p.name, p.weight, '
                         'm.brand_name, m.country, cp.cost, COALESCE(SUM(shpr.count), 0) '
                         'FROM product p '
                         'JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id '
                         'LEFT JOIN shop_product shpr on shpr.product_id = p.product_id '
                         'JOIN cost_of_product cp ON p.product_id = cp.product_id '
                         'WHERE cp.date_of_entry = '
                         '(SELECT MAX(date_of_entry) FROM cost_of_product cp where p.product_id = cp.product_id)')
            elif request.session.get('shop_employee_id'):
                emp = 1
                cursor.execute('SELECT shop_id FROM employee_of_shop WHERE employee_id = %s',
                                         (str(request.session['shop_employee_id'])))
                shop_id = cursor.fetchone()[0]
                query = (
                        'SELECT p.product_id, p.name, p.weight, '
                        'm.brand_name, m.country, cp.cost, COALESCE(shpr.count, 0) AS count '
                        'FROM product p '
                        'JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id '
                        'LEFT JOIN shop_product shpr ON shpr.product_id = p.product_id AND '
                        'shpr.shop_id =' + str(shop_id) + ' ' +
                        'JOIN cost_of_product cp ON p.product_id = cp.product_id '
                        'WHERE cp.date_of_entry = '
                        '(SELECT MAX(date_of_entry) FROM cost_of_product WHERE product_id = p.product_id)'
                )
            else:
                return redirect('emp_index')
            for param in params:
                if params[param]:
                    query += f' AND {param} = "{params[param]}"'
            if cost['min_cost']:
                query += f' AND cp.cost >= {cost["min_cost"]}'
            if cost['max_cost']:
                query += f' AND cp.cost <= {cost["max_cost"]}'
            if find_name:
                query += f' AND p.name LIKE "%{find_name}%"'
            query += ' GROUP BY p.product_id, p.name, p.weight, m.brand_name, m.country, cp.cost'
            cursor.execute(query)
            products_raw = cursor.fetchall()
            products = []
            for row in products_raw:
                products.append({
                    'product_id': row[0],
                    'product_name': row[1],
                    'weight': row[2],
                    'brand_name': row[3],
                    'country': row[4],
                    'cost': row[5],
                    'total': row[6]
                })
            cursor.execute('SELECT DISTINCT brand_name FROM manufacturer')
            brands = cursor.fetchall()
            brands = tuple(item[0] for item in brands)
            cursor.execute('SELECT DISTINCT country FROM manufacturer')
            countries = cursor.fetchall()
            countries = tuple(item[0] for item in countries)
        products = tuple(products)
        products_count = len(products)
        return render(request, 'admin_menu/admin_menu.html', {'title': 'Админ панель',
                                                              'products': products,
                                                              'products_count': products_count,
                                                              'brands': brands, 'countries': countries, 'emp': emp})
    else:
        redirect('emp_index')


def edit_product(request):
    if request.session.get('shop_employee_id'):
        emp = 1
    elif request.session.get('employee_id'):
        emp = 0
    else:
        return redirect('emp_index')

    if request.POST.get('del_id'):
        del_id = request.POST.get('del_id')
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM shop_product WHERE product_id = %s', (del_id,))
            cursor.execute('DELETE FROM cost_of_product WHERE product_id = %s', (del_id,))
            cursor.execute('DELETE FROM product WHERE product_id = %s', (del_id,))
        return redirect('admin_menu')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if (request.POST.get('name') or request.POST.get('weight')
                or request.POST.get('brand')
                or request.POST.get('country')
                or request.POST.get('cost')):
            product_name = request.POST.get('name')
            product_weight = request.POST.get('weight')
            product_brand = request.POST.get('brand')
            product_cost = request.POST.get('cost')
            with connection.cursor() as cursor:
                cursor.execute('SELECT manufacturer_id FROM manufacturer WHERE brand_name =%s', (product_brand,))
                brand_id = cursor.fetchone()
                cursor.execute('UPDATE product SET name = %s, weight = %s, manufacturer_id = %s WHERE product_id = %s',
                               (product_name, product_weight, brand_id, product_id))
                cursor.execute('INSERT INTO cost_of_product (product_id, cost, date_of_entry) '
                               'VALUES (%s, %s, NOW())', (product_id, product_cost))
        if request.POST.get('quantity') and request.POST.get('shop_id'):
            quantity = request.POST.get('quantity')
            shop_id = request.POST.get('shop_id')
            with connection.cursor() as cursor:
                cursor.execute('SELECT count FROM shop_product WHERE product_id = %s AND shop_id = %s',
                               (product_id, shop_id))
                existing_row = cursor.fetchone()
                if existing_row:
                    cursor.execute('UPDATE shop_product SET count = %s WHERE product_id = %s AND shop_id = %s',
                                   (quantity, product_id, shop_id))
                else:
                    cursor.execute('INSERT INTO shop_product (product_id, shop_id, count) VALUES (%s, %s, %s)',
                                   (product_id, shop_id, quantity))
    else:
        return redirect('/admin_menu')
    with connection.cursor() as cursor:
        cursor.execute('SELECT p.product_id, p.name, p.weight, '
                       'm.brand_name, m.country, cp.cost '
                       'FROM product p '
                       'JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id '
                       'JOIN cost_of_product cp ON p.product_id = cp.product_id '
                       'WHERE cp.date_of_entry = '
                       '(SELECT MAX(date_of_entry) FROM cost_of_product cp WHERE p.product_id = cp.product_id) '
                       'AND p.product_id = %s', (product_id,))
        row = cursor.fetchone()
        product = {
            'product_id': row[0],
            'name': row[1],
            'weight': row[2],
            'brand': row[3],
            'country': row[4],
            'cost': row[5],
        }
        if emp == 1:
            cursor.execute('SELECT shop_id FROM employee_of_shop WHERE employee_id = %s',
                           (str(request.session['shop_employee_id'])))
            shop_id = cursor.fetchone()[0]
            cursor.execute('SELECT a.subject, a.town, '
                           'a.street, a.house, sh.shop_id, '
                           'COALESCE(shpr.count, 0) AS coun '
                           'FROM address a '
                           'JOIN shop sh ON a.address_id = sh.address_id '
                           'LEFT JOIN shop_product shpr ON sh.shop_id = shpr.shop_id '
                           'AND shpr.product_id = %s '
                           'WHERE (shpr.product_id = %s OR '
                           'shpr.product_id IS NULL) AND sh.shop_id = %s', (product_id, product_id, shop_id))
        else:
            cursor.execute('SELECT a.subject, a.town, '
                           'a.street, a.house, sh.shop_id, '
                           'COALESCE(shpr.count, 0) AS coun '
                           'FROM address a '
                           'JOIN shop sh ON a.address_id = sh.address_id '
                           'LEFT JOIN shop_product shpr ON sh.shop_id = shpr.shop_id '
                           'AND shpr.product_id = %s '
                           'WHERE (shpr.product_id = %s OR '
                           'shpr.product_id IS NULL)', (product_id, product_id))
        availability_raw = cursor.fetchall()
        cursor.execute('SELECT DISTINCT brand_name FROM manufacturer')
        brands = cursor.fetchall()
        brands = tuple(item[0] for item in brands)
        cursor.execute('SELECT DISTINCT country FROM manufacturer')
        countries = cursor.fetchall()
        countries = tuple(item[0] for item in countries)
        availability = []
        for available in availability_raw:
            availability.append({
                'address': ' '.join(str(item) for item in available[0:3]),
                'shop_id': available[4],
                'quantity': available[5],
            })
    return render(request, 'admin_menu/edit_product.html', {'title': 'Редактирование товара',
                                                            'product': product, 'availability': availability,
                                                            'brands': brands, 'countries': countries, 'emp': emp})


def add_product(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT DISTINCT manufacturer_id, brand_name FROM manufacturer')
        brands = cursor.fetchall()
    brands = tuple(item[0:2] for item in brands)
    if request.method == 'POST':
        name = request.POST.get('name')
        weight = request.POST.get('weight')
        brand_id = request.POST.get('brand_id')
        print(brand_id)
        price = request.POST.get('price')
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO product (name, weight, manufacturer_id) VALUES (%s, %s, %s)',
                           (name, weight, brand_id))
            last_id = cursor.lastrowid
            cursor.execute('INSERT INTO cost_of_product (product_id, cost, date_of_entry) VALUES (%s, %s, NOW())',
                           (last_id, price))
    return render(request, 'admin_menu/add_product.html', {'brands': brands})

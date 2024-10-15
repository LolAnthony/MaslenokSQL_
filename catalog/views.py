from django.db import connection

from django.shortcuts import render, redirect

from scripts.db_initialize import delete_all_products, initialize_products
from scripts.sbis_script import get_products


# Create your views here.


def catalog(request):
    find_flag = False
    params = {}
    cost = {}
    params['weight'] = request.GET.get('weight')
    find_name = request.GET.get('name')
    params['brand_name'] = request.GET.get('brand_name')
    params['country'] = request.GET.get('country')
    page_number = int(request.GET.get('page_number', 0)) * 40
    cost['min_cost'] = request.GET.get('min_cost')
    cost['max_cost'] = request.GET.get('max_cost')
    for param in params:
        if params[param]:
            find_flag = True
            break
    if not find_flag:
        for param in cost:
            if cost[param]:
                find_flag = True
                break
    if not find_flag:
        if find_name:
            find_flag = True
    query = ('SELECT p.product_id, p.description, p.weight, '
             'm.brand_name, m.country, cp.cost '
             'FROM product p '
             'JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id '
             'JOIN cost_of_product cp ON p.product_id = cp.product_id '
             'WHERE cp.date_of_entry = '
             '(SELECT MAX(date_of_entry) FROM cost_of_product cp where p.product_id = cp.product_id)')
    for param in params:
        if params[param]:
            query += f' AND {param} = "{params[param]}"'
    if cost['min_cost']:
        query += f' AND cp.cost >= {cost["min_cost"]}'
    if cost['max_cost']:
        query += f' AND cp.cost <= {cost["max_cost"]}'
    if find_name:
        query += f' AND p.name LIKE "%{find_name}%"'
    if not find_flag:
        query += f' LIMIT 40 OFFSET {page_number};'
    with connection.cursor() as cursor:
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
                'cost': row[5]
            })
        cursor.execute('SELECT COUNT("product_id") FROM product')
        lists_of_products = cursor.fetchone()[0] // 40
        products = tuple(products)
        cursor.execute('SELECT DISTINCT brand_name FROM manufacturer')
        brands = cursor.fetchall()
        brands = tuple(item[0] for item in brands)
        cursor.execute('SELECT DISTINCT country FROM manufacturer')
        countries = cursor.fetchall()
        countries = tuple(item[0] for item in countries)
    last_flag = False
    if page_number // 40 > lists_of_products - 2:
        last_flag = True
    products = tuple(products)
    return render(request, 'catalog/catalog.html',
                  {'title': 'Каталог', 'products': products,
                   'page_number': page_number // 40, 'find_flag': find_flag,
                   'brands': brands, 'countries': countries, 'lists_of_products': lists_of_products, 'last_flag': last_flag})


def delete_all_products_view(request):
    delete_all_products()
    return redirect('index')


def initialize_products_view(request):
    catalog = get_products(100)
    initialize_products(catalog, 1)
    return redirect('catalog')


def add_to_cart(request):
    try:
        if request.session['platform_user_id']:
            if request.method == 'POST':
                product_id = request.POST.get('product_id')
                cart_items = request.session.get('cart_items', {})
                if product_id in cart_items:
                    cart_items[product_id] += 1
                else:
                    cart_items[product_id] = 1
                request.session['cart_items'] = cart_items
            return redirect('cart')
    except KeyError:
        return redirect('login')


def cart(request):
    if 'platform_user_id' in request.session:
        if request.session.get('cart_items'):
            cart_items = request.session['cart_items']
        else:
            cart_items = {}
        cart_items_keys = list(cart_items.keys())
        if not cart_items_keys:
            return render(request, 'catalog/cart.html', {'title': 'Корзина'})
        placeholders = ','.join(['%s'] * len(cart_items_keys))
        query = f'''
                SELECT p.product_id, p.name, p.weight, m.brand_name, m.country, cp.cost,
                (SELECT SUM(count) FROM shop_product WHERE product_id = p.product_id) AS sh_pr
                FROM product p
                JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id
                JOIN cost_of_product cp ON p.product_id = cp.product_id
                WHERE cp.date_of_entry = (
                SELECT MAX(date_of_entry) FROM cost_of_product WHERE product_id = p.product_id
                ) AND p.product_id IN ({placeholders})
                '''
        with connection.cursor() as cursor:
            cursor.execute(query, cart_items_keys)
            products_raw = cursor.fetchall()
            products = []
            for row in products_raw:
                products.append(
                    dict(product_id=row[0],
                            product_name=row[1],
                            weight=row[2],
                            brand_name=row[3],
                            country=row[4],
                            cost=row[5],
                            quantity=row[6],
                            curr_quantity=cart_items[str(row[0])]))
        return render(request, 'catalog/cart.html', {'title': 'Корзина', 'products': products})
    else:
        return redirect('login')


def delete_product_cart(request, product_id):
    if 'cart_items' in request.session:
        cart = request.session['cart_items']
        str_product_id = str(product_id)
        if str_product_id in cart:
            del cart[str_product_id]
            request.session['cart_items'] = cart
    return redirect('cart')

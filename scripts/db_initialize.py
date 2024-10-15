import random

from django.db import connection


def initialize_db():
    with connection.cursor() as cursor:
        cursor.execute('SELECT * from storage')
        test = cursor.fetchone()
        if test:
            print('адреса, магазин и склад ранее были инициализированы')
            return 101 #бд уже инициализирована
        cursor.execute('INSERT INTO address (subject,'
                       'town, street, house, `index`) '
                       'VALUES ("Ростовская Область", "Таганрог", "ул. Розы Люксембург", "159", "347935")')
        inserted_id = cursor.lastrowid
        cursor.execute('INSERT INTO storage (address_id,'
                       'storage_code) VALUES '
                       '(%s, %s)', (inserted_id, 1))
        cursor.execute('INSERT INTO shop (address_id) VALUES (%s)', (inserted_id,))
        return 0



def initialize_products(catalog, shop_id):
    countries = ['Россия', 'США', 'Германия', 'Япония',
                 'Китай', 'Южная Корея', 'Франция',
                 'Италия', 'Великобритания', 'Индия']
    with connection.cursor() as cursor:
        cursor.execute('SELECT * from product')
        test = cursor.fetchone()
        if test:
            print('продукты ранее были инициализированы')
            return 102
        for product in catalog:
            name = product['name']
            cost = product['cost']
            manufacturer = product['manufacturer']
            quantity = product['quantity']
            cursor.execute('SELECT manufacturer_id FROM '
                           'manufacturer WHERE brand_name=%s',
                           (manufacturer,))
            manufacturer_id = cursor.fetchone()
            if manufacturer_id is None:
                random_country = random.choice(countries)
                cursor.execute('INSERT INTO manufacturer (brand_name, country) '
                               'VALUES (%s, %s)', (manufacturer, random_country))
                manufacturer_id = cursor.lastrowid
            cursor.execute('INSERT INTO product '
                           '(name, weight, manufacturer_id) '
                           'VALUES (%s, %s, %s)', (name,
                                                   random.randint(1,10),
                                                   manufacturer_id))
            product_id = cursor.lastrowid
            cursor.execute('INSERT INTO shop_product '
                           '(product_id, shop_id, count) '
                           'VALUES (%s, %s, %s)',
                           (product_id, shop_id, quantity))
            cursor.execute('INSERT INTO cost_of_product (product_id, cost, date_of_entry) '
                           'VALUES (%s, %s, NOW())', (product_id, cost))


def delete_all_products():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM shop_product')
        cursor.execute('DELETE FROM cost_of_product')
        cursor.execute('DELETE FROM product')
        cursor.execute('DELETE FROM manufacturer')

#DELETE FROM shop_product WHERE product_id IN (SELECT product_id FROM product WHERE manufacturer_id IN (26, 28))
#DELETE FROM cost_of_product WHERE product_id in (SELECT product_id FROM product WHERE manufacturer_id IN (26, 28))
#DELETE FROM product WHERE manufacturer_id IN (26,28)
#DELETE FROM manufacturer WHERE manufacturer_id IN (26,28)

def get_products(count):
    import random
    import requests
    json = {
        "app_client_id": "#####",
        "app_secret": "####",
        "secret_key": "####"
    }

    url = 'https://online.sbis.ru/oauth/service/'
    response = requests.post(url, json=json)
    products = []
    if response.status_code == 200:
        # Извлекаем данные из ответа
        data = response.json()

        # Извлекаем данные из словаря и сохраняем в переменные
        access_token = data.get('access_token', None)
        sid = data.get('sid', None)
        token = data.get('token', None)

        # Выводим переменные
        print(f"access_token: {access_token}")
        print(f"sid: {sid}")
        print(f"token: {token}")

        # получаем прайс лист
        parameters_65 = {
            'pointId': 123,
            'priceListId': 65,
            'withName': True,
            'page': 0
        }
        url_65 = 'https://api.sbis.ru/retail/nomenclature/list?'
        headers_65 = {
            "X-SBISAccessToken": access_token
        }
        has_more_65 = True

        while has_more_65:
            if count < 0:
                break
            response_65 = requests.get(url_65, params=parameters_65, headers=headers_65)
            response_65.encoding = 'utf-8'

            if response_65.status_code == 200:
                data_65 = response_65.json()
                nomenclatures_65 = data_65.get('nomenclatures', [])
                for nomenclature in nomenclatures_65:
                    name = nomenclature.get('name', '')
                    cost = nomenclature.get('cost', None)
                    category_name = name.split()[0]
                    if cost:
                        products.append({
                            'name': name,
                            'cost': cost,
                            'manufacturer': category_name,
                            'quantity': random.randint(1,10)
                        })
                        count -= 1
                has_more_65 = data_65.get('outcome', {}).get('hasMore', False)
                parameters_65['page'] += 1

        # получаем прайс лист
        parameters_66 = {
            'pointId': 123,
            'priceListId': 66,
            'withName': True,
            'page': 0
        }
        url_66 = 'https://api.sbis.ru/retail/nomenclature/list?'
        headers_66 = {
            "X-SBISAccessToken": access_token
        }
        has_more_66 = True

        while has_more_66 and count > 0:
            response_66 = requests.get(url_66, params=parameters_66, headers=headers_66)
            response_66.encoding = 'utf-8'

            if response_66.status_code == 200 and count > 0:
                data_66 = response_66.json()
                nomenclatures_66 = data_66.get('nomenclatures', [])
                for nomenclature in nomenclatures_66:
                    if count < 0:
                        break
                    name = nomenclature.get('name', '')
                    cost = nomenclature.get('cost', None)
                    unit = nomenclature.get('unit', '')
                    category_name = name.split()[0]

                    if cost and count > 0:
                        product_dict = {
                            'name': name,
                            'cost': cost,
                            'description': '',
                            'manufacturer': category_name,
                            'quantity': random.randint(1, 10)
                        }
                        if len(products) < count:
                            products.append(product_dict)
                            count -= 1
                has_more_66 = data_66.get('outcome', {}).get('hasMore', False)
                parameters_66['page'] += 1

    else:
        print(f"Ошибка при выполнении запроса. Код статуса: {response.status_code}")
    products = tuple(products)
    return products

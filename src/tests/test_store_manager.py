"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import pytest
from store_manager import app

import os
os.environ["DB_HOST"] = "localhost"
os.environ["REDIS_HOST"] = "localhost"



@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        PROPAGATE_EXCEPTIONS=True,
        PRESERVE_CONTEXT_ON_EXCEPTION=False,
    )
    with app.test_client() as client:
        yield client




def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    # 1) Create product
    product_data = {'name': 'Some Item', 'sku': '12345', 'price': 99.90}
    response = client.post('/products',
                            data=json.dumps(product_data),
                            content_type='application/json')

    #  Affiche le body
    if response.status_code >= 400:
        print("SERVER ERROR BODY (POST /products):", response.get_data(as_text=True))
    assert response.status_code in (200, 201)

    product = response.get_json() or {}
    product_id = product.get('product_id') or product.get('id')
    assert product_id, f"Réponse inattendue pour /products: {product}"

    # 2) Add 5 units
    response = client.post('/stocks',
                           data=json.dumps({'product_id': product_id, 'quantity': 5}),
                           content_type='application/json')
    if response.status_code >= 400:
        print("SERVER ERROR BODY (POST /stocks):", response.get_data(as_text=True))
    assert response.status_code in (200, 201)

    # 3) Check == 5
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code in (200, 201)
    assert (response.get_json() or {}).get('quantity') == 5

    # 4) Create order (2 units)
    response = client.post('/orders',
                           data=json.dumps({'user_id': 1,
                                            'items': [{'product_id': product_id, 'quantity': 2}]}),
                           content_type='application/json')
    if response.status_code >= 400:
        print("SERVER ERROR BODY (POST /orders):", response.get_data(as_text=True))
    assert response.status_code in (200, 201)
    order = response.get_json() or {}
    order_id = order.get('order_id') or order.get('id')
    assert order_id

    # 5) Check == 3
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code in (200, 201)
    assert (response.get_json() or {}).get('quantity') == 3

    # 6) Delete order
    response = client.delete(f'/orders/{order_id}')
    assert response.status_code in (200, 204)

    # Back to 5
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code in (200, 201)
    assert (response.get_json() or {}).get('quantity') == 5

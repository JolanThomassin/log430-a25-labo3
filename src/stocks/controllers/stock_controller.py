"""
Product stock controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from flask import jsonify
from stocks.queries.read_stock import get_stock_by_id, get_stock_for_all_products
from stocks.commands.write_stock import set_stock_for_product

# GraphQL
from stocks.schemas.query import schema  # nécessite stocks/schemas/query.py

def set_stock(request):
    """Set stock quantities of a product"""
    payload = request.get_json() or {}
    product_id = payload.get('product_id')
    quantity = payload.get('quantity')
    try:
        result = set_stock_for_product(product_id, quantity)
        return jsonify({'result': result}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_stock(product_id):
    """Get stock quantities of a product"""
    try:
        stock = get_stock_by_id(product_id)
        # 200 pour un GET ; tes tests acceptent 200/201 de toute façon
        return jsonify(stock), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_stock_overview():
    """Get stock for all products (overview report)"""
    try:
        data = get_stock_for_all_products()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def stocks_graphql_query(request):
    payload = request.get_json(silent=True) or {}
    query = payload.get("query")
    variables = payload.get("variables")

    if not query:
        return jsonify({"error": "missing 'query' field"}), 400

    try:
        result = schema.execute(query, variable_values=variables)
        if result.errors:
            return jsonify({"errors": [str(e) for e in result.errors]}), 400
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import graphene
from db import get_redis_conn
from stocks.queries.read_stock import get_stock_by_id
from stocks.queries.read_product import get_product_by_id

class ProductType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    sku = graphene.String()
    price = graphene.Float()
    quantity = graphene.Int()

class Query(graphene.ObjectType):
    # Usage: { product(id: "20") { id name sku price quantity } }
    product = graphene.Field(ProductType, id=graphene.ID(required=True))

    def resolve_product(root, info, id):
        pid = int(id)

        # Récupère en DB (pas Redis)
        prod = get_product_by_id(pid) or {}
        stock = get_stock_by_id(pid) or {}

        # Si rien en DB, renvoie null
        if not (prod or stock):
            return None

        return ProductType(
            id=pid,
            name=prod.get("name"),
            sku=prod.get("sku"),
            price=float(prod["price"]) if prod.get("price") is not None else None,
            quantity=stock.get("quantity"),
        )

schema = graphene.Schema(query=Query)
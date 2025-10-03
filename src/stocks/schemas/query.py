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
    product = graphene.Field(ProductType, id=graphene.ID(required=True))

    def resolve_product(root, info, id):
        pid = int(id)

        # 1) Redis en priorité
        r = get_redis_conn()
        data = r.hgetall(f"stock:{pid}") or {}

        if data:
            return ProductType(
                id=pid,
                name=(data.get("name") or None),
                sku=(data.get("sku") or None),
                price=float(data["price"]) if data.get("price") is not None else None,
                quantity=int(data["quantity"]) if data.get("quantity") else None,
            )

        # 2) Fallback DB (si pas présent en cache)
        prod = get_product_by_id(pid) or {}
        stock = get_stock_by_id(pid) or {}
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
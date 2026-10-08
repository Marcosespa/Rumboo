"""Formato común de listados: {items, total, page, page_size}."""
from sqlalchemy import func, select


def paginar(db, query, page, page_size, serialize):
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size))
    return {"items": [serialize(row) for row in rows], "total": total, "page": page, "page_size": page_size}

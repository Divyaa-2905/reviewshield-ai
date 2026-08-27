from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_product_id(self, product_id: str) -> Product | None:
        return self.db.query(Product).filter(Product.product_id == product_id).first()

    def get_by_id(self, product_db_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_db_id).first()

    def list_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[Product], int]:
        query = self.db.query(Product).order_by(Product.name)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def create(self, **kwargs) -> Product:
        product = Product(**kwargs)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

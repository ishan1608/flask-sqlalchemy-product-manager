import csv


def process_csv(file_path):
    from models import Product
    from server import get_db

    db = get_db()

    with open(file_path, "r") as products_csv_file:
        products_reader = csv.reader(products_csv_file)
        next(products_reader)
        for product_row in products_reader:
            product = Product(
                name=product_row[0],
                sku=product_row[1],
                description=product_row[2],
                is_active=True
            )
            db.session.add(product)
        db.session.commit()

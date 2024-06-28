from connectors.mysql_connector import connection
from flask import Blueprint, request
from models.product import Product
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user
from flasgger import swag_from

product_routes = Blueprint("product_routes", __name__)


@product_routes.route("/products", methods=['GET'])
@login_required
def product_home():
    Session = sessionmaker(connection)
    s = Session()
    # with Session() as s:

    try:
        # Logic Apps
        product_query = select(Product)

        search_keyword = request.args.get('query')
        if search_keyword != None:
            product_query = product_query.where(Product.name.like(f"%{search_keyword}%"))

        result = s.execute(product_query)
        products = []

        for row in result.scalars():
            (products.append({
                'id': row.id,
                'name': row.name,
                'price': row.price,
                'description': row.description
            }))

        return {
            'products': products,
            'message': "Hello, " + current_user.name
        }, 200

        # for row in products.scalars():
        #     print(f'ID: {row.id}, Name: {row.name}')

        # Commit
    except Exception as e:
        # Rollback
        print(e)
        # Kirim Error Message
        return {'message': 'Unexpected Error'}, 500

@product_routes.route('/product', methods=['POST'])
# @jwt_required()
def product_insert():
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        NewProduct = Product(
            name=request.form['name'],
            price=request.form['price'],
            description=request.form['description']
        )

        s.add(NewProduct)
        s.commit()
    except Exception as e:
        s.rollback()
        return {"message": "Fail to Insert"}, 500

    return {'message': 'Success insert product data'}, 200


@product_routes.route('/product/<id>', methods=['DELETE'])
def product_delete(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        product = s.query(Product).filter(Product.id == id).first()
        s.delete(product)
        s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Fail to Delete"}, 500

    return {'message': 'Success delete product data'}, 200


@product_routes.route('/product/<id>', methods=['PUT'])
def product_update(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        product = s.query(Product).filter(Product.id == id).first()

        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']

        s.commit()
    except Exception as e:
        s.rollback()
        return {"message": "Fail to Update"}, 500

    return {'message': 'Success update product data'}, 200

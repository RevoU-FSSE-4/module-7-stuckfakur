from connectors.mysql_connector import connection
from flask import Blueprint, request
from flask_login import login_required, current_user
from models.product import Product
from models.review import Review
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

review_routes = Blueprint("review_routes", __name__)


@review_routes.route("/reviews", methods=['GET'])
@login_required
def review_home():
    Session = sessionmaker(connection)
    s = Session()

    try:
        # set to get product name from product_id
        review_query = select(Review, Product.name).join(Product, Review.product_id == Product.id)

        search_keyword = request.args.get('query')
        if search_keyword:
            review_query = review_query.where(Review.description.like(f"%{search_keyword}%"))

        result = s.execute(review_query)
        reviews = []

        for row in result:
            review, product_name = row
            reviews.append({
                'id': review.id,
                'product_name': product_name,  # this is show name from product_id
                'email': review.email,
                'rating': review.rating,
                'description': review.description,
            })

        return {
            'reviews': reviews,
            'message': "Hello, " + current_user.name
        }, 200

    except Exception as e:
        print(e)
        return {'message': 'Unexpected Error'}, 500


@review_routes.route('/review', methods=['POST'])
# @jwt_required()
def product_insert():
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        NewReview = Review(
            product_id=request.form['product_id'],
            email=request.form['email'],
            rating=request.form['rating'],
            description=request.form['description']
        )

        s.add(NewReview)
        s.commit()
    except Exception as e:
        s.rollback()
        return {"message": "Fail to Insert"}, 500

    return {'message': 'Success insert review data'}, 200


@review_routes.route('/review/<id>', methods=['DELETE'])
def review_delete(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        review = s.query(Review).filter(Review.id == id).first()
        s.delete(review)
        s.commit()
    except Exception as e:
        print(e)
        s.rollback()
        return {"message": "Fail to Delete"}, 500

    return {'message': 'Success delete review data'}, 200


@review_routes.route('/review/<id>', methods=['PUT'])
def review_update(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        review = s.query(Review).filter(Review.id == id).first()

        review.product_id = request.form['product_id']
        review.email = request.form['email']
        review.rating = request.form['rating']
        review.description = request.form['description']

        s.commit()
    except Exception as e:
        s.rollback()
        return {"message": "Fail to Update"}, 500

    return {'message': 'Success update review data'}, 200

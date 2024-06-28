from flask import Flask
from flasgger import Swagger
from dotenv import load_dotenv
load_dotenv()

from connectors.mysql_connector import connection

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from models.product import Product

from controllers.product import product_routes
from controllers.review import review_routes
from controllers.user import user_routes
import os

from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from models.user import User


app = Flask(__name__)
swagger = Swagger(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.register_blueprint(product_routes)
app.register_blueprint(review_routes)
app.register_blueprint(user_routes)

# JSON Web Token
jwt = JWTManager(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(connection)
    s = Session()
    return s.query(User).get(int(user_id))

@app.route("/")
def hello_world():

    # Insert data to product table
    # Session = sessionmaker(connection)
    # with Session() as s:
    #     s.execute(text("INSERT INTO product (name, price, description) VALUES ('Tas Rajut', 56000, 'Dibuat Dari kulit sapi impor')"))
    #     s.commit()

    # Insert data using SQLAlchemy Model
    # NewProduct = Product( name="Pisau Lipat", price=30000, description="Made from Krakatau Steel")
    # Session = sessionmaker(connection)
    # with Session() as s:
    #     s.add(NewProduct)    
    #     s.commit()

    # Fetch all products using ORM
    product_query = select(Product)
    Session = sessionmaker(connection)
    with Session() as s:
        result = s.execute(product_query)
        for row in result.scalars():
            print(f'ID: {row.id}, Name: {row.name}')

    return "Insert Sukses"

if __name__ == "__main__":
    app.run(debug=True)
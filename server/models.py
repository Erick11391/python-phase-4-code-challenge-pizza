from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_restaurant_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)  # Removed unique=True from here
    address = db.Column(db.String, nullable=False)

    # Relationships
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', 
                                      cascade="all, delete-orphan")
    pizzas = association_proxy('restaurant_pizzas', 'pizza',
                             creator=lambda pizza_obj: RestaurantPizza(pizza=pizza_obj))

    # Serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurant_pizzas')

    def __repr__(self):
        return f'<Restaurant {self.name}>'

class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationships
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', 
                                      cascade="all, delete-orphan")
    restaurants = association_proxy('restaurant_pizzas', 'restaurant',
                                  creator=lambda restaurant_obj: RestaurantPizza(restaurant=restaurant_obj))

    # Serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.restaurant_pizzas')

    def __repr__(self):
        return f'<Pizza {self.name}>'

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Relationships
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')

    # Serialization rules
    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity
from user import UserRegister

app = Flask(__name__)
app.secret_key='some key'
api = Api(app)

# JWT creates a new endpoint /auth
jwt = JWT(app, authenticate, identity)

items = []

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("price",
        type=float,
        required=True,
        help = "This field cannot be left blank"
    )

    @jwt_required()
    def get(self, name):
        """
            A user has to be authenticated to send a GET request
        """

        item = next(filter(lambda item: item['name']==name, items), None) # returns the first item found
        return {"item": item}, 200 if item else 404

    @jwt_required()
    def post(self, name):
        if next(filter(lambda item: item['name']==name, items), None):
            return {"message": "An item with name {} already exists".format(name)}, 400

        data = Item.parser.parse_args()
        item = {"name": name, "price": data['price']}
        items.append(item)
        return item, 201 # to insure a client that the item has been created (that's what 201 mean)

    @jwt_required()
    def delete(self, name):
        global items
        items = list(filter(lambda item: item['name'] != name, items))
        return {"message": "{} was deleted from the database.".format(name)}

    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()
        item =  next(filter(lambda item: item['name']==name, items), None)
        if item is None:
            item = {"name": name, "price": data['price']}
            items.append(item)
        else:
            item.update(data)
        return item

class ItemList(Resource):
    def get(self):
        return {"items": items}

# 
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')

app.run(port=5000, debug=True)

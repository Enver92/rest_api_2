import sqlite3

from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("price",
        type=float,
        required=True,
        help = "This field cannot be left blank."
    )

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "SELECT * FROM items WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {"item": {"name": row[0], "price": row[1]}}

    @classmethod
    def insert(cls, item):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(query, (item['name'], item['price']))

        connection.commit()
        connection.close()

    @classmethod
    def update(cls, item):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "UPDATE items SET price=? WHERE name=?"
        cursor.execute(query, (item['price'], item['name']))
        connection.commit()
        connection.close()

    @jwt_required()
    def get(self, name):
        try:
            item = self.find_by_name(name)
        except:
            return {"message": "There was a proble while searching for an item."}, 500
        if item:
            return item
        return {"message": "Item not found"}, 404

    def post(self, name):
        if self.find_by_name(name):
            return {"message": "Item with name {} already exists.".format(name)}
        data = Item.parser.parse_args()
        item = {"name": name, "price": data['price']}
        try:
            self.insert(item)
        except:
            return {"message": "An error occured while inserting an item"}, 500

        return item, 201 # to insure a client that the item has been created (that's what 201 mean)

    def delete(self, name):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name, ))

        connection.commit()
        connection.close()
        return {"message": "Item deleted."}

    # @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()

        try:
            item =  self.find_by_name(name)
        except:
            return {"message": "There was an internal problem."}, 500
        updated_item = {"name": name, "price": data['price']}
        if item is None:
            self.insert(updated_item)
        else:
            self.update(updated_item)
        return updated_item

class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({"name": row[0], 'price': row[1]})

        connection.close()

        return {"items": items}

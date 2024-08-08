from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource 

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

api = Api(app)
CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

class Messages(Resource):
    def get(self):
        try:
            return make_response([message.to_dict() for message in Message.query], 200)
        except Exception as e:
            return make_response(str(e), 400)
    
    def post(self):
        try:
            data = request.get_json()
            new_message = Message(**data)

            db.session.add(new_message)
            db.session.commit()
            return new_message.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 400)

class MessagesById(Resource):
    def patch(self,id):
        try: 
            if message := db.session.get(Message, id):
                data = request.get_json()
                for attr, value in data.items():
                    setattr(message, attr, value)
                db.session.commit()
                return message.to_dict(), 202
            return {"error": "Message not found"}, 404
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 400)

    def delete(self, id):
        try:
            if message := db.session.get(Message, id):
                db.session.delete(message)
                db.session.commit()
                return make_response('', 204)
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 422)

api.add_resource(Messages, "/messages")
api.add_resource(MessagesById,"/messages/<int:id>")

if __name__ == '__main__':
    app.run(port=5555)

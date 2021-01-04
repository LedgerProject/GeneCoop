from flask import Flask, request
from flask_restful import Resource, Api, reqparse


consent_parser = reqparse.RequestParser()
consent_parser.add_argument('research', type=bool, required=True, help='Please specify whether research is allowed')

id_parser = reqparse.RequestParser()
id_parser.add_argument('consent_id', type=int, required=True, help='Id of the user')


# print(f'name is {__name__}')
app = Flask(__name__)
api = Api(app)

consents = {}
consent_id = 0


class Consents(Resource):
    def get(self):
        args = id_parser.parse_args()
        if args['consent_id'] in consents:
            return {args['consent_id']: consents[args['consent_id']]}
        else:
            return {'Error': f"Id not found: {args['consent_id']}"}

    def put(self):
        global consent_id
        # global consents
        args = consent_parser.parse_args()
        consents[consent_id] = args
        response = {consent_id: consents[consent_id]}
        consent_id += 1
        return response

class DataAccess(Resource):
    def get(self):
        args = id_parser.parse_args()
        if args['consent_id'] in consents:
            return {args['consent_id']: consents[args['consent_id']]}
        else:
            return {'Error': f"Id not found: {args['consent_id']}"}

    def put(self):
        global consent_id
        # global consents
        args = consent_parser.parse_args()
        consents[consent_id] = args
        response = {consent_id: consents[consent_id]}
        consent_id += 1
        return response


api.add_resource(Consents, '/consent')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0',debug=True)

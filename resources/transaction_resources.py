from flask_cors import cross_origin
import time

from flask import request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_restful_swagger_2 import swagger

from db import create_session, User, Investment, Transaction
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import re
from flask_cors import cross_origin

min_topup_sum = 10

max_topup_sum = 100


class TransactionCreateTopup(Resource):
    @cross_origin()
    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()

        parser.add_argument('sum', help='This field is required', required=True)
        args = parser.parse_args()
        if not args['sum'].isnumeric():
            return {'success': False, "message": "Sum must be numeric."}, 400

        if int(args['sum']) < min_topup_sum or int(args['sum']) > max_topup_sum:
            return {'success': False,
                    "message": f"Amount topup sum error. Max_sum = {max_topup_sum}, Min_sum = {min_topup_sum}"}, 400
        session = create_session()
        try:
            new_transaction = Transaction()
            new_transaction.user_id = current_user_id
            new_transaction.summ = int(args['sum'])
            new_transaction.type = 'topup'
            new_transaction.status = 'created'
            new_transaction.time_created = int(time.time())
            new_transaction.payment_data = "7770 5555 3323 2222"
            session = create_session()
            session.add(new_transaction)
            session.commit()
            return {'success': True, 'payment_data': "7770 5555 3323 2222", 'payment_id': new_transaction.id}, 200
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': 'db error'}, 500
        finally:
            session.close()


class TransactionCommitTopup(Resource):

    @cross_origin()
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()

        parser.add_argument('topup_id', help='This field is required', required=True)
        args = parser.parse_args()

        if not args['topup_id'].isnumeric():
            return {"success": False, "message": "topup_id must be numeric"}

        session = create_session()
        needed_topup = session.query(Transaction).filter(Transaction.user_id == current_user_id).filter(
            Transaction.id == args['topup_id']).filter(
            Transaction.type == 'topup').first()

        if not (needed_topup) or (needed_topup.status != 'created'):
            return {"success": False, "message": "Topup not found"}, 404

        try:
            needed_topup.status = 'pending'
            needed_topup.time_commited = int(time.time())
            session.add(needed_topup)
            session.commit()
            return {'success': True, 'message': 'Topup was commited succesfully'}, 200
        except Exception as e:
            session.rollback()
            return {"success": False, "message": "Db error"}, 500
        finally:
            session.close()


class TransactionGetTopup(Resource):

    @cross_origin()
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('topup_id', help='This field is required', required=True)
        args = parser.parse_args()

        session = create_session()
        needed_topup = session.query(Transaction).filter(Transaction.user_id == current_user_id).filter(
            Transaction.id == args['topup_id']).filter(
            Transaction.type == 'topup').first()

        if not (needed_topup):
            return {"success": False, "message": "Topup not found"}, 404

        return {'success': True, 'topup': needed_topup.as_dict()}, 200

import time

from flask_restful import Resource, Api, reqparse
from db import create_session, User, Token
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import re
from flask_cors import cross_origin


class GetLastFreeToken(Resource):
    @cross_origin()
    @jwt_required()
    def get(self):
        session = create_session()
        last_token = session.query(Token).filter(Token.status == 'new').first()
        if last_token:
            return {'success': True, 'token': last_token.as_dict()}


class BuyToken(Resource):
    @cross_origin()
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', help='This field is required', required=True)
        args = parser.parse_args()
        if not (args['quantity'].isnumeric()):
            return {'success': False, 'message': 'Quantity must be number'}

        if int(args['quantity']) < 1 or int(args['quantity']) > 10:
            return {'success': False, 'message': 'Quantity must be lower 10 and upper 0'}

        session = create_session()
        cur_user = session.query(User).filter(User.id == current_user_id).first()
        if cur_user.balance == 0:
            return {'success': False, 'message': 'Not enough balance'}

        tokens_to_buy = session.query(Token).filter(Token.status == 'new').limit(args['quantity']).all()
        sum_to_buy = sum(x.price for x in tokens_to_buy)

        if cur_user.balance < sum_to_buy:
            return {'success': False, 'message': 'Not enough balance'}

        try:
            cur_user.balance -= sum_to_buy
            cur_user.total_coins = args['quantity']
            for token in tokens_to_buy:
                token.status = 'bought'
                token.holder_id = current_user_id
                token.time_bought = (int(time.time()))
                session.add(token)
            if (tokens_to_buy[0].id - 1) != 0:
                print('here')
                sum_to_div = sum_to_buy // (tokens_to_buy[0].id - 1)
                print(sum_to_div)
                users_to_div = session.query(User).filter(User.total_coins > 0).filter(User.id != current_user_id).all()
                print(users_to_div)
                for user_to_div in users_to_div:
                    user_to_div.dividends_sum += (sum_to_div * user_to_div.total_coins)
                    session.add(user_to_div)
            session.add(cur_user)
            session.commit()
            session.close()
            return {'success': True, 'message': 'The purchase was successful'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error {e}'}


class GetSumTokens(Resource):
    @cross_origin()
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', help='This field is required', required=True)
        args = parser.parse_args()
        if not (args['quantity'].isnumeric()):
            return {'success': False, 'message': 'Quantity must be number'}

        if int(args['quantity']) < 1 or int(args['quantity']) > 10:
            return {'success': False, 'message': 'Quantity must be lower 10 and upper 0'}

        session = create_session()
        tokens_to_buy = session.query(Token).filter(Token.status == 'new').limit(args['quantity']).all()
        sum_to_buy = sum(x.price for x in tokens_to_buy)
        return {'success': True, 'sum': sum_to_buy}

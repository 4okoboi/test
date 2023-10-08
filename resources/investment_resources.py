import time

from flask_restful import Resource, Api, reqparse
from db import create_session, User, Packet, Investment, Transaction

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import re
from flask_cors import cross_origin


class GetPacketsList(Resource):
    @cross_origin()
    @jwt_required()
    def get(self):
        session = create_session()
        packets = session.query(Packet).all()
        packets_list = []
        for packet in packets:
            packets_list.append(packet.as_dict())
        response = {'success': True, 'packets': packets_list}, 200
        return response


class BuyPacket(Resource):
    @cross_origin()
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('id', help='This field is required', required=True)
        parser.add_argument('sum', help='This field is required', required=True)
        args = parser.parse_args()
        if not (args['id'].isnumeric()) or not (args['sum'].isnumeric()):
            return {'success': False, 'message': 'Quantity and sum must be numeric'}, 400
        session = create_session()
        packet = session.query(Packet).filter(Packet.id == args['id']).first()
        if not packet:
            return {'success': False, 'message': 'Packet not found'}, 404

        if int(args['sum']) < packet.min_sum or int(args['sum']) > packet.max_sum:
            return {'success': False, 'message': 'Sum error'}, 400

        session = create_session()
        cur_user = session.query(User).filter(User.id == current_user_id).first()
        if cur_user.balance == 0:
            return {'success': False, 'message': 'Not enough balance'}, 400

        try:
            cur_user.balance -= int(args['sum'])
            new_investment = Investment()
            new_investment.user_id = current_user_id
            new_investment.packet_id = args['id']
            new_investment.sum = -args['sum']
            new_investment.day_left = packet.time
            new_investment.status = 'active'
            new_investment.dividends = args['sum']

            new_transaction = Transaction()
            new_transaction.summ = args['sum']
            new_transaction.user_id = current_user_id
            new_transaction.status = 'success'
            new_transaction.type = 'packet_buy'

            session.add(new_transaction)
            session.add(cur_user)
            session.add(new_investment)
            session.commit()
            session.close()
            return {'success': True, 'message': 'The purchase was successful'}, 200
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Db error'}, 500

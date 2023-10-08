import os

from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from db import create_session, User, global_init, Packet
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import re

from resources.investment_resources import GetPacketsList, BuyPacket
from resources.transaction_resources import TransactionCreateTopup, TransactionCommitTopup, TransactionGetTopup
from resources.user_resources import UserRegistration, UserLogin, UserUpdate, UserSelf, GetUserInvestments
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)

CORS(app, resources={r"/*": {"origins": "*"}})

# Настройка JWT для аутентификации
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Замените на ваш секретный ключ

jwt = JWTManager(app)


@jwt.invalid_token_loader
def custom_invalid_token_callback(error):
    return jsonify({'success': False, 'message': 'Token signature verification failed'}), 401


@jwt.expired_token_loader
def custom_expired_token_callback(error):
    return jsonify({'success': False, 'message': 'Token expired'}), 401


@jwt.unauthorized_loader
def custom_auth_token_error(error):
    return jsonify({'success': False, 'message': 'Token is required'}), 401


# Ресурс для регистрации новых пользователей
# Добавляем ресурсы к API
api.add_resource(UserRegistration, '/api/user/register')
api.add_resource(UserLogin, '/api/user/login')
api.add_resource(UserUpdate, '/api/user/update/')
api.add_resource(UserSelf, '/api/user/self')
api.add_resource(GetUserInvestments, '/api/user/packets')

api.add_resource(TransactionCreateTopup, '/api/transaction/create/topup')
api.add_resource(TransactionCommitTopup, '/api/transaction/commit/topup')
api.add_resource(TransactionGetTopup, '/api/transaction/get/topup')

api.add_resource(GetPacketsList, '/api/packet/all')
api.add_resource(BuyPacket, '/api/packet/buy')

if __name__ == '__main__':
    global_init('sqlite:///users.sqlite')

    app.run(debug=True, host='127.0.0.1', port=os.environ.get('PORT', '3000'))

import time

from flask import request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_restful_swagger_2 import swagger

from db import create_session, User, Investment, Transaction
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import re
from flask_cors import cross_origin


class UserRegistration(Resource):
    @cross_origin()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='This field is required', required=True)
        parser.add_argument('password', help='This field is required', required=True)
        parser.add_argument('email', help='This field is required', required=True)
        args = parser.parse_args()

        password_pattern = '^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        email_pattern = '([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)'

        session = create_session()
        existing_user = session.query(User).filter_by(email=args['email']).first()
        if existing_user:
            return {'success': False, 'message': 'User with that email already exists'}, 400
        if not re.match(password_pattern, args['password']):
            return {'success': False, 'message': 'Password error'}, 400
        if not re.match(email_pattern, args['email']):
            return {'success': False, 'message': 'Email error'}, 400
        try:
            user = User(username=args['username'], balance=0, frozen_balance=0, email=args['email'],
                        role='user')
            user.set_password(args['password'])
            print(user.email)
            session.add(user)
            session.commit()
            return {'success': True, 'message': 'User registered successfully'}, 201
        except Exception as e:
            session.rollback()
            print(e)
            return {'success': False, 'message': 'Db error'}, 500
        finally:
            session.close()


# Ресурс для аутентификации и выдачи токена доступа
class UserLogin(Resource):
    @cross_origin()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', help='This field is required', required=True)
        parser.add_argument('password', help='This field is required', required=True)
        args = parser.parse_args()

        session = create_session()
        user = session.query(User).filter_by(email=args['email']).first()

        if user and user.check_password(args['password']):
            access_token = create_access_token(identity=user.id)
            session.close()
            return {'success': True, 'access_token': access_token}, 200
        else:
            session.close()
            return {'success': False, 'message': 'Invalid credentials'}, 401


class UserUpdate(Resource):
    @cross_origin()
    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        password_pattern = '^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

        parser.add_argument('username', help='This field is required', required=True)
        parser.add_argument('old_password', help='This field is required', required=True)
        parser.add_argument('new_password', help='This field is required', required=True)

        args = parser.parse_args()

        session = create_session()
        cur_user = session.query(User).filter(User.id == current_user_id).first()

        if args['username']:
            cur_user = session.query(User).filter(User.id == current_user_id).first()
            cur_user.username = args['username']
        if args['new_password']:
            if not cur_user.check_password(args['old_password']):
                return {'success': False, 'message': 'Old passwor does not match'}, 400
            if not re.match(password_pattern, args['new_password']):
                return {'success': False, 'message': 'Password error'}, 400

            cur_user.set_password(args['new_password'])

        session.add(cur_user)
        session.commit()
        session.close()
        return {'success': True, 'message': 'User has updated'}, 200


class UserSelf(Resource):
    @cross_origin()
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()

        session = create_session()
        cur_user = session.query(User).filter(User.id == current_user_id).first()
        if cur_user:
            return {'success': True, 'user': cur_user.as_dict()}


class GetUserInvestments(Resource):

    @cross_origin()
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()

        session = create_session()
        user_investments = session.query(Investment).filter(Investment.user_id == current_user_id).all()
        user_investments_list = []
        for investment in user_investments:
            user_investments_list.append(investment.as_dict())
        return {'success': True, 'investments_list': user_investments_list}

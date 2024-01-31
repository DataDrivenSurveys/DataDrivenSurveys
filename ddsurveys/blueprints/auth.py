#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import annotations

import traceback
from datetime import timedelta

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from ..get_logger import get_logger
from ..models import Researcher, get_db

logger = get_logger(__name__)


auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['POST'])
def signup():

    try:
        with get_db() as db:
            data = request.get_json()

            # check if user already exists
            user = db.query(Researcher).filter_by(email=data['email']).first()
            if user:
                return jsonify({'message': {'id': 'api.auth.user_already_exists', 'text': 'User already exists'}}), 409

            firstname = data.get('firstname')
            lastname = data.get('lastname')

            if not firstname or firstname == '':
                logger.debug(f"Failed to register: no firstname")
                return jsonify({"message": {"id": "api.auth.firstname_required", 'text': 'First name is required'}}), 400

            if not lastname or lastname == '':
                logger.debug(f"Failed to register: no lastname")
                return jsonify({"message": {"id": "api.auth.lastname_required", 'text': 'Last name is required'}}), 400

            if not data['email'] or data['email'] == '':
                logger.debug(f"Failed to register: no email")
                return jsonify({"message": {"id": "api.auth.email_required", 'text': 'Email is required'}}), 400

            if not data['password'] or data['password'] == '':
                logger.debug(f"Failed to register: no password")
                return jsonify({"message": {"id": "api.auth.password_required", 'text': 'Password is required'}}), 400

            hashed_password = generate_password_hash(data['password'], method='scrypt')

            new_researcher = Researcher(
                firstname=firstname,
                lastname=lastname,
                email=data['email'],
                password=hashed_password
            )
            db.add(new_researcher)
            db.commit()
            logger.info(f"Successfully registered: {new_researcher.email}")
            return jsonify({'message': {'id': 'api.auth.registered_successfully', 'text': 'Registered successfully'}}), 200
    except Exception as e:
        logger.critical(f"This error should be excepted correctly: {e}")
        logger.error(f"Failed to register: {traceback.format_exc()}")
        return jsonify({"message": {"id": "api.auth.registration_failed", 'text': 'Failed to register'}}), 500


@auth.route('/signin', methods=['POST'])
def signin():
    with get_db() as db:
        data = request.get_json()
        user = db.query(Researcher).filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'message': {'id': 'api.auth.invalid_username_or_password', 'text': 'Invalid username or password'}}), 401
        token = create_access_token(
            identity={
                'id': user.id,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email
            }
        )
        logger.info(f"Successfully signed in: {user.email}")
        return jsonify({'token': token}), 200


@auth.route('/me', methods=['GET'])
@jwt_required()
def session():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

#!/usr/bin/env python3
"""
view that handles all routes for the Session authentication.
"""

import os
from api.v1.views import app_views
from flask import jsonify, abort, request
from models.user import User


@app_views.route('/auth_session/login', methods=['POST'],
                 strict_slashes=False)
def login():
    """
    implements user login
    """
    password = request.form.get('password', None)
    email = request.form.get('email', None)

    if email is None:
        return jsonify({"error": "email missing"}), 400
    if password is None:
        return jsonify({"error": "password missing"}), 400

    # User.load_from_file()
    user_exist = User.search({'email': email})
    if not user_exist:
        return jsonify({"error": "no user found for this email"}), 404

    for user in user_exist:
        if user.is_valid_password(password) is False:
            return jsonify({"error": "wrong password"}), 401
        try:
            from api.v1.app import auth
            session_id = auth.create_session(user.id)
            response = jsonify(user.to_json())
            response.set_cookie(os.getenv('SESSION_NAME'), session_id)
            return response
        except Exception:
            return jsonify({"error": "no user found for this email"}), 404


@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def logout():
    """
    Logout
    """
    from api.v1.app import auth
    if not auth.destroy_session(request):
        abort(404)
    auth.destroy_session(request)
    return jsonify({}), 200

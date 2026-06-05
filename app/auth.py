from functools import wraps
from flask import session, redirect, url_for, jsonify, request


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'uid' not in session:
            if request.is_json:
                return jsonify({'error': 'No autenticado'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'uid' not in session:
                if request.is_json:
                    return jsonify({'error': 'No autenticado'}), 401
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                if request.is_json:
                    return jsonify({'error': 'Sin permisos'}), 403
                return redirect(url_for('auth.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

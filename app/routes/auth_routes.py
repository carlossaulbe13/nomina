from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from firebase_admin import auth

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if 'uid' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login')
def login():
    if 'uid' in session:
        return redirect(url_for('auth.dashboard'))
    return render_template('login.html')


@auth_bp.route('/auth/session', methods=['POST'])
def create_session():
    data = request.get_json()
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({'error': 'Token requerido'}), 400

    try:
        decoded = auth.verify_id_token(id_token, clock_skew_seconds=10)
        uid = decoded['uid']
        user = auth.get_user(uid)
        claims = user.custom_claims or {}

        session['uid'] = uid
        session['email'] = user.email
        session['nombre'] = user.display_name or user.email
        session['role'] = claims.get('role', 'viewer')
        session['sucursal_id'] = data.get('sucursal_id') or claims.get('sucursal_id')

        return jsonify({'success': True, 'role': session['role']})
    except Exception as e:
        return jsonify({'error': str(e)}), 401


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
def dashboard():
    if 'uid' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', user=session)

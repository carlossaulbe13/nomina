from flask import Blueprint, render_template, request, jsonify, session
from app.auth import role_required
from app.services.usuarios_service import (
    get_all_usuarios, create_usuario, update_usuario, toggle_usuario
)

usuarios_bp = Blueprint('usuarios', __name__)

SUCURSALES = {'s1': '6 PTE.', 's2': '12 PTE.'}


@usuarios_bp.route('/')
@role_required('dueno')
def index():
    return render_template('usuarios/index.html', user=session, sucursales=SUCURSALES)


@usuarios_bp.route('/api', methods=['GET'])
@role_required('dueno')
def api_list():
    return jsonify(get_all_usuarios())


@usuarios_bp.route('/api', methods=['POST'])
@role_required('dueno')
def api_create():
    data = request.get_json()
    try:
        usuario = create_usuario(
            data['usuario'], data['password'], data['nombre'],
            data['role'], data.get('sucursal_id') or None
        )
        return jsonify(usuario), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@usuarios_bp.route('/api/<uid>', methods=['PUT'])
@role_required('dueno')
def api_update(uid):
    data = request.get_json()
    try:
        update_usuario(uid, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@usuarios_bp.route('/api/<uid>/toggle', methods=['POST'])
@role_required('dueno')
def api_toggle(uid):
    data = request.get_json()
    toggle_usuario(uid, data.get('activo', True))
    return jsonify({'success': True})

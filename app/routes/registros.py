from flask import Blueprint, render_template, request, jsonify, session
from app.auth import login_required
from app.services.registros_service import (
    get_registros_by_date, create_registro, delete_registro, update_registro, ROLES,
    create_corte, delete_corte, tiene_descanso_semana,
)
from datetime import date

registros_bp = Blueprint('registros', __name__)


@registros_bp.route('/')
@login_required
def index():
    return render_template('registros/index.html', user=session, roles=ROLES)


@registros_bp.route('/api', methods=['GET'])
@login_required
def api_list():
    fecha = request.args.get('fecha', date.today().isoformat())
    registros = get_registros_by_date(fecha)
    return jsonify(registros)


@registros_bp.route('/api', methods=['POST'])
@login_required
def api_create():
    data = request.get_json()
    data['registrado_por'] = session.get('uid')
    data['registrado_nombre'] = session.get('nombre')
    result = create_registro(data)
    if result.get('error'):
        return jsonify(result), 400
    return jsonify(result), 201


@registros_bp.route('/api/<key>', methods=['PATCH'])
@login_required
def api_update(key):
    data = request.get_json()
    update_registro(key, data['rol'])
    return jsonify({'success': True})


@registros_bp.route('/api/<key>', methods=['DELETE'])
@login_required
def api_delete(key):
    delete_registro(key)
    return jsonify({'success': True})


@registros_bp.route('/check-descanso', methods=['GET'])
@login_required
def api_check_descanso():
    empleado_id = request.args.get('empleado_id')
    fecha = request.args.get('fecha')
    if not empleado_id or not fecha:
        return jsonify({'error': 'Faltan parámetros'}), 400
    tiene = tiene_descanso_semana(empleado_id, fecha)
    return jsonify({'tiene_descanso': tiene})


@registros_bp.route('/corte', methods=['POST'])
@login_required
def api_create_corte():
    data = request.get_json()
    create_corte(data['fecha'], session.get('sucursal_id'), session.get('uid'), session.get('nombre'))
    return jsonify({'success': True})


@registros_bp.route('/corte/<fecha>/<sucursal_id>', methods=['DELETE'])
@login_required
def api_delete_corte(fecha, sucursal_id):
    delete_corte(fecha, sucursal_id)
    return jsonify({'success': True})

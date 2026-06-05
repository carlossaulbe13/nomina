from flask import Blueprint, render_template, request, jsonify, session
from app.auth import login_required
from app.services.nomina_service import get_nomina_semanal, get_semanas_disponibles, set_pago_sucursal, delete_semana, get_cobros, set_cobro, delete_cobro
from datetime import date

nomina_bp = Blueprint('nomina', __name__)


@nomina_bp.route('/')
@login_required
def index():
    return render_template('nomina/index.html', user=session)


@nomina_bp.route('/api', methods=['GET'])
@login_required
def api_nomina():
    today = date.today()
    iso = today.isocalendar()
    semana = request.args.get('semana', f"{iso[0]}-W{iso[1]:02d}")
    sucursal_id = request.args.get('sucursal_id') or None
    nomina = get_nomina_semanal(semana, sucursal_id)
    return jsonify(nomina)


@nomina_bp.route('/api/semanas', methods=['GET'])
@login_required
def api_semanas():
    semanas = get_semanas_disponibles()
    return jsonify(semanas)


@nomina_bp.route('/api/pago_sucursal', methods=['POST'])
@login_required
def api_set_pago():
    data = request.get_json()
    set_pago_sucursal(data['semana'], data['empleado_id'], data['sucursal_id'])
    return jsonify({'success': True})


@nomina_bp.route('/api/semana/<semana>', methods=['DELETE'])
@login_required
def api_delete_semana(semana):
    delete_semana(semana)
    return jsonify({'success': True})


@nomina_bp.route('/api/cobros', methods=['GET'])
@login_required
def api_get_cobros():
    semana = request.args.get('semana', '')
    return jsonify(get_cobros(semana))


@nomina_bp.route('/api/cobros', methods=['POST'])
@login_required
def api_set_cobro():
    data = request.get_json()
    set_cobro(data['semana'], data['empleado_id'])
    return jsonify({'success': True})


@nomina_bp.route('/api/cobros/<empleado_id>', methods=['DELETE'])
@login_required
def api_delete_cobro(empleado_id):
    semana = request.args.get('semana', '')
    delete_cobro(semana, empleado_id)
    return jsonify({'success': True})

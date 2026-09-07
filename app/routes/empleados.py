from flask import Blueprint, render_template, request, jsonify, session
from app.auth import login_required, role_required
from app.services.empleados_service import (
    get_all_empleados, create_empleado, update_empleado, deactivate_empleado,
    delete_empleado
)

empleados_bp = Blueprint('empleados', __name__)

SUCURSALES = {'s1': '6 PTE.', 's2': '12 PTE.'}


@empleados_bp.route('/')
@login_required
def index():
    return render_template('empleados/index.html', user=session, sucursales=SUCURSALES)


@empleados_bp.route('/api', methods=['GET'])
@login_required
def api_list():
    empleados = get_all_empleados()
    return jsonify(empleados)


@empleados_bp.route('/api', methods=['POST'])
@login_required
def api_create():
    data = request.get_json()
    empleado = create_empleado(data)
    return jsonify(empleado), 201


@empleados_bp.route('/api/<empleado_id>', methods=['PUT'])
@login_required
def api_update(empleado_id):
    data = request.get_json()
    update_empleado(empleado_id, data)
    return jsonify({'success': True})


@empleados_bp.route('/api/<empleado_id>', methods=['DELETE'])
@login_required
def api_delete(empleado_id):
    deactivate_empleado(empleado_id)
    return jsonify({'success': True})


# Borrado definitivo, separado de la baja y solo para el dueno: la baja se
# deshace desde la misma pantalla, esto no.
@empleados_bp.route('/api/<empleado_id>/definitivo', methods=['DELETE'])
@role_required('dueno')
def api_delete_definitivo(empleado_id):
    delete_empleado(empleado_id)
    return jsonify({'success': True})

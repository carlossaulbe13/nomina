from firebase_admin import db
from datetime import date, timedelta

DIAS_ES = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']


def _semana_a_fechas(semana_str):
    year, week = semana_str.split('-W')
    # El lunes ISO menos 2 días = el sábado que inicia la semana (sáb→vie)
    monday = date.fromisocalendar(int(year), int(week), 1)
    saturday = monday - timedelta(days=2)
    return [(saturday + timedelta(days=i)).isoformat() for i in range(7)]


def _registros_de_semana(semana_str):
    """Trae solo los registros de esa semana. Las fechas son ISO (YYYY-MM-DD),
    así que el orden lexicográfico de Firebase coincide con el cronológico.
    Requiere el índice .indexOn ["fecha"] en /registros."""
    fechas = _semana_a_fechas(semana_str)
    return db.reference('registros') \
        .order_by_child('fecha') \
        .start_at(fechas[0]) \
        .end_at(fechas[-1]) \
        .get() or {}


def get_nomina_semanal(semana, sucursal_id=None):
    data = _registros_de_semana(semana)
    pago_overrides = db.reference(f'pago_sucursal/{semana}').get() or {}
    fechas = _semana_a_fechas(semana)
    empleados_map = {}

    for reg in data.values():
        if sucursal_id and reg.get('sucursal_id') != sucursal_id:
            continue
        emp_id = reg['empleado_id']
        if emp_id not in empleados_map:
            empleados_map[emp_id] = {
                'empleado_id': emp_id,
                'nombre': reg['nombre_empleado'],
                'sucursales_trabajadas': [],
                'sucursal_pago': pago_overrides.get(emp_id, reg.get('sucursal_id', '')),
                'dias': {},
                'total': 0,
            }
        suc = reg.get('sucursal_id', '')
        if suc and suc not in empleados_map[emp_id]['sucursales_trabajadas']:
            empleados_map[emp_id]['sucursales_trabajadas'].append(suc)
        empleados_map[emp_id]['dias'][reg['fecha']] = {
            'rol': reg['rol'],
            'tarifa': reg['tarifa'],
            'sucursal_id': suc,
        }
        empleados_map[emp_id]['total'] += reg['tarifa']

    empleados = sorted(empleados_map.values(), key=lambda x: x['nombre'])

    totales_sucursal = {}
    for emp in empleados:
        sp = emp['sucursal_pago'] or 'sin_sucursal'
        totales_sucursal[sp] = totales_sucursal.get(sp, 0) + emp['total']

    return {
        'semana': semana,
        'fechas': fechas,
        'dias_labels': [DIAS_ES[(date.fromisoformat(f).weekday() + 1) % 7] for f in fechas],
        'empleados': empleados,
        'gran_total': sum(e['total'] for e in empleados),
        'totales_sucursal': totales_sucursal,
    }


def get_semanas_disponibles():
    # Índice mantenido por registros_service.create_registro: una clave por
    # semana en vez de recorrer todos los registros históricos.
    semanas = db.reference('semanas').get() or {}
    return sorted(semanas.keys(), reverse=True)


def set_pago_sucursal(semana, empleado_id, sucursal_id):
    db.reference(f'pago_sucursal/{semana}/{empleado_id}').set(sucursal_id)


def delete_semana(semana):
    data = _registros_de_semana(semana)
    if data:
        # Un solo update multi-path (valor None = borrar) en vez de N requests.
        db.reference('registros').update({key: None for key in data})
    db.reference(f'pago_sucursal/{semana}').delete()
    db.reference(f'semanas/{semana}').delete()


def get_cobros(semana):
    data = db.reference(f'cobros/{semana}').get() or {}
    return list(data.keys())


def set_cobro(semana, empleado_id):
    db.reference(f'cobros/{semana}/{empleado_id}').set(True)


def delete_cobro(semana, empleado_id):
    db.reference(f'cobros/{semana}/{empleado_id}').delete()

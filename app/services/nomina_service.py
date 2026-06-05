from firebase_admin import db
from datetime import date, timedelta

DIAS_ES = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']


def _semana_a_fechas(semana_str):
    year, week = semana_str.split('-W')
    # El lunes ISO menos 1 día = el domingo que inicia la semana
    monday = date.fromisocalendar(int(year), int(week), 1)
    sunday = monday - timedelta(days=1)
    return [(sunday + timedelta(days=i)).isoformat() for i in range(7)]


def get_nomina_semanal(semana, sucursal_id=None):
    all_data = db.reference('registros').get() or {}
    data = {k: v for k, v in all_data.items() if v.get('semana') == semana}
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
    data = db.reference('registros').get() or {}
    semanas = {v['semana'] for v in data.values() if 'semana' in v}
    return sorted(semanas, reverse=True)


def set_pago_sucursal(semana, empleado_id, sucursal_id):
    db.reference(f'pago_sucursal/{semana}/{empleado_id}').set(sucursal_id)


def delete_semana(semana):
    all_data = db.reference('registros').get() or {}
    keys = [k for k, v in all_data.items() if v.get('semana') == semana]
    for key in keys:
        db.reference(f'registros/{key}').delete()
    db.reference(f'pago_sucursal/{semana}').delete()


def get_cobros(semana):
    data = db.reference(f'cobros/{semana}').get() or {}
    return list(data.keys())


def set_cobro(semana, empleado_id):
    db.reference(f'cobros/{semana}/{empleado_id}').set(True)


def delete_cobro(semana, empleado_id):
    db.reference(f'cobros/{semana}/{empleado_id}').delete()

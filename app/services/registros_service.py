from firebase_admin import db
from datetime import date, timedelta

ROLES = {
    'cajero': 500,
    'apoyo': 430,
    'mole': 430,
    'brasero': 430,
    'aguas': 430,
    'loza': 430,
    'mesero': 320,
    'descanso': 430,
    'permiso': 0,
}


def _semana(fecha_str):
    d = date.fromisoformat(fecha_str)
    # Desplazar +2 días para que el sábado sea inicio de semana (sáb→vie)
    shifted = d + timedelta(days=2)
    iso = shifted.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def get_registros_by_date(fecha):
    # Requiere el índice .indexOn ["fecha"] en /registros.
    data = db.reference('registros').order_by_child('fecha').equal_to(fecha).get() or {}
    result = [{'key': k, **v} for k, v in data.items()]
    result.sort(key=lambda x: x.get('nombre_empleado', ''))
    return result


def create_registro(data):
    emp_id = data['empleado_id']
    fecha = data.get('fecha', date.today().isoformat())
    key = f"{emp_id}_{fecha}"

    existing = db.reference(f'registros/{key}').get()
    if existing:
        return {'error': f"Ya hay un registro para este empleado el {fecha}"}

    rol = data['rol']
    semana = _semana(fecha)
    registro = {
        'empleado_id': emp_id,
        'nombre_empleado': data['nombre_empleado'],
        'rol': rol,
        'tarifa': ROLES.get(rol, 0),
        'fecha': fecha,
        'semana': semana,
        'sucursal_id': data.get('sucursal_id', ''),
        'registrado_por': data.get('registrado_por', ''),
        'registrado_nombre': data.get('registrado_nombre', ''),
    }
    db.reference(f'registros/{key}').set(registro)
    # Índice de semanas que consume nomina_service.get_semanas_disponibles.
    db.reference(f'semanas/{semana}').set(True)
    return {'key': key, **registro}


def delete_registro(key):
    db.reference(f'registros/{key}').delete()


def update_registro(key, rol):
    tarifa = ROLES.get(rol, 0)
    db.reference(f'registros/{key}').update({'rol': rol, 'tarifa': tarifa})


def get_corte(fecha):
    return db.reference(f'cortes/{fecha}').get()


def create_corte(fecha, sucursal_id, uid, nombre):
    db.reference(f'cortes/{fecha}/{sucursal_id}').set({
        'cerrado': True,
        'cerrado_por': uid,
        'cerrado_nombre': nombre,
        'fecha': fecha,
        'sucursal_id': sucursal_id,
    })


def delete_corte(fecha, sucursal_id):
    db.reference(f'cortes/{fecha}/{sucursal_id}').delete()


def tiene_descanso_semana(empleado_id, fecha_str):
    semana = _semana(fecha_str)
    d = date.fromisoformat(fecha_str)
    for delta in range(-6, 7):
        check_date = (d + timedelta(days=delta)).isoformat()
        if _semana(check_date) != semana:
            continue
        reg = db.reference(f'registros/{empleado_id}_{check_date}').get()
        if reg and reg.get('rol') == 'descanso':
            return True
    return False

import uuid
from firebase_admin import db


def get_all_empleados():
    data = db.reference('empleados').get() or {}
    result = [{'id': k, **v} for k, v in data.items()]
    result.sort(key=lambda x: x.get('nombre', ''))
    return result


def create_empleado(data):
    emp_id = uuid.uuid4().hex[:8]
    empleado = {
        'nombre': data['nombre'],
        'sucursal_id': data['sucursal_id'],
        'activo': True,
    }
    db.reference(f'empleados/{emp_id}').set(empleado)
    return {'id': emp_id, **empleado}


def update_empleado(emp_id, data):
    allowed = ['nombre', 'sucursal_id', 'activo']
    update = {k: v for k, v in data.items() if k in allowed}
    db.reference(f'empleados/{emp_id}').update(update)


def deactivate_empleado(emp_id):
    db.reference(f'empleados/{emp_id}').update({'activo': False})


def delete_empleado(emp_id):
    """Borra al empleado del catalogo. Los registros de turnos se quedan como
    estan a proposito: cada uno guarda por su cuenta nombre, rol y tarifa, asi
    que las nominas ya cerradas siguen cuadrando aunque el empleado ya no exista.
    Lo unico que se pierde es poder capturarle turnos nuevos."""
    db.reference(f'empleados/{emp_id}').delete()

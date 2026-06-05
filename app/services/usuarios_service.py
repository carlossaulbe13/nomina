from firebase_admin import auth

DOMINIO = '@restaurante.local'


def _email(usuario):
    return f"{usuario.lower()}{DOMINIO}"


def get_all_usuarios():
    result = []
    for user in auth.list_users().iterate_all():
        claims = user.custom_claims or {}
        result.append({
            'uid': user.uid,
            'usuario': (user.email or '').replace(DOMINIO, ''),
            'nombre': user.display_name or '',
            'role': claims.get('role', ''),
            'sucursal_id': claims.get('sucursal_id', ''),
            'activo': not user.disabled,
        })
    result.sort(key=lambda x: x['nombre'])
    return result


def create_usuario(usuario, password, nombre, role, sucursal_id=None):
    email = _email(usuario)
    user = auth.create_user(email=email, password=password, display_name=nombre)
    claims = {'role': role}
    if sucursal_id:
        claims['sucursal_id'] = sucursal_id
    auth.set_custom_user_claims(user.uid, claims)
    return {
        'uid': user.uid,
        'usuario': usuario,
        'nombre': nombre,
        'role': role,
        'sucursal_id': sucursal_id or '',
        'activo': True,
    }


def update_usuario(uid, data):
    update = {}
    if 'nombre' in data:
        update['display_name'] = data['nombre']
    if 'password' in data and data['password']:
        update['password'] = data['password']
    if update:
        auth.update_user(uid, **update)

    user = auth.get_user(uid)
    claims = dict(user.custom_claims or {})
    if 'role' in data:
        claims['role'] = data['role']
    if 'sucursal_id' in data:
        if data['sucursal_id']:
            claims['sucursal_id'] = data['sucursal_id']
        elif 'sucursal_id' in claims:
            del claims['sucursal_id']
    auth.set_custom_user_claims(uid, claims)


def toggle_usuario(uid, activo):
    auth.update_user(uid, disabled=not activo)

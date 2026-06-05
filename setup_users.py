"""
Corre este script para crear y gestionar usuarios del sistema.
Uso: python setup_users.py

Los usuarios se identifican con un nombre de usuario simple (sin correo).
Internamente se convierte a usuario@restaurante.local para Firebase.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate(os.environ.get('FIREBASE_CREDENTIALS', 'serviceAccountKey.json'))
firebase_admin.initialize_app(cred)

DOMINIO = '@restaurante.local'


def _email(usuario):
    return f"{usuario.lower()}{DOMINIO}"


def crear_usuario(usuario, password, nombre, role, sucursal_id=None):
    email = _email(usuario)
    try:
        user = auth.create_user(email=email, password=password, display_name=nombre)
        claims = {'role': role}
        if sucursal_id:
            claims['sucursal_id'] = sucursal_id
        auth.set_custom_user_claims(user.uid, claims)
        print(f"  ✓ {nombre} (usuario: {usuario}) — {role}" + (f" — {sucursal_id}" if sucursal_id else ""))
        return user
    except Exception as e:
        print(f"  ✗ Error: {e}")


def listar_usuarios():
    print("\n  Nombre                      Usuario           Rol        Sucursal")
    print("  " + "-" * 70)
    for user in auth.list_users().iterate_all():
        claims = user.custom_claims or {}
        nombre = (user.display_name or '—')[:26]
        usuario = (user.email or '—').replace(DOMINIO, '')[:16]
        role = claims.get('role', '—')
        suc = claims.get('sucursal_id', 'todas')
        print(f"  {nombre:<28} {usuario:<18} {role:<10} {suc}")


def actualizar_rol(usuario, role, sucursal_id=None):
    user = auth.get_user_by_email(_email(usuario))
    claims = dict(user.custom_claims or {})
    claims['role'] = role
    if sucursal_id:
        claims['sucursal_id'] = sucursal_id
    elif 'sucursal_id' in claims and role == 'dueno':
        del claims['sucursal_id']
    auth.set_custom_user_claims(user.uid, claims)
    print(f"  ✓ Rol actualizado: {usuario} → {role}")


if __name__ == '__main__':
    print("\n=== Gestión de usuarios — Restaurante ===\n")
    print("  1. Crear usuario")
    print("  2. Listar usuarios")
    print("  3. Actualizar rol de usuario")
    print()

    op = input("  Opción: ").strip()

    if op == '1':
        usuario = input("  Nombre de usuario (ej: carlos): ").strip()
        password = input("  Contraseña (mín. 6 caracteres): ").strip()
        nombre = input("  Nombre completo: ").strip()
        print("  Roles disponibles: encargado, dueno")
        role = input("  Rol: ").strip()
        sucursal = None
        if role == 'encargado':
            sucursal = input("  Sucursal (s1 / s2): ").strip()
        crear_usuario(usuario, password, nombre, role, sucursal)

    elif op == '2':
        listar_usuarios()

    elif op == '3':
        usuario = input("  Nombre de usuario: ").strip()
        print("  Roles disponibles: encargado, dueno")
        role = input("  Nuevo rol: ").strip()
        sucursal = None
        if role == 'encargado':
            sucursal = input("  Sucursal (s1 / s2): ").strip()
        actualizar_rol(usuario, role, sucursal)

    print()

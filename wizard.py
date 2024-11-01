import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
import sys
import termios
import tty

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Ruta a config.py en la estructura del proyecto clonado
config_path = "./app/config.py"

# Intentar conectar al servidor de base de datos en un bucle
while True:
    db_user = input("Ingrese el usuario de la base de datos: ")
    db_password = input("Ingrese la contraseña de la base de datos: ")
    db_host = input("Ingrese la dirección del host de la base de datos (default: localhost): ") or "localhost"

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/")
        connection = engine.connect()
        print("Conexión al servicio de base de datos verificada exitosamente.")
        break
    except OperationalError as e:
        if "Access denied" in str(e):
            print("\033[91mNo se pudo conectar al servicio de MySQL. Presione Esc para cancelar o Enter para volver a ingresar usuario y clave.\033[0m")
        else:
            print("\033[91mError de conexión al servicio de MySQL. Verifique si el servicio está activo y accesible.\033[0m")
        while True:
            print("¿Desea intentarlo de nuevo? (Enter para continuar, Esc para cancelar): ", end="", flush=True)
            confirm = get_key()
            if confirm == '\x1b':
                print("\nInstalación cancelada.")
                exit(0)
            elif confirm == '\r' or confirm == '\n':
                print("\nReintentando conexión...")
                break
            else:
                print("\nOpción no válida. Presione Esc para cancelar o Enter para continuar.")

# Guardar la configuración de la base de datos en config.py
db_name = input("Ingrese el nombre de la base de datos: ")
with open(config_path, "w") as config_file:
    config_file.write(f"""class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
""")

print(f"Archivo de configuración {config_path} actualizado con los datos de conexión.")

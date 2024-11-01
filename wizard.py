import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import sys
import termios
import tty
import subprocess

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Intentar conectar al servidor de base de datos en un bucle
while True:
    # Solicitar usuario, contraseña y host de la base de datos
    db_user = input("Ingrese el usuario de la base de datos: ")
    db_password = input("Ingrese la contraseña de la base de datos: ")
    db_host = input("Ingrese la dirección del host de la base de datos (default: localhost): ") or "localhost"

    # Intentar conectar al servidor de base de datos
    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/")
        connection = engine.connect()
        print("Conexión al servicio de base de datos verificada exitosamente.")
        break  # Salir del bucle si la conexión es exitosa
    except OperationalError:
        print("\033[91mNo se pudo conectar al servicio de MySQL. Presione Esc para cancelar o Enter para volver a ingresar usuario y clave.\033[0m")
        
        # Confirmación con Enter para reintentar, Esc para salir
        while True:
            print("¿Desea intentarlo de nuevo? (Enter para continuar, Esc para cancelar): ", end="", flush=True)
            confirm = get_key()
            if confirm == '\x1b':  # Esc key code
                print("\nInstalación cancelada.")
                exit(0)
            elif confirm == '\r' or confirm == '\n':  # Enter key code
                print("\nReintentando conexión...")
                break  # Volver al inicio del bucle para reingresar usuario y clave
            else:
                print("\nOpción no válida. Presione Esc para cancelar o Enter para continuar.")

# Obtener las bases de datos disponibles, excluyendo las bases de datos del sistema
result = connection.execute(text("SHOW DATABASES;"))
databases = [row[0] for row in result if row[0] not in ("mysql", "performance_schema", "information_schema")]

# Listar opciones de bases de datos
while True:
    print("\nSeleccione una opción:")
    print("0 - Crear una nueva base de datos")
    for i, db_name in enumerate(databases, start=1):
        print(f"{i} - {db_name}")

    # Solicitar selección de base de datos o creación de una nueva
    selection = input("Ingrese el número de la base de datos o 0 para crear una nueva: ")

    if selection == "0":
        # Verificar permisos para crear una nueva base de datos
        try:
            connection.execute(text("CREATE DATABASE test_permission_check;"))
            connection.execute(text("DROP DATABASE test_permission_check;"))  # Limpiar prueba
            new_db_name = input("Ingrese el nombre de la nueva base de datos: ")
            connection.execute(text(f"CREATE DATABASE {new_db_name};"))
            print(f"Base de datos '{new_db_name}' creada exitosamente.")
            db_name = new_db_name
            break
        except ProgrammingError:
            print("\033[91mNo tiene permisos para crear una nueva base de datos. Seleccione una de las anteriores.\033[0m")
    else:
        # Seleccionar una base de datos existente
        try:
            db_name = databases[int(selection) - 1]
            print(f"\033[38;5;214m¿Quiere hacer un backup de la base de datos '{db_name}' antes de utilizarla? Recuerde que todo el contenido actual será eliminado. (Enter para hacer backup, Esc para omitir):\033[0m", end="", flush=True)
            confirm = get_key()
            if confirm == '\r' or confirm == '\n':  # Enter key code for backup
                backup_file = f"{db_name}_backup.sql"
                os.environ['MYSQL_PWD'] = db_password  # Usar MYSQL_PWD para evitar pasar la contraseña en línea de comando
                dump_cmd = ["mysqldump", "-u", db_user, "-h", db_host, db_name]
                with open(backup_file, "w") as f:
                    subprocess.run(dump_cmd, stdout=f)
                del os.environ['MYSQL_PWD']  # Eliminar la variable de entorno por seguridad
                print(f"\nBackup de la base de datos '{db_name}' guardado como {backup_file}.")
            elif confirm != '\x1b':
                print(f"\nNo se realizó el backup.")

            # Confirmación final para eliminar
            print(f"\033[38;5;214mLa información de la base de datos '{db_name}' será eliminada. ¿Está seguro que desea continuar? (Enter para continuar, Esc para salir):\033[0m", end="", flush=True)
            confirm = get_key()
            if confirm == '\x1b':  # Esc key code
                print("\nVolviendo a la selección de bases de datos.")
                continue  # Volver a la selección de bases de datos
            elif confirm == '\r' or confirm == '\n':  # Enter key code
                break  # Proceder con la eliminación
        except (IndexError, ValueError):
            print("Selección inválida.")

# Desactivar las verificaciones de claves foráneas para permitir la eliminación
connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

# Eliminar todas las tablas de la base de datos seleccionada
connection.execute(text(f"USE {db_name};"))
tables = connection.execute(text("SHOW TABLES;")).fetchall()
for table in tables:
    connection.execute(text(f"DROP TABLE IF EXISTS {table[0]};"))
print(f"Todas las tablas de la base de datos '{db_name}' fueron eliminadas.")

# Reactivar las verificaciones de claves foráneas
connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

# Crear la nueva estructura de tabla meli_access
connection.execute(text("""
CREATE TABLE IF NOT EXISTS `meli_access` (
  `app_id` bigint DEFAULT NULL,
  `secret_key` varchar(50) CHARACTER SET armscii8 COLLATE armscii8_bin DEFAULT NULL,
  `refresh_token` varchar(50) COLLATE armscii8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;
"""))
print("Estructura de tabla 'meli_access' creada exitosamente.")
print("\nConfiguración completada.")

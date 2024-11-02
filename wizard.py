import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import sys
import termios
import tty
import subprocess
from getpass import getpass

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Ruta a .env en la estructura del entorno virtual
env_path = "./.env"

# Intentar conectar al servidor de base de datos en un bucle
while True:
    db_user = input("Ingrese el usuario de la base de datos: ")
    db_password = getpass("Ingrese la contraseña de la base de datos: ")
    db_host = input("Ingrese la dirección del host de la base de datos (default: localhost): ") or "localhost"

    # Intentar conectar al servidor de base de datos
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

        # Confirmación con Enter para reintentar, Esc para salir
        while True:
            print("¿Desea intentarlo de nuevo? (Enter para continuar, Esc para cancelar): ", end="", flush=True)
            confirm = get_key()
            if confirm == '\x1b':  # Esc key code
                print("\nInstalación cancelada.")
                exit(0)
            elif confirm == '\r' or confirm == '\n':  # Enter key code
                print("\nReintentando conexión...")
                break
            else:
                print("\nOpción no válida. Presione Esc para cancelar o Enter para continuar.")

# Obtener las bases de datos disponibles
result = connection.execute(text("SHOW DATABASES;"))
databases = [row[0] for row in result if row[0] not in ('mysql', 'performance_schema', 'information_schema')]

# Listar opciones de bases de datos
print("\nSeleccione una opción:")
print("0 - Crear una nueva base de datos")
for i, db_name in enumerate(databases, start=1):
    print(f"{i} - {db_name}")

# Solicitar selección de base de datos o creación de una nueva
while True:
    selection = input("Ingrese el número de la base de datos o 0 para crear una nueva: ")
    if selection == "0":
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
        try:
            db_name = databases[int(selection) - 1]
            print(f"\033[38;5;214m¿Quiere hacer un backup de la base de datos '{db_name}' antes de utilizarla? Recuerde que todo el contenido actual será eliminado. (Enter para hacer backup, Esc para omitir):\033[0m")
            confirm = get_key()
            if confirm == '\x1b':
                print("\nBackup omitido.")
            elif confirm == '\r' or confirm == '\n':
                backup_command = ["mysqldump", "-u", db_user, "-h", db_host, db_name]
                backup_env = os.environ.copy()
                backup_env["MYSQL_PWD"] = db_password
                with open(f"{db_name}_backup.sql", "w") as backup_file:
                    subprocess.run(backup_command, stdout=backup_file, env=backup_env)
                print(f"Backup de la base de datos '{db_name}' guardado como {db_name}_backup.sql.")
            print(f"\033[38;5;214mLa información de la base de datos '{db_name}' será eliminada. ¿Está seguro que desea continuar? (Enter para continuar, Esc para salir):\033[0m")
            confirm = get_key()
            if confirm == '\x1b':
                print("\nInstalación cancelada.")
                exit(0)
            elif confirm == '\r' or confirm == '\n':
                connection.execute(text(f"USE {db_name};"))
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]
                for table in tables:
                    try:
                        connection.execute(text(f"DROP TABLE IF EXISTS {table};"))
                    except OperationalError as e:
                        print(f"Error al eliminar la tabla {table}: {e}")
                # Crear nueva estructura de tablas con 'id' como clave primaria
                connection.execute(text(f"USE {db_name};"))  # Seleccionar la base de datos
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS inicio (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """))
                connection.execute(text("""
                    INSERT INTO inicio (title) VALUES
                    ('Hola, soy una aplicacion de Flask funcional conectada a Mysql');
                """))
                print(f"Base de datos '{db_name}' lista para usarse.")
                break
        except (IndexError, ValueError):
            print("Selección inválida. Intente de nuevo.")

# Guardar credenciales en .env
with open(env_path, "w") as env_file:
    env_file.write(f"DB_USER={db_user}\n")
    env_file.write(f"DB_PASSWORD={db_password}\n")
    env_file.write(f"DB_HOST={db_host}\n")
    env_file.write(f"DB_NAME={db_name}\n")

print(f"Archivo de configuración {env_path} creado con los datos de conexión.")
print(f"\nConfiguración completada. La base de datos '{db_name}' está lista para usarse.")

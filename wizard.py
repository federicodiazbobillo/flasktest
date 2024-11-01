import os
from sqlalchemy import create_engine, text
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
                break  # Volver al inicio del bucle para reingresar usuario y clave
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
            print(f"\033[38;5;214m¿Quiere hacer un backup de la base de datos '{db_name}' antes de utilizarla? Recuerde que todo el contenido actual será eliminado. (Enter para hacer backup, Esc para omitir):\033[0m")
            confirm = get_key()
            if confirm == '\x1b':
                print("\nBackup omitido.")
            elif confirm == '\r' or confirm == '\n':
                os.system(f"mysqldump -u {db_user} -p{db_password} -h {db_host} {db_name} > {db_name}_backup.sql")
                print(f"Backup de la base de datos '{db_name}' guardado como {db_name}_backup.sql.")
            print(f"\033[38;5;214mLa información de la base de datos '{db_name}' será eliminada. ¿Está seguro que desea continuar? (Enter para continuar, Esc para salir):\033[0m")
            confirm = get_key()
            if confirm == '\x1b':
                print("\nInstalación cancelada.")
                exit(0)
            elif confirm == '\r' or confirm == '\n':
                # Eliminar tablas existentes
                connection.execute(text(f"USE {db_name};"))
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]
                for table in tables:
                    try:
                        connection.execute(text(f"DROP TABLE IF EXISTS {table};"))
                    except OperationalError as e:
                        print(f"Error al eliminar la tabla {table}: {e}")
                # Crear nueva estructura de tablas
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS meli_access (
                        app_id BIGINT DEFAULT NULL,
                        secret_key VARCHAR(50) CHARACTER SET armscii8 COLLATE armscii8_bin DEFAULT NULL,
                        refresh_token VARCHAR(50) COLLATE armscii8_bin DEFAULT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;
                """))
                print(f"Base de datos '{db_name}' lista para usarse.")
                break
        except (IndexError, ValueError):
            print("Selección inválida. Intente de nuevo.")

# Guardar la configuración de la base de datos en config.py
with open(config_path, "w") as config_file:
    config_file.write(f"""class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
""")

print(f"Archivo de configuración {config_path} actualizado con los datos de conexión.")
print(f"\nConfiguración completada. La base de datos '{db_name}' está lista para usarse.")

from dejavu import Dejavu

config = {
    "database": {
        "host": "localhost",  # O el nombre de tu contenedor de base de datos si estás usando Docker
        "user": "root",  # El usuario de la base de datos
        "password": "password",  # La contraseña que hayas configurado
        "database": "dejavu",  # El nombre de la base de datos
    },
    "database_type": "mysql",  # Usa 'mysql' si estás usando MySQL
}

djv = Dejavu(config)

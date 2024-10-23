from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pymysql
import bcrypt
import base64

app = Flask(__name__)
CORS(app)

# Función para encriptar la contraseña
def encriptar(palabra):
    return bcrypt.hashpw(palabra.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Función para verificar la contraseña
def verificar_contrasena(contrasena_intentada, contrasena_hash):
    return bcrypt.checkpw(contrasena_intentada.encode('utf-8'), contrasena_hash.encode('utf-8'))

# Función para conectarnos a la base de datos de MySQL
def conectar(vhost, vuser, vpass, vdb):
    return pymysql.connect(host=vhost, user=vuser, passwd=vpass, db=vdb, charset='utf8mb4')

# Variables de conexión
vhost = 'localhost'
vuser = 'root'
vpass = ''
vdb = 'alojoseguro'

# Clientes
@app.route("/general_cliente")
def consulta_general_clientes():
    try:
        conn = conectar(vhost, vuser, vpass, vdb)
        cur = conn.cursor()
        cur.execute("SELECT * FROM cliente")
        datos = cur.fetchall()
        data = []
        for row in datos:
            dato = {'id': row[0], 'nombre': row[1], 'correo': row[2], 'contraseña': row[3]}
            data.append(dato)
        cur.close()
        conn.close()
        return jsonify({'clientes': data, 'mensaje': 'clientes'})
    except Exception as ex:
        print(ex)
    return jsonify({'mensaje': 'Error'})

# Consulta individual
@app.route("/consulta_individual/<id>", methods=['GET'])
def consulta_individual(id):
    try:
        conn = conectar(vhost, vuser, vpass, vdb)
        cur = conn.cursor()
        cur.execute("SELECT * FROM cliente WHERE id = %s", (id,))
        datos = cur.fetchone()
        cur.close()
        conn.close()
        if datos:
            dato = {'id': datos[0], 'nombre': datos[1], 'correo': datos[2], 'contraseña': datos[3]}
            return jsonify({'cliente': dato, 'mensaje': 'Registro encontrado'})
        else:
            return jsonify({'mensaje': 'Registro no encontrado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

# Registro de clientes
@app.route("/registro", methods=['POST'])
def registro():
    try:
        conn = conectar(vhost, vuser, vpass, vdb)
        cur = conn.cursor()
        contraseña_encriptada = encriptar(request.json['contraseña'])
        cur.execute("INSERT INTO cliente (nombre, correo, contraseña) VALUES (%s, %s, %s)",
                    (request.json['nombre'], request.json['correo'], contraseña_encriptada))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Registro agregado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

@app.route("/login", methods=['POST'])
def login():
    try:
        data = request.json
        correo = data.get('email')
        contraseña_intentada = data.get('password')

        conn = conectar(vhost, vuser, vpass, vdb)
        cur = conn.cursor()
        cur.execute("SELECT contraseña FROM cliente WHERE correo = %s", (correo,))
        cliente = cur.fetchone()
        cur.close()
        conn.close()

        if cliente:
            if verificar_contrasena(contraseña_intentada, cliente[0]):
                return jsonify({'success': True, 'message': 'Inicio de sesión exitoso'})
            else:
                return jsonify({'success': False, 'message': 'Contraseña incorrecta'})
        else:
            return jsonify({'success': False, 'message': 'Correo no encontrado'})
    except Exception as ex:
        print(ex)
        return jsonify({'success': False, 'message': 'Error en el inicio de sesión'})

@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar(codigo):
    try:
        conn = conectar(vhost, vuser, vpass, vdb)
        cur = conn.cursor()
        cur.execute("DELETE FROM cliente WHERE id = %s", (codigo,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'eliminado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

@app.route("/actualizar", methods=['PUT'])
def actualizar():
    try:
        data = request.json
        conn = conectar(vhost, vuser, vpass, vdb)
        with conn.cursor() as cur:
            # Encriptar la nueva contraseña usando bcrypt
            salt = bcrypt.gensalt()
            contraseña_encriptada = bcrypt.hashpw(data['contraseña'].encode('utf-8'), salt)

            # Actualizar la contraseña en la base de datos
            cur.execute("UPDATE cliente SET contraseña = %s WHERE correo = %s",
                        (contraseña_encriptada.decode('utf-8'), data['correo']))
            conn.commit()
            
            affected_rows = cur.rowcount

        conn.close()

        if affected_rows > 0:
            return jsonify({'mensaje': 'Registro Actualizado'})
        else:
            return jsonify({'mensaje': 'No se encontró el usuario'})
    except pymysql.Error as e:
        print(f"Error de PyMySQL: {e}")
        return jsonify({'mensaje': 'Error en la base de datos'})
    except Exception as ex:
        print(f"Error general: {ex}")
        return jsonify({'mensaje': 'Error inesperado'})
    
@app.route('/registro_hotel', methods=['POST'])
def registrar_hotel():
    data = request.json
    nombre_hotel = data.get('nombre_hotel')
    ubicacion_ciudad = data.get('ubicacion_ciudad')
    ubicacion_barrio = data.get('ubicacion_barrio')
    direccion = data.get('direccion')
    habitaciones_disponibles = data.get('habitaciones_disponibles')
    tipos_habitaciones = data.get('tipos_habitaciones')
    servicios = data.get('servicios')
    clasificacion_hotel = data.get('clasificacion_hotel')
    telefono = data.get('telefono')  # Nuevo campo: teléfono
    precio = data.get('precio')  # Nuevo campo: precio
    imagen_base64 = data.get('imagen')

    # Configuración de la conexión a la base de datos
    db_config = {
        'host': vhost,
        'user': vuser,
        'password': vpass,
        'database': vdb
    }

    try:
        # Conectar a la base de datos
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO hoteles 
                (nombre_hotel, ubicacion_ciudad, ubicacion_barrio, direccion, habitaciones_disponibles, tipos_habitaciones, fotos, servicios, clasificacion_hotel, telefono, precio) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                nombre_hotel,
                ubicacion_ciudad,
                ubicacion_barrio,
                direccion,
                habitaciones_disponibles,
                tipos_habitaciones,
                base64.b64decode(imagen_base64),
                servicios,
                clasificacion_hotel,
                telefono,  # Inserta el valor de teléfono
                precio  # Inserta el valor de precio
            ))
            connection.commit()

        return jsonify({'mensaje': 'Hotel agregado correctamente'})
    except Exception as e:
        print(f"Error al registrar el hotel: {e}")
        return jsonify({'mensaje': 'Error al registrar el hotel'}), 500
    finally:
        if 'connection' in locals():
            connection.close()
            
# Ruta para consultar todos los hoteles
@app.route("/general_hoteles", methods=['GET'])
def consultar_hoteles():
    try:
        conn = conectar(vhost, vuser, vpass, vdb)
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = "SELECT * FROM hoteles"
            cur.execute(sql)
            hoteles = cur.fetchall()

            # Convertir las imágenes a Base64
            for hotel in hoteles:
                if hotel['fotos']:
                    hotel['fotos'] = base64.b64encode(hotel['fotos']).decode('utf-8')
                else:
                    hotel['fotos'] = None  # Asegúrate de que no haya error si no hay fotos

        return jsonify({'hoteles': hoteles}), 200
    except Exception as ex:
        print("Error al consultar hoteles:", ex)
        return jsonify({'mensaje': 'Error al consultar los hoteles'}), 500
    finally:
        conn.close()


@app.route("/eliminar_hotel/<id_hotel>", methods=['DELETE'])
def eliminar_hotel(id_hotel):
    try:
        conn = conectar(vhost, vuser, vpass, vdb)
        cur = conn.cursor()
        cur.execute("DELETE FROM hoteles WHERE id_hotel = %s", (id_hotel,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'eliminado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# Actualizar hotel
@app.route("/actualizar_hotel", methods=['PUT'])
def actualizar_hotel():
    data = request.get_json()
    try:
        conn = conectar(vhost, vuser, vpass, vdb)
        with conn.cursor() as cur:
            sql = """
                UPDATE hoteles SET nombre_hotel = %s, ubicacion_ciudad = %s, ubicacion_barrio = %s,
                direccion = %s, habitaciones_disponibles = %s, tipos_habitaciones = %s, 
                fotos = %s, servicios = %s, clasificacion_hotel = %s, calificacion_cliente_a_hotel = %s
                WHERE id = %s
            """
            cur.execute(sql, (
                data['nombre_hotel'], data['ubicacion_ciudad'], data['ubicacion_barrio'],
                data['direccion'], data['habitaciones_disponibles'], data['tipos_habitaciones'],
                data['fotos'], data['servicios'], data['clasificacion_hotel'],
                data['calificacion_cliente_a_hotel'], data['id']
            ))
            conn.commit()
        return jsonify({'mensaje': 'Hotel actualizado correctamente'}), 200
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error al actualizar el hotel'}), 500
    finally:
        conn.close()

@app.route('/reservar_hotel', methods=['POST'])
def reservar_hotel():
    data = request.get_json()
    nombre_hotel = data.get('nombre_hotel')
    
    if not nombre_hotel:
        return jsonify({'success': False, 'mensaje': 'Hotel no especificado'}), 400

    try:
        connection = pymysql.connect(
            host=vhost,
            user=vuser,
            password=vpass,
            database=vdb,
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Actualizar habitaciones disponibles restando 1
            cursor.execute("UPDATE hoteles SET habitaciones_disponibles = habitaciones_disponibles - 1 WHERE nombre_hotel = %s AND habitaciones_disponibles > 0", (nombre_hotel,))
            affected_rows = cursor.rowcount
            
            if affected_rows > 0:
                connection.commit()
                return jsonify({'success': True}), 200
            else:
                return jsonify({'success': False, 'mensaje': 'No hay habitaciones disponibles o el hotel no fue encontrado.'}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'mensaje': 'Error al procesar la reserva'}), 500

    finally:
        connection.close()

# Render templates
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route('/valledupar')
def valledupar():
    return render_template('valledupar.html')

@app.route('/barranquilla')
def barranquilla():
    return render_template('barranquilla.html')

@app.route('/cartagena')
def cartagena():
    return render_template('cartagena.html')

@app.route('/santamarta')
def santamarta():
    return render_template('santamarta.html')

@app.route('/vermas')
def vermas():
    return render_template('vermas.html')

@app.route('/registro')
def registro_view():
    return render_template('registro.html')

@app.route('/ingreso_h')
def ingreso_hoteles():
    return render_template('ingreso_hoteles.html')

if __name__ == '__main__':
    app.run(debug=True)

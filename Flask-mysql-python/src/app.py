from flask import Flask, jsonify, make_response, render_template, request, redirect, send_from_directory, url_for
from flask_swagger_ui import get_swaggerui_blueprint
from flask_swagger import swagger
import random
import requests
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType

import requests
import os 
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder= template_dir)

#AL INICIAR VA DIRECTAMENTE A SWAGGER DOCS
@app.before_request
def redirect_to_docs():
    if request.path == '/':
        return redirect(url_for('swagger_docs'))

#CRUD
@app.route('/')
def Index():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM producto")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columNames, record)))
    cursor.close()
    return render_template('index.html', data = insertObject)
@app.route('/user', methods=['POST'])
def addUser():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    categoria = request.form['categoria']
    precio = request.form['precio']
    stock = request.form['stock']
    
    if nombre and descripcion and categoria and precio and stock:
        cursor = db.database.cursor()
        sql = "INSERT INTO producto (nombre,descripcion,categoria,precio,stock) VALUES (%s, %s, %s , %s, %s)"
        data = (nombre,descripcion,categoria,precio, stock)
        cursor.execute(sql, data)
        db.database.commit()
    return redirect(url_for('Index'))
@app.route('/delete/<string:id>')
def delete (id):
    cursor = db.database.cursor()
    sql = "DELETE FROM producto WHERE id=%s"
    data = (id,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('Index'))
@app.route('/edit/<string:id>',methods=['POST'])
def edit(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    categoria = request.form['categoria']
    precio = request.form['precio']
    stock = request.form['stock']
    
    if nombre and descripcion and categoria and precio and stock:
        cursor = db.database.cursor()
        sql = "UPDATE producto SET nombre = %s,descripcion = %s,categoria = %s,precio = %s, stock = %s WHERE id = %s"
        data = (nombre,descripcion,categoria,precio,stock, id)
        cursor.execute(sql, data)
        db.database.commit()
    return redirect(url_for('Index'))
    
#API PRODUCTOS

# GET TODOS LOS PRODUCTOS
@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM producto")
    myresult = cursor.fetchall()
    #Convertir los datos a lista de diccionarios
    result = []
    columNames = [column[0] for column in cursor.description]
    for record in myresult:
        result.append(dict(zip(columNames, record)))
    cursor.close()
    return jsonify(result)

# POST UN PRODUCTO
@app.route('/api/productos', methods=['POST'])
def create_producto():
    nombre = request.json['nombre']
    descripcion = request.json['descripcion']
    categoria = request.json['categoria']
    precio = request.json['precio']
    stock = request.json['stock']
    cursor = db.database.cursor()
    sql = "INSERT INTO producto (nombre, descripcion, categoria, precio, stock) VALUES (%s, %s, %s, %s, %s)"
    data = (nombre, descripcion, categoria, precio, stock)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()
    return make_response(jsonify({'message': 'Producto creado exitosamente'}), 201)

# GET PRODUCTO ESPECIFICO
@app.route('/api/productos/<int:id>', methods=['GET'])
def get_producto(id):
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM producto WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    if producto is not None:
        return jsonify(producto)
    else:
        return make_response(jsonify({'error': 'Producto no encontrado'}), 404)

# PUT ACTUALIZAR UN PRODUCTO
@app.route('/api/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    nombre = request.json['nombre']
    descripcion = request.json['descripcion']
    categoria = request.json['categoria']
    precio = request.json['precio']
    stock = request.json['stock']
    cursor = db.database.cursor()
    sql = "UPDATE producto SET nombre=%s, descripcion=%s, categoria=%s, precio=%s, stock=%s WHERE id=%s"
    data = (nombre, descripcion, categoria, precio, stock, id)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()
    return make_response(jsonify({'message': 'Producto actualizado exitosamente'}), 200)

# ELIMINAR UN PRODUCTO
@app.route('/api/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    cursor = db.database.cursor()
    # Eliminar los registros de la tabla pedido_productos
    cursor.execute("DELETE FROM pedido_productos WHERE producto_id = %s", (id,))
    cursor.execute("DELETE FROM producto WHERE id = %s", (id,))
    db.database.commit()
    cursor.close()
    return make_response(jsonify({'message': 'Producto eliminado exitosamente'}), 200)
cursor = db.database.cursor()
  
#API PEDIDOS

# GET TODOS PEDIDOS
@app.route('/api/pedidos', methods=['GET'])
def obtener_pedidos():
    cursor = db.database.cursor()
    cursor.execute("SELECT p.id AS pedido_id, c.rut AS cliente_rut, p.fecha_pedido, pp.producto_id, pr.nombre AS producto_nombre, pp.cantidad \
                    FROM pedidos p \
                    JOIN clientes c ON p.rut_cliente = c.rut  \
                    JOIN pedido_productos pp ON p.id = pp.pedido_id \
                    JOIN producto pr ON pp.producto_id = pr.id")
    result = cursor.fetchall()
    cursor.close()
    
    #Convertir los datos a lista de diccionarios
    pedidos = []
    for row in result:
        pedido_id = row[0]
        cliente_rut = row[1]
        fecha = row[2]
        producto_id = row[3]
        producto_nombre = row[4]
        cantidad = row[5]
        
        # Buscar si el pedido ya existe en la lista
        pedido_existente = next((pedido for pedido in pedidos if pedido['id'] == pedido_id), None)
        
        if pedido_existente:
            # Agregar el producto y su cantidad al pedido existente
            pedido_existente['productos'].append({
                
                'id': producto_id,
                'nombre': producto_nombre,
                'cantidad': cantidad
            })
        else:
            # Crear un nuevo pedido con el producto y su cantidad
            pedido = {
                'id': pedido_id,
                'rut_cliente': cliente_rut,
                'fecha_pedido': fecha,
                'productos': [{
                    'id': producto_id,
                    'nombre': producto_nombre,
                    'cantidad': cantidad
                }]
            }
            pedidos.append(pedido)
    
    return jsonify(pedidos)

# POST PEDIDOS
@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    # Obtener los datos del pedido del cuerpo de la solicitud JSON
    data = request.json
    rut_cliente = data['rut_cliente']
    fecha_pedido = data['fecha_pedido']
    productos = data['productos']

    # Insertar el pedido en la tabla de pedidos
    cursor = db.database.cursor()
    sql = "INSERT INTO pedidos (rut_cliente, fecha_pedido) VALUES (%s, %s)"
    cursor.execute(sql, (rut_cliente, fecha_pedido))
    db.database.commit()

    # Obtener el ID del pedido recién insertado
    pedido_id = cursor.lastrowid

    # Insertar los productos del pedido en la tabla de pedido_productos
    for producto in productos:
        producto_id = producto['producto_id']
        cantidad = producto['cantidad']
        sql = "INSERT INTO pedido_productos (pedido_id, producto_id, cantidad) VALUES (%s, %s, %s)"
        cursor.execute(sql, (pedido_id, producto_id, cantidad))
        db.database.commit()

    cursor.close()

    return jsonify({'message': 'Pedido creado exitosamente'}), 201

# GET ESPECIFICO PEDIDOS
@app.route('/api/pedidos/<int:pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    cursor = db.database.cursor()
    cursor.execute("SELECT p.id AS pedido_id, c.rut AS cliente_rut, p.fecha_pedido, pp.producto_id, pr.nombre AS producto_nombre, pp.cantidad \
                    FROM pedidos p \
                    JOIN clientes c ON p.rut_cliente = c.rut  \
                    JOIN pedido_productos pp ON p.id = pp.pedido_id \
                    JOIN producto pr ON pp.producto_id = pr.id \
                    WHERE p.id = %s", (pedido_id,))
    result = cursor.fetchall()
    cursor.close()  

    # Verificar si se encontró el pedido
    if len(result) == 0:
        return make_response(jsonify({'error': 'Pedido no encontrado'}), 404)

    # Construir la respuesta
    pedido = {
        'id': result[0][0],
        'rut_cliente': result[0][1],
        'fecha_pedido': result[0][2],
        'productos': []
    }

    for row in result:
        producto_id = row[3]
        producto_nombre = row[4]
        cantidad = row[5]

        pedido['productos'].append({
            'id': producto_id,
            'nombre': producto_nombre,
            'cantidad': cantidad
        })

    return jsonify(pedido)

# PUT PEDIDO EDITAR
@app.route('/api/pedidos/<int:id>', methods=['PUT'])
def update_pedido(id):
    # Obtener los datos del pedido a partir de la solicitud
    datos_pedido = request.json
    
    # Extraer los campos necesarios del pedido
    rut_cliente = datos_pedido['rut_cliente']
    fecha_pedido = datos_pedido['fecha_pedido']
    productos = datos_pedido['productos']
    
    # Realizar la actualización del pedido en la base de datos
    cursor = db.database.cursor()
    sql_pedido = "UPDATE pedidos SET rut_cliente=%s, fecha_pedido=%s WHERE id=%s"
    data_pedido = (rut_cliente, fecha_pedido, id)
    cursor.execute(sql_pedido, data_pedido)
    
    # Eliminar los productos asociados al pedido en la tabla pedido_productos
    sql_delete_productos = "DELETE FROM pedido_productos WHERE pedido_id=%s"
    cursor.execute(sql_delete_productos, (id,))
    
    # Insertar los nuevos productos asociados al pedido en la tabla pedido_productos
    sql_insert_productos = "INSERT INTO pedido_productos (pedido_id, producto_id, cantidad) VALUES (%s, %s, %s)"
    for producto in productos:
        producto_id = producto['producto_id']
        cantidad = producto['cantidad']
        cursor.execute(sql_insert_productos, (id, producto_id, cantidad))
    
    db.database.commit()
    cursor.close()
    
    return make_response(jsonify({'message': 'Pedido actualizado exitosamente'}), 200)

# DELETE PEDIDO
@app.route('/api/pedidos/<int:id>', methods=['DELETE'])
def delete_pedido(id):
    cursor = db.database.cursor()

    # Eliminar los registros de la tabla pedido_productos relacionados con el pedido
    cursor.execute("DELETE FROM pedido_productos WHERE pedido_id = %s", (id,))
    
    # Eliminar el registro del pedido en la tabla pedidos
    cursor.execute("DELETE FROM pedidos WHERE id = %s", (id,))

    db.database.commit()
    cursor.close()
    return make_response(jsonify({'message': 'Pedido eliminado exitosamente'}), 200)

# SWAGGER

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API Documentation"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/api/docs/')
def swagger_docs():
    return send_from_directory('static', 'swagger-ui.html')



@app.route('/crear_transaccion', methods=['POST'])
def crear_transaccion():
    buy_order = request.form.get('buy_order')
    session_id = request.form.get('session_id')
    amount = request.form.get('amount')
    return_url = request.form.get('return_url')
    
    tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
    resp = tx.create(buy_order, session_id, amount, return_url)
    
    print(resp)
    resp['url']
    resp['token']
    
    return redirect(resp['url'])
@app.route('/formulario_pago', methods=['GET'])
def formulario_pago():
    return render_template('formulario_pago.html')


# Ruta para confirmar la transacción y procesar la respuesta
@app.route('/confirmar_pago', methods=['POST'])
def confirmar_pago():
    # Obtener el token de transacción de la solicitud
    token = request.form.get('token_ws')

    # Confirmar la transacción utilizando el token
    tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
    resp = tx.commit(token)

    # Procesar la respuesta de confirmación
    if resp['status'] == 'AUTHORIZED':
        # La transacción se confirmó correctamente
        return render_template('pago_exitoso.html')
    else:
        # La transacción no pudo ser confirmada
        return render_template('pago_error.html')
    
if __name__ == '__main__':  
    app.run(port = 4000, debug=True)
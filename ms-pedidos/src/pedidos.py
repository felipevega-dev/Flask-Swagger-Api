from flask import Flask, jsonify, make_response, redirect, render_template, request, send_from_directory, url_for
from flask_swagger_ui import get_swaggerui_blueprint
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

#API PEDIDOS

# GET TODOS PEDIDOS
@app.route('/api/pedidos', methods=['GET'])
def obtener_pedidos():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)

    # Calcular los índices de inicio y fin para la paginación
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    cursor = db.database.cursor()
    cursor.execute("SELECT p.id AS pedido_id, c.rut AS cliente_rut, p.fecha_pedido, pp.producto_id, pr.nombre AS producto_nombre, pp.cantidad \
                    FROM pedidos p \
                    JOIN clientes c ON p.rut_cliente = c.rut  \
                    JOIN pedido_productos pp ON p.id = pp.pedido_id \
                    JOIN producto pr ON pp.producto_id = pr.id \
                    ORDER BY p.id ASC")
    result = cursor.fetchall()
    cursor.close()

    # Obtener los pedidos paginados
    paginated_pedidos = result[start_index:end_index]

    # Convertir los datos a una lista de diccionarios
    pedidos = []
    for row in paginated_pedidos:
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

    # Crear la respuesta paginada
    response = {
        "page": page,
        "page_size": page_size,
        "total_count": len(result),
        "pedidos": pedidos
    }

    return jsonify(response), 200


# POST PEDIDOS
@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    # Obtener los datos del pedido del cuerpo de la solicitud JSON
    data = request.json
    rut_cliente = data['rut_cliente']
    fecha_pedido = data['fecha_pedido']
    productos = data['productos']

    cursor = db.database.cursor()
    try:
        # Verificar el stock de los productos antes de realizar el pedido
        for producto in productos:
            producto_id = producto['producto_id']
            cantidad = producto['cantidad']
            
            # Obtener el stock disponible del producto
            cursor.execute("SELECT stock FROM producto WHERE id = %s", (producto_id,))
            stock_disponible = cursor.fetchone()[0]

            if cantidad > stock_disponible:
                # Si la cantidad solicitada es mayor al stock disponible, retornar un error
                return jsonify({'error': 'No hay suficiente stock para el producto con ID {}'.format(producto_id)}), 400

        # Insertar el pedido en la tabla de pedidos
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

        return jsonify({'message': 'Pedido creado exitosamente'}), 201

    except Exception as e:
        # En caso de cualquier error, hacer rollback de la transacción
        db.database.rollback()
        return jsonify({'error': 'Error al crear el pedido: {}'.format(str(e))}), 500

    finally:
        cursor.close()
        
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

if __name__ == '__main__':  
    app.run(port = 4001, debug=True)
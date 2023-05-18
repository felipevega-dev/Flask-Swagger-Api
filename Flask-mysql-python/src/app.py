from flask import Flask, jsonify, make_response, render_template, request, redirect, url_for
import os 
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder= template_dir)

#RUTAS DE LA APP

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
    cursor.execute("DELETE FROM producto WHERE id = %s", (id,))
    db.database.commit()
    cursor.close()
    return make_response(jsonify({'message': 'Producto eliminado exitosamente'}), 200)
    
    
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


if __name__ == '__main__':  
    app.run(port = 4000, debug=True)

# stock
# armar json
# validar stock en productos
# guardar en tabla de pedidos

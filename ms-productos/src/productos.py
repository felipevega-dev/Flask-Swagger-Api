from flask import Flask, jsonify, make_response, redirect, render_template, request, send_from_directory, url_for
from flask_swagger_ui import get_swaggerui_blueprint
import os 
import database as db


template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder= template_dir)

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
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)

    # Calcular los índices de inicio y fin para la paginación
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # Obtener la lista de productos en stock con stock mayor o igual a 1
    cursor = db.database.cursor()
    sql = "SELECT id, nombre, descripcion, categoria, precio, stock FROM producto WHERE stock >= 1 ORDER BY id ASC"
    cursor.execute(sql)
    productos = cursor.fetchall()

    # Aplicar la paginación
    paginated_products = productos[start_index:end_index]

    # Obtener el número total de productos en stock
    total_count = len(productos)

    cursor.close()

    # Crear la respuesta paginada con nombres de los valores
    response = {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "productos": [
            {
                "id": producto[0],
                "nombre": producto[1],
                "descripcion": producto[2],
                "categoria": producto[3],
                "precio": producto[4],
                "stock": producto[5]
            }
            for producto in paginated_products
        ]
    }

    return jsonify(response), 200

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
    app.run(port = 4000, debug=True)
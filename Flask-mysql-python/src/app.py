from flask import Flask, render_template, request, redirect, url_for
import os 
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder= template_dir)

#RUTAS DE LA APP

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

#Ruta para guardar usuarios en la bd
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
    
    
    
if __name__ == '__main__':
    app.run(port = 4000, debug=True)
    

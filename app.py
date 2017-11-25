from flask import Flask, render_template, redirect, url_for, flash, request, session, logging
from data import Materiales
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators
from functools import wraps
app = Flask(__name__)
#MySQL STUFF---------------------------------------------------------
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='sergio1234'
app.config['MYSQL_DB']='odc'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql = MySQL(app)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        userpass = request.form['userpass']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM usuarios WHERE usuario = %s and pass= %s", (username, userpass))
        if result > 0:
            data = cur.fetchall()
            app.logger.info('PASSWORD MATCHED')
            session['logged_in']=True
            session['username']=username
            return redirect(url_for('index'))

        else:
            error = "Usuario o pass no coinciden"
            return render_template('login.html', error = error)
        cur.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return(*args, *kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def index():
    return render_template('index.html')
#MATERIALES STUFF------------------------------------------------
@app.route('/materiales')
def materiales():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM proyecto_app_material")
    mater = cur.fetchall()
    if result > 0:
        return render_template('materiales.html', mater=mater)
    else:
        msg = 'NO hay ningun material'
        return render_template('materiales.html', msg=msg)
    cur.close()


@app.route('/material/edit/<string:id>', methods = ['GET', 'POST'])
@is_logged_in
def materialedit(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM proyecto_app_material WHERE id = %s", [id])
    mater = cur.fetchone()

    form = AddMaterial(request.form)
    form.nombre.data = mater['nombre']
    form.unidad.data = mater['unidad']
    form.precio.data = mater['precio']

    if request.method == 'POST' and form.validate():
        nombre = request.form['nombre']
        unidad = request.form['unidad']
        precio = request.form['precio']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE proyecto_app_material SET nombre = %s, unidad= %s, precio=%s WHERE id=%s", (nombre, unidad, precio, id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('materiales'))
    return render_template('materialedit.html', form=form)


class AddMaterial(Form):
    nombre = StringField(u'Nombre del material')
    unidad = StringField(u'Nombre de la unidad')
    precio = StringField(u'Precio')

@app.route('/material/new/', methods = ['GET', 'POST'])
@is_logged_in
def materialadd():
    form = AddMaterial(request.form)
    if request.method == 'POST' and form.validate():
        nombre = form.nombre.data
        unidad = form.unidad.data
        precio = form.precio.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO proyecto_app_material (nombre, unidad, precio) VALUES (%s, %s, %s)", (nombre, unidad, precio))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('materiales'))
    return render_template('materialadd.html', form=form)

@app.route('/material/delete/<string:id>', methods = ['GET', 'POST'])
@is_logged_in
def materialdelete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM material WHERE id=%s", (id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('materiales'))


#ORDENES STUFF-----------------------------------------------------
@app.route('/ordenes')
def ordenes():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM proyecto_app_encabezado")
    mater = cur.fetchall()
    if result > 0:
        return render_template('ordenes.html', ordenes=mater)
    else:
        msg = 'NO hay ningun material'
        return render_template('ordenes.html', msg=msg)
    cur.close()
class AddOrden(Form):
    encargado = StringField(u'Encargado')
    fecha = StringField(u'Fecha')


@app.route('/orden/new/', methods = ['GET', 'POST'])
@is_logged_in
def ordenadd():
    form = AddOrden(request.form)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM proyecto_app_material")
    mater = cur.fetchall()
    if request.method == 'POST' and form.validate():
        encargado = form.encargado.data
        fecha = form.fecha.data
        materiales = request.form['materiales']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO proyecto_app_encabezado (encargado, fecha) VALUES (%s, %s)", (encargado, fecha))
        mysql.connection.commit()
        cur.close()



        for mat in materiales:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO proyecto_app_descripcion (encabezado_id, material_id) VALUES (%s, %s)", (1, mat))
            mysql.connection.commit()
            cur.close()

        return redirect(url_for('ordenes'))
    return render_template('ordenadd.html', form=form, mater=mater)


if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)

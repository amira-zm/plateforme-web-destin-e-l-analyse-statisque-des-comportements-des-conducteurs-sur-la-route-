from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
import pandas as pd
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from pyroutelib3 import Router
import folium
from datetime import time

app = Flask(__name__)

app.config['MYSQL_HOST'] = '51.77.149.46'
app.config['MYSQL_USER'] = 'djagora'
app.config['MYSQL_PASSWORD'] = 'djagora123@student'
app.config['MYSQL_DB'] = 'djagora_student1'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('To access to your dashboard, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


def generate_id(c):
    idii = 0
    if (c == "2"):
        idii = 1
    elif (c == "20"):
        idii = 2
    elif (c == "10000002"):
        idii = 3
    elif (c == "2020202"):
        idii = 5
    elif (c == "3"):
        idii = 4
    elif (c == "4"):
        idii = 6
    elif (c == "1"):
        idii = 7
    elif (c == "10"):
        idii = 8
    elif (c == "1010101"):
        idii = 9
    elif (c == "10000001"):
        idii = 10
    elif (c == "11067773"):
        idii = 11
    return idii


def map_generate(idn, n):
    ch = "C:\\Users\\AMIRA\\Desktop\\driveandwin - Copie\\user" + str(idn) + "\\trip" + str(n) + ".csv"
    data = pd.read_csv(ch)
    att = data['altitude'].tolist()
    latt = data['longitude'].tolist()
    tup = []
    print(len(att))
    for i in range(len(att)):
        t = (att[i], latt[i])
        tup.append(t)

    router = Router("car")  # on cherche à construire un parcours pour : car, cycle, foot, horse, tram, train
    icone = "car"  # choix de l'icone des marqueurs
    ##on identifie les points de départ et d'arrivée
    point_depart = (att[0], latt[0])
    point_arrivee = (att[-1], latt[-1])
    depart = router.findNode(point_depart[0], point_depart[1])
    arrivee = router.findNode(point_arrivee[0], point_arrivee[1])

    routeLatLons = tup
    ##calcul des distances cumulées
    L = len(routeLatLons)  # taille de la liste = nombre de points
    d = []  # initialisation de la distance : liste vide
    d_cum = []  # initialisation de la distance cumulée: liste vide
    for i in range(1, L):
        d.append(router.distance(routeLatLons[i - 1], routeLatLons[i]))  # liste des distances entre deux points
        d_cum.append(sum(d))  # liste des distances cumulées
    distance = round(d_cum[-1], 2)  # écriture arrondie à deux chiffres après la virgule
    # routeLatLons est un tuple qui stocke les latitudes et les longitudes
    # routeLatLons[0] est la liste des latitudes
    # routeLatLons[1] est la liste des longitudes
    ##initialisation de la carte et choix de l'échelle
    ##on marque certains points
    pas = 10
    for i in range(1, L, pas):  # on positionne des marqueurs tous les ...pas... points
        c = folium.Map(location=[(point_depart[0] + point_arrivee[0]) / 2, (point_depart[1] + point_arrivee[1]) / 2],
                       zoom_start=13)  # carte centrée sur le milieu du segment [depart ; arrivee]
        # folium.Circle(routeLatLons[i], radius=2,
        # popup="point n°" + str(i) + " : " + str(round(d_cum[i], 2)) + "km").add_to(c)

    # on marque le départ
    folium.Marker(routeLatLons[0], popup="Départ", icon=folium.Icon(icon=icone, prefix="fa", color="green")).add_to(c)
    # on marque l'arrivée
    folium.Marker(routeLatLons[-1], popup="Arrivée après " + str(distance) + " km",
                  icon=folium.Icon(icon=icone, prefix="fa", color="red")).add_to(c)
    ##on trace la route

    folium.PolyLine(routeLatLons, color="red", weight=2.5, opacity=1).add_to(
        c)  # on trace la route en une ##carte sauvegardée
    c.save('templates\maRoute' + str(idn) + str(n) + '.html')
    return (n)


# Register Form Class
class RegisterForm(Form):
    CIN = StringField('', [validators.Length(min=8, max=8)], render_kw={"placeholder": "CIN"})
    name = StringField('', [validators.Length(min=1, max=50)], render_kw={"placeholder": "Name"})
    address = StringField('', [validators.Length(min=1, max=50)], render_kw={"placeholder": "address"})
    email = StringField('', [validators.Length(min=6, max=50)], render_kw={"placeholder": "Email"})
    username = StringField('', [validators.Length(min=4, max=25)], render_kw={"placeholder": "Username"})

    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ], render_kw={"placeholder": "Password"})
    confirm = PasswordField('', render_kw={"placeholder": "Confirm Password"})
    permis = StringField('', [validators.Length(min=1, max=50)], render_kw={"placeholder": "permis"})


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        CIN = request.form['CIN']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username

        result = cur.execute("SELECT * FROM users WHERE CIN = %s", [CIN])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if (password_candidate == password):
                # Passed
                session['logged_in'] = True
                session['CIN'] = CIN
                flash('You are now logged in', 'success')
                return redirect(url_for('table', id=generate_id(session['CIN'])))
            else:
                error = 'Invalid login'
                return render_template('includes/login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'CIN not found'
            return render_template('includes/login.html', error=error)

    return render_template('includes/login.html')





@app.route('/table/<string:id>/')
@is_logged_in
def table(id):
    id = generate_id(session['CIN'])
    # Create cursor
    cur1 = mysql.connection.cursor()

    # Get article
    result = cur1.execute("SELECT * FROM trip_table WHERE CIN = %s", [id])

    trips = cur1.fetchall()
    print(trips)

    cur1.close()

    return render_template('includes/table.html', trips=trips, idi=id, map_generate=map_generate)


@app.route('/line/user/<idn>/<n>')
@is_logged_in
def line(idn, n):
    idn = generate_id(session['CIN'])
    ch = "C:\\Users\\AMIRA\\Desktop\\driveandwin - Copie\\user" + str(idn) + "\\trip" + n + ".csv"
    data = pd.read_csv(ch)
    label = data['time'].tolist()
    value = data['Speed'].tolist()
    etat1 = data['TargetValue'].tolist()
    etat=etat1[0]

    values = []
    labels = []
    for i in range(0, len(value), 4):
        values.append(value[i])
        labels.append(label[i])

    colors = [
        "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
        "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
        "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
    line_labels = labels
    line_values = values
    return render_template('line_chart.html', title='Bitcoin Monthly Price in USD', max=130, labels=line_labels,
                           values=line_values,etat=etat)


@app.route('/map/user/<idn>/<n>')
@is_logged_in
def map(idn, n):
    s = 'maRoute' + idn + n + '.html'
    return render_template(s)


@app.route('/user')
def user():
    id = generate_id(session['CIN'])
    cur4 = mysql.connection.cursor()

    # Get article
    result = cur4.execute("SELECT * FROM users WHERE CIN = %s", [session['CIN']])

    users = cur4.fetchall()
    print(users)

    cur4.close()
    return render_template('includes/user.html', users=users, id=id)


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        CIN = form.CIN.data
        name = form.name.data
        address = form.address.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        permis = form.permis.data
        # Create cursor
        cur3 = mysql.connection.cursor()

        # Execute query
        cur3.execute(
            "INSERT INTO users (`CIN`, `name`, `address`, `email`, `username`, `password`, `permis`) VALUES(%s, %s, %s,%s, %s, %s, %s)",
            (CIN, name, address, email, username, password, permis))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur3.close()

        flash('You are now registered and you can log In', 'success')

        return redirect(url_for('trip_table'))
    return render_template('includes/register.html', form=form)
# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host="localhost", port=5000, debug=True)

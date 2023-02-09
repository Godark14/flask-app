from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'

DB_HOST = "localhost"
DB_NAME = "cdb"
DB_USER = "postgres"
DB_PASS = "GodWIN200?"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)



@app.route('/')
def home():
    # Vérifier si l’utilisateur est connecté
    if 'loggedin' in session:
        # L’utilisateur est connecté pour leur montrer la page d’accueil
        return render_template('home.html', username=session['username'])
    # L’utilisateur n’est pas connecté rediriger vers la page de connexion
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Vérifiez si des requêtes POST «nom d’utilisateur» et «mot de passe» existent (formulaire soumis par l’utilisateur)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Vérifier si le compte existe à l’aide de MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Récupérer un enregistrement et renvoyer le résultat
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # Si le compte existe dans la table des utilisateurs dans notre base de données
            if check_password_hash(password_rs, password):
                # Créer des données de session, nous pouvons accéder à ces données dans d’autres routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Rediriger vers la page d’accueil
                return redirect(url_for('home'))
            else:
                # Le compte n’existe pas ou le nom d’utilisateur/mot de passe est incorrect
                flash('Incorrect username/password')
        else:
            # Le compte n’existe pas ou le nom d’utilisateur/mot de passe est incorrect
            flash('Incorrect username/password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Vérifiez s’il existe des demandes POST «nom d’utilisateur», «mot de passe» et «email» (formulaire soumis par l’utilisateur)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        #Créer des variables pour un accès facile
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        # Vérifier si le compte existe à l’aide de MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # Si le compte existe, afficher les contrôles d’erreur et de validation
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Le compte n’existe pas et les données du formulaire sont valides, insérez maintenant un nouveau compte dans la table des utilisateurs
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                           (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Le formulaire est vide... (pas de données POST)
        flash('Please fill out the form!')
    # Afficher le formulaire d’inscription avec message (le cas échéant)
    return render_template('register.html')


@app.route('/logout')
def logout():
    # Supprimez les données de session, cela déconnectera l’utilisateur
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Rediriger vers la page de connexion
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Vérifier si l’utilisateur est connecté
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Afficher la page de profil avec les informations du compte
        return render_template('profile.html', account=account)
    # L’utilisateur n’est pas connecté rediriger vers la page de connexion
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
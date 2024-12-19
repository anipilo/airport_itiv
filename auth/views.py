from flask import Blueprint, redirect, request, render_template, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import smtplib
import random
import string

from database import DatabaseManager as db


auth_blueprint = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@auth_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    current_user_id = session.get('current_user')
    if current_user_id:
        return redirect(url_for('airport.profile') + '?sort=0')

    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        print(password)

        user = db.one(
            f"""SELECT * FROM users WHERE login = '{login}';"""
        )
        error_text = None
        if not user:
            error_text=f'Пользователь "{login}" не существует.'
        else:
            if not check_password_hash(user[3], password):
                error_text='Неправильный пароль.'

        if error_text:
            return render_template(
                'login.html',
                error_text=error_text,
                login=login
            )
        session['current_user'] = user[0]
        if not user[4]:
            session['current_user_admin'] = True
        return redirect(url_for('airport.profile') + '?sort=0')
    return render_template('login.html')


@auth_blueprint.route('/logout/', methods=['GET'])
def logout():
    session['current_user'] = None
    session['current_user_admin'] = False
    return redirect(url_for('auth.login'))


@auth_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    current_user_id = session.get('current_user')
    if current_user_id:
        return redirect(url_for('airport.profile') + '?sort=0')

    if request.method == 'POST':
        login = request.form.get('login')
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.one(
            f"""SELECT * FROM users WHERE login = '{login}';"""
        )
        if user:
            return render_template(
                'register.html',
                error_text=f'Пользователь "{login}" уже существует.',
                login=login
            )

        user_id = db.one(
            f"""INSERT INTO users (login, password, email) VALUES (
            '{login}', '{generate_password_hash(password)}', '{email}');
            SELECT id FROM users WHERE login = '{login}';"""
        )

        db.execute(
            f"""INSERT INTO company_infos (user_id) VALUES ({user_id[0]});"""
        )
        return redirect(url_for('auth.login'))
    else:
        return render_template('register.html')


@auth_blueprint.route('/money/add/', methods=['POST'])
def money_add():
    money = request.form.get('sum')
    if money:
        money = int(money)
    else:
        money = 0
    user_id = session.get('current_user')
    
    ci = db.one(
        f"""SELECT * FROM company_infos WHERE user_id = {user_id};"""
    )
    new_money = ci[4] + money
    db.execute(
        f"""UPDATE company_infos SET money = {new_money} WHERE user_id = {user_id};"""
    )
    return jsonify()


@auth_blueprint.route('/password/reset/', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        new_password = ''.join([random.choice(string.ascii_lowercase) for _ in range(8)])
        user_login = request.form.get('login')

        user = db.one(f"SELECT * FROM users WHERE login = '{user_login}';")
        if not user:
            return render_template('password_reset.html', login=user_login, error_text=f'Пользователь не существует.')
        db.execute(f"UPDATE users SET password = '{generate_password_hash(new_password)}' WHERE id = {user[0]};")
        try:
            server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
            server.ehlo()
            server.login('airport.noreplay@mail.ru', 'eFZU64fGaujW3TA7FnRe')
            mail_text = f"""Ваш новый пароль:\n\n{new_password}"""
            mail_text = mail_text.encode()
            server.sendmail('airport.noreplay@mail.ru', user[2], mail_text)
            server.close()
        except Exception as e:
            print(e)
            pass
        return redirect(url_for('auth.password_reset_complete') + f'?login={user_login}')
        
    return render_template('password_reset.html')

@auth_blueprint.route('/password/reset/complete/', methods=['GET'])
def password_reset_complete():
    user_login = request.args.get('login')
    email = db.one(f"SELECT email FROM users WHERE login = '{user_login}';")
    return render_template('password_reset_complete.html', email=email)
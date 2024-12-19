from flask import Blueprint, redirect, request, render_template, session, url_for, jsonify

from database import DatabaseManager as db


airport_blueprint = Blueprint('airport', __name__, template_folder='templates', static_folder='static')


@airport_blueprint.route('/', methods=['GET', 'POST'])
def profile():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if not current_user_id:
        return redirect(url_for('auth.login'))
    if is_admin:
        return redirect(url_for('admin.admin_menu'))

    sort_by = request.args.get('sort', None)
    search_query = f"""SELECT * FROM planes WHERE company_id = {current_user_id}"""

    search = request.args.get('search', None)
    if search:
        search_query += f" AND name ~* '{search}'"

    if not sort_by:
        sort_by = '0'
    if sort_by == '0':
        search_query += " ORDER BY name"
    elif sort_by == '1':
        search_query += " ORDER BY basket_id ASC"
    elif sort_by == '2':
        search_query += " ORDER BY basket_id DESC"

    if request.method == 'POST':
        name = request.form.get('name')

        db.execute(
            f"""INSERT INTO planes (name, company_id) VALUES (
            '{name}', {current_user_id});"""
        )
        return redirect(url_for('airport.profile') + '?sort=0')

    search_query += ';'
    info_name, info_country, money = db.one(f"""SELECT name, country, money FROM company_infos WHERE user_id = {current_user_id};""")
    planes = db.all(
        search_query
    )
    context = {
        'info_name': info_name,
        'info_country': info_country,
        'money': money,
        'planes': planes,
        'sort': sort_by,
        'search': search
    }
    return render_template('profile.html', **context)


@airport_blueprint.route('/hangar/<int:plane_id>/', methods=['GET', 'POST'])
def hangar(plane_id):
    basket_id = db.one(f"SELECT basket_id FROM planes WHERE id = {plane_id};")[0]
    context = {}
    if not basket_id:
        # создаем корзину c итоговой стоимостью равной цене аренды
        basket_id = db.one(
            f"""INSERT INTO baskets (sum_price) VALUES (
            (SELECT price FROM services WHERE id = 1)) RETURNING id;"""
        )[0]
        db.execute(f"UPDATE planes SET basket_id = {basket_id} WHERE id = {plane_id};")

        # добавляем стандартную услугу аренды анагара
        db.execute(
            f"""INSERT INTO baskets_services (basket_id, service_id)
            VALUES ({basket_id}, 1);"""
        )
    context.update({'sum_price': db.one(f"SELECT sum_price FROM baskets WHERE id = {basket_id};")[0]})
    added_services = db.all(
        f"""SELECT service_id FROM baskets_services WHERE basket_id = {basket_id};"""
    )
    added_services_ids = [i[0] for i in added_services]
    added_services_text = ', '.join(map(lambda x: str(x), added_services_ids))
    services = db.all(f"SELECT * FROM services WHERE id IN ({added_services_text});")
    all_services = db.all(f"SELECT * FROM services WHERE id != 1 AND id NOT IN ({added_services_text});")
    context.update({
        'basket_id': basket_id,
        'services': services,
        'plane_id': plane_id,
        'money': db.one(f"SELECT money FROM company_infos WHERE user_id = {session.get('current_user')};")[0],
        'all_services': all_services
    })
    return render_template('hangar.html', **context)


@airport_blueprint.route('/company/', methods=['GET', 'POST'])
def update_company_info():
    if not session.get('current_user'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        country = request.form.get('country')

        info_id = db.one(f"SELECT id FROM company_infos WHERE user_id = {session.get('current_user')};")[0]
        if info_id:
            db.execute(f"UPDATE company_infos SET name = '{name}', country = '{country}' WHERE id = {info_id};")
        else:
            db.execute(
                f"""INSERT INTO company_infos (name, country, user_id) VALUES
                ('{name}', '{country}', {session.get('current_user')});"""
            )
        return redirect(url_for('airport.profile') + '?sort=0')
    context = {
        'money': db.one(f"SELECT money FROM company_infos WHERE user_id = {session.get('current_user')};")[0],
        'country': db.one(f"SELECT country FROM company_infos WHERE user_id = {session.get('current_user')};")[0],
        'name': db.one(f"SELECT name FROM company_infos WHERE user_id = {session.get('current_user')};")[0]
    }
    return render_template('company.html', **context)


@airport_blueprint.route('/hangar/work/<int:basket_id>/', methods=['GET'])
def hangar_work(basket_id):
    bs = db.all(
        f"""SELECT service_id FROM baskets_services
        WHERE basket_id = {basket_id};
        """
    )
    service_ids = [i[0] for i in bs if i[0] != 1]
    services = db.all(
        f"""SELECT * FROM services WHERE id IN ({', '.join(map(lambda x: str(x), service_ids))});"""
    )
    sum_price = db.one(f"SELECT sum_price FROM baskets WHERE id = {basket_id};")[0]
    if not sum_price:
        return redirect(url_for('airport.profile') + '?sort=0')
    
    db.execute(
        f"""UPDATE company_infos SET money = money - {sum_price}
        WHERE user_id = {session.get('current_user')};
        UPDATE company_infos SET money =
        CASE WHEN money < 0 THEN 0 ELSE money END WHERE user_id = 
        {session.get('current_user')};
        """
    )

    order_about = ''
    for s in services:
        order_about += s[1] + ', '
    order_about = order_about[:-2]

    db.execute(
        f"""INSERT INTO orders (user_id, about, price) VALUES (
        {session.get('current_user')}, '{order_about}', {sum_price});
        """
    )

    db.execute(
        f"""DELETE FROM baskets_services WHERE basket_id = {basket_id};
        UPDATE planes SET basket_id = null WHERE basket_id = {basket_id};
        DELETE FROM baskets WHERE id = {basket_id};
        """
    )

    context = {
        'money': db.one(f"SELECT money FROM company_infos WHERE user_id = {session.get('current_user')};")[0],
        'services': services
    }
    return render_template('hangar_work.html', **context)


@airport_blueprint.route('/hangar/delete/<int:plane_id>/')
def hangar_delete(plane_id):
    db.execute(
        f"""UPDATE planes SET basket_id = NULL WHERE id = {plane_id};
        DELETE FROM baskets_services WHERE basket_id = 
        (SELECT basket_id FROM planes WHERE id = {plane_id});
        DELETE FROM baskets WHERE id = (SELECT basket_id FROM planes WHERE id = {plane_id});
        """
    )
    return redirect(url_for('airport.profile') + '?sort=0')


@airport_blueprint.route('/service/delete/')
def service_delete():
    plane_id = request.args.get('plane_id')
    items = request.args.get('items')
    items = items.split(',')

    basket_id = db.one(f"SELECT basket_id FROM planes WHERE id = {plane_id};")[0]
    added_services = db.all(f"SELECT service_id FROM baskets_services WHERE basket_id = {basket_id};")
    added_services_ids = [str(i[0]) for i in added_services]

    for item in items:
        if item == 1 or item not in added_services_ids:
            continue
        db.execute(
            f"""DELETE FROM baskets_services WHERE basket_id = {basket_id} AND
            service_id = {item};"""
        )
        db.execute(
            f"""UPDATE baskets SET sum_price = sum_price -
            (SELECT price FROM services WHERE id = {item});
            UPDATE baskets SET sum_price =
            CASE WHEN sum_price < 0 THEN 0 ELSE sum_price END WHERE id = {basket_id};"""
        )

    return jsonify()


@airport_blueprint.route('/service/add/')
def service_add():
    plane_id = request.args.get('plane_id')
    items = request.args.get('items')
    items = items.split(',')

    basket_id = db.one(f"SELECT basket_id FROM planes WHERE id = {plane_id};")[0]
    added_services = db.all(f"SELECT service_id FROM baskets_services WHERE basket_id = {basket_id};")
    added_services_ids = [str(i[0]) for i in added_services]

    response_services = []
    for item in items:
        if not item in added_services_ids:
            db.execute(
                f"""INSERT INTO baskets_services (basket_id, service_id)
                VALUES ({basket_id}, {item});"""
            )
            added_services_ids.append(item)

            _, name, price= db.one(f"SELECT * FROM services WHERE id = {item};")
            response_services.append((name, price, item))
            db.execute(f"UPDATE baskets SET sum_price = sum_price + {price} WHERE id = {basket_id};")
    return jsonify()


@airport_blueprint.route('/plane/delete/', methods=['POST'])
def plane_delete():
    plane_id = request.form.get('plane_id')
    basket_id = db.one(f"SELECT basket_id FROM planes WHERE id = {plane_id};")[0]
    db.execute(f"""DELETE FROM planes WHERE id = {plane_id};""")
    if basket_id:
        db.execute(
            f"""DELETE FROM baskets_services WHERE basket_id = {basket_id};
            DELETE FROM baskets WHERE id = {basket_id}"""
        )

    return jsonify()


@airport_blueprint.route('/orders/', methods=['GET', 'POST'])
def orders():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if not current_user_id:
        return redirect(url_for('auth.login'))
    if is_admin:
        return redirect(url_for('admin.admin_menu'))
    
    if request.method == 'POST':
        db.execute(
            f"""DELETE FROM orders WHERE user_id = {current_user_id};"""
        )
        return redirect(url_for('airport.orders'))
    orders = db.all(
        f"""SELECT about, price FROM orders WHERE user_id = {current_user_id};"""
    )
    context = {
        'orders': orders,
        'money': db.one(f"""SELECT money FROM company_infos WHERE user_id = {current_user_id};""")[0]
    }
    return render_template('orders.html', **context)
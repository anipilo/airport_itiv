from flask import Blueprint, redirect, request, render_template, session, url_for, jsonify, send_from_directory
from werkzeug.security import generate_password_hash
import xlsxwriter
import json

from database import DatabaseManager as db


admin_blueprint = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


@admin_blueprint.route('/', methods=['GET'])
def admin_menu():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    return render_template('admin_menu.html')


@admin_blueprint.route('/anlt/', methods=['GET'])
def admin_anlt():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    data = {}
    orders = db.all('SELECT * FROM orders;')
    for order in orders:
        if order[2] in data:
            data[order[2]] += 1
        else:
            data.update({order[2]: 1})
    context = {
        'orders': dict(sorted(data.items()))
    }
    return render_template('admin_anlt.html', **context)


@admin_blueprint.route('/companies/', methods=['GET', 'POST'])
def admin_companies():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        companies = db.all(
            f"""SELECT users.id, login, name, country, money FROM users JOIN company_infos ON user_id = users.id;"""
        )
        context = {
            'companies': companies
        }
        return render_template('admin_companies.html', **context)


@admin_blueprint.route('/company/<int:company_id>/', methods=['GET', 'POST'])
def admin_company(company_id):
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        planes = db.all(f"SELECT * FROM planes WHERE company_id = {company_id};")
        company = db.one(
            f"""SELECT users.id, login, name, country, money FROM users JOIN company_infos
            ON users.id = user_id WHERE users.id = {company_id};"""
        )

        context = {
            'planes': planes,
            'company': company
        }
        return render_template('admin_company.html', **context)
    else:
        user_id = request.form.get('user_id')
        login = request.form.get('login')
        name = request.form.get('name', 'NULL')
        country = request.form.get('country', 'NULL')
        money = request.form.get('money', 'NULL')

        db.execute(
            f"""
            UPDATE users SET login = '{login}' WHERE id = {user_id};
            UPDATE company_infos SET name = '{name}', country = '{country}',
            money = {money} WHERE user_id = {user_id};"""
        )
        return redirect(url_for('admin.admin_company', company_id=company_id))


@admin_blueprint.route('/company/add/', methods=['GET', 'POST'])
def admin_company_add():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return render_template('admin_company_add.html')
    else:
        login = request.form.get('login')
        password = request.form.get('password')

        if login and password:
            user_id = db.one(
                f"""INSERT INTO users (login, password) VALUES 
                ('{login}', '{generate_password_hash(password)}') RETURNING id;"""
            )[0]

            name = request.form.get('name')
            if not name:
                name = None
            country = request.form.get('country')
            if not country:
                country = None
            money = request.form.get('money')
            if not money:
                money = None
            else:
                money = float(money)

            db.execute(
                f"""INSERT INTO company_infos (name, country, money, user_id) VALUES 
                ('{name if name else ""}', '{country if country else ""}', {money}, {user_id});"""
            )
        return redirect(url_for('admin.admin_companies'))


@admin_blueprint.route('/company/delete/', methods=['POST'])
def admin_company_delete():
    user_id = request.form.get('user_id')
    db.execute(
        f"""DELETE FROM planes WHERE company_id = {user_id};
        DELETE FROM company_infos WHERE user_id = {user_id};
        DELETE FROM users WHERE id = {user_id};"""
    )
    return jsonify()


@admin_blueprint.route('/plane/delete/', methods=['POST'])
def admin_plane_delete():
    plane_id = request.form.get('plane_id')
    db.execute(f"DELETE FROM planes WHERE id = {plane_id};")
    return jsonify()


@admin_blueprint.route('/service/delete/', methods=['POST'])
def admin_service_delete():
    service_id = request.form.get('service_id')
    if service_id != '1':
        db.execute(f"DELETE FROM services WHERE id = {service_id};")
        return jsonify()


@admin_blueprint.route('/services/', methods=['GET', 'POST'])
def admin_services():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        services = db.all(f"SELECT * FROM services;")
        context = {'services': services}
        return render_template('admin_services.html', **context)


@admin_blueprint.route('/plane/<int:company_id>/add/', methods=['GET', 'POST'])
def admin_plane_add(company_id):
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        context = {
            'company_id': company_id
        }
        return render_template('admin_plane_add.html', **context)
    else:
        name = request.form.get('name')
        if not name:
            name = 'NULL'
        basket_id = request.form.get('basket_id')
        if not basket_id:
            basket_id = 'NULL'
        company_id = request.form.get('company_id')
        if not company_id:
            company_id = 'NULL'

        if name:
            db.execute(
                f"""INSERT INTO planes (name, basket_id, company_id) VALUES
                ('{name}', {basket_id}, {company_id});"""
            )
        return redirect(url_for('admin.admin_company', company_id=company_id))


@admin_blueprint.route('/plane/<int:company_id>/<int:plane_id>/', methods=['GET', 'POST'])
def admin_plane(company_id, plane_id):
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    plane = db.one(f"SELECT * FROM planes WHERE id = {plane_id};")
    if request.method == 'GET':
        context = {
            'plane': plane,
            'company_id': company_id
        }
        return render_template('admin_plane.html', **context)
    else:
        name = request.form.get('name')
        if not name:
            name = 'NULL'
        basket_id = request.form.get('basket_id')
        if not basket_id:
            basket_id = 'NULL'
        company_id = request.form.get('company_id')
        if not company_id:
            company_id = 'NULL'

        db.execute(f"UPDATE planes SET name = '{name}', basket_id = {basket_id}, company_id = {company_id} WHERE id = {plane_id};")
        return redirect(url_for('admin.admin_company', company_id=company_id))


@admin_blueprint.route('/basket/delete/', methods=['POST'])
def admin_basket_delete():
    basket_id = request.form.get('basket_id')
    # удаляем id корзины из самолета
    db.execute(
        f"""UPDATE planes SET basket_id = NULL WHERE basket_id = {basket_id};"""
    )
    # удалеям все услуги из корзины
    db.execute(
        f"""DELETE FROM baskets_services WHERE basket_id = {basket_id};
        DELETE FROM baskets WHERE id = {basket_id};"""
    )
    return jsonify()


@admin_blueprint.route('/services/add/', methods=['GET', 'POST'])
def admin_service_add():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return render_template('admin_service_add.html')
    else:
        name = request.form.get('name')
        if not name:
            name = None
        price = request.form.get('price')
        if not price:
            price = None

        if price and name:
            db.execute(
                f"""INSERT INTO services (name, price) VALUES 
                ('{name}', {price});"""
            )
            return redirect(url_for('admin.admin_services'))
        return redirect(url_for('admin.admin_service_add'))


@admin_blueprint.route('/services/<int:service_id>/', methods=['GET', 'POST'])
def admin_service(service_id):
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    service = db.one(f"SELECT * FROM services WHERE id = {service_id};")
    if request.method == 'GET':
        return render_template('admin_service.html', service=service)
    else:
        name = request.form.get('name')
        if not name:
            name = 'NULL'
        price = request.form.get('price')
        if not price:
            price = 'NULL'

        if price and name:
            db.execute(f"UPDATE services SET name = '{name}', price = {price} WHERE id = {service_id};")
        return redirect(url_for('admin.admin_services'))


@admin_blueprint.route('/baskets/', methods=['GET', 'POST'])
def admin_baskets():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        context = {'baskets': db.all("SELECT * FROM baskets;")}
        return render_template('admin_baskets.html', **context)


@admin_blueprint.route('/baskets/add/', methods=['GET', 'POST'])
def admin_basket_add():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return render_template('admin_basket_add.html')
    else:
        sum_price = request.form.get('sum_price')
        if not sum_price:
            sum_price = None

        if sum_price:
            service_price = db.one(f"SELECT price FROM services WHERE id = 1;")[0]
            basket_id = db.one(
                f"""INSERT INTO baskets (sum_price) VALUES ({int(sum_price) + int(service_price)}) RETURNING id;"""
            )[0]
            db.execute(
                f"""INSERT INTO baskets_services (basket_id, service_id) VALUES
                ({basket_id}, 1);"""
            )
            return redirect(url_for('admin.admin_baskets'))
        return redirect(url_for('admin.admin_basket_add'))


@admin_blueprint.route('/baskets/<int:basket_id>/', methods=['GET', 'POST'])
def admin_basket(basket_id):
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    basket = db.one(f"SELECT * FROM baskets WHERE id = {basket_id};")
    if request.method == 'GET':
        baskets_services = db.all(
            f"""SELECT service_id FROM baskets_services WHERE basket_id = {basket_id};"""
        )
        services_ids = [i[0] for i in baskets_services]
        services = db.all(f"SELECT * FROM services WHERE id IN ({', '.join(map(lambda x: str(x), services_ids))});")
        context = {
            'basket': basket,
            'services': services
        }
        return render_template('admin_basket.html', **context)
    else:
        sum_price = request.form.get('sum_price')
        if not sum_price and sum_price != 0:
            sum_price = None
        else:
            sum_price = int(sum_price)

        if sum_price or sum_price == 0:
            db.execute(f"UPDATE baskets SET sum_price = {sum_price} WHERE id = {basket_id};")
        return redirect(url_for('admin.admin_baskets'))


@admin_blueprint.route('/baskets/delete-service/', methods=['POST'])
def admin_basket_service_delete():
    basket_id = request.form.get('basket_id')
    service_id = request.form.get('service_id')

    if service_id != '1':
        basket = db.one(f"SELECT * FROM baskets WHERE id = {basket_id};")
        if not basket:
            return jsonify()
        db.execute(
            f"""UPDATE baskets SET sum_price = sum_price - 
            (SELECT price FROM services WHERE id = {service_id})
            WHERE id = {basket_id};
            UPDATE baskets SET sum_price =
            CASE WHEN sum_price < 0 THEN 0 ELSE sum_price END;"""
        )
        db.execute(
            f"""DELETE FROM baskets_services WHERE basket_id = {basket_id} AND service_id = {service_id};"""
        )
    return jsonify()


@admin_blueprint.route('/baskets/add-service/', methods=['POST'])
def admin_add_basket_service():
    basket_id = request.form.get('basket_id')
    service_id = request.form.get('service_id')

    if service_id != '1':

        basket = db.one(f"SELECT * FROM baskets WHERE id = {basket_id};")
        if not basket:
            return jsonify()
        db.execute(
            f"""UPDATE baskets SET sum_price = sum_price + 
            (SELECT price FROM services WHERE id = {service_id})
            WHERE id = {basket_id};
            INSERT INTO baskets_services (basket_id, service_id) VALUES 
            ({basket_id}, {service_id});
            """
        )
    return jsonify()


@admin_blueprint.route('/export/', methods=['GET'])
def admin_export():
    current_user_id = session.get('current_user')
    is_admin = bool(session.get('current_user_admin'))
    if current_user_id:
        if not is_admin:
            return redirect(url_for('auth.login'))
    context = {
        'tablenames': db.tablenames() 
    }
    return render_template('admin_export.html', **context)


@admin_blueprint.route('/download/json/', methods=['GET', 'POST'])
def download_json():
    data = {}
    tablenames = request.args.get('tablenames', '')
    tablenames = tablenames.split(',')
    print(tablenames)
    #tablenames = 

    for tn in tablenames:
        elements_names = db.desc(tn)
        elements = db.all(f"SELECT * FROM {tn};")
        elements_data = []
        for el in elements:
            element_data = {}
            for k in range(len(elements_names)):
                element_data.update({elements_names[k]: el[k]})
            elements_data.append(element_data)
        data.update({
            tn: elements_data
        })
    with open('./data/data.json', 'w') as f:
        f.write(json.dumps(data, default=str, indent=4, separators=(',', ': ')))
    return send_from_directory('./data/', 'data.json')


@admin_blueprint.route('/download/excel/', methods=['GET', 'POST'])
def download_excel():
    tablenames = request.args.get('tablenames', '')
    tablenames = tablenames.split(',')
    print(tablenames)

    with xlsxwriter.Workbook('./data/data.xlsx') as workbook:
        for tn in tablenames:
            elements = db.all(f"SELECT * FROM {tn} ORDER BY id;")
            worksheet = workbook.add_worksheet(tn)
            column = 0
            for value in db.desc(tn):
                worksheet.write(0, column, value)
                column += 1
            row = 1
            for element in elements:
                column = 0
                for value in element:
                    worksheet.write(row, column, value)
                    column += 1
                row += 1
            
    return send_from_directory('./data/', 'data.xlsx')


@admin_blueprint.route('/import/', methods=['GET', 'POST'])
def admin_import():
    try:
        current_user_id = session.get('current_user')
        is_admin = bool(session.get('current_user_admin'))
        if current_user_id:
            if not is_admin:
                return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            files = request.files
            c = 0
            if files:
                file = files['file']
                with file.stream as f:
                    data = json.loads(f.read())
                    for tablename in data.keys():
                        for obj in data[tablename]:
                            fields = obj.keys()
                            fields_str = '(' + ','.join(fields) + ')'
                            values_str = '('
                            for field in fields:
                                values_str += f"'{obj[field]}',"
                            values_str = values_str[:-1] + ')'
                            db.execute(f"INSERT INTO {tablename} {fields_str} VALUES {values_str};")
                            c += 1
            return redirect(url_for('admin.admin_import_success') + f'?c={c}')
        return render_template('admin_import.html')
    except:
        return redirect(url_for('admin.admin_import_error'))


@admin_blueprint.route('/import/success/', methods=['GET'])
def admin_import_success():
    c = request.args.get('c')
    return render_template('admin_import_success.html', c=c)


@admin_blueprint.route('/import/error/', methods=['GET'])
def admin_import_error():
    return render_template('admin_import_error.html')

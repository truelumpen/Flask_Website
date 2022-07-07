import os
from datetime import datetime

import flask_login
from docxtpl import DocxTemplate
from flask import render_template, url_for, flash, request, redirect
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from project import db, data, checkout, app
from project.checks import *
from project.config import *
from project.db_tables import Customer, Seller, Contract, Auto, Order


@app.route('/', methods=['GET'])
def main_page():
    return render_template('mainpage.html')


@app.route('/home', methods=['GET', 'POST'])
@flask_login.login_required
def user_main_page():
    return render_template('usermainpage.html')


@app.route('/my_filial', methods=['GET', 'POST'])
@flask_login.login_required
def my_filial():
    id = current_user.id
    user = Seller.query.filter_by(id=id).first()
    cars = Auto.query.filter_by(fil_id=id).filter_by(sold=False).all()
    return render_template('filial.html', user=user, cars=cars)


@app.route('/filials', methods=['GET', 'POST'])
@flask_login.login_required
def filials():
    user = request.args.get('user')
    id = int(str(user).split(' ')[-1][:-1])
    user = Seller.query.filter_by(id=id).first()
    cars = Auto.query.filter_by(fil_id=id).filter_by(sold=False).all()
    return render_template('filial_user.html', user=user, cars=cars)


@app.route('/chose_auto', methods=['GET', 'POST'])
@flask_login.login_required
def chose_auto():
    id = current_user.id
    user = Seller.query.filter_by(id=id).first()
    cars = Auto.query.filter_by(fil_id=id).filter_by(sold=False).all()
    return render_template('chose_auto.html', user=user, cars=cars)


@app.route('/chose_fil', methods=['GET', 'POST'])
@flask_login.login_required
def chose_fil():
    sellers = Seller.query.all()
    return render_template('chose_fil.html', sellers=sellers)


@app.route('/delete_auto/<int:id>', methods=['POST'])
@flask_login.login_required
def delete_auto(id):
    car = Auto.query.filter_by(id=id).first()
    db.session.delete(car)
    db.session.commit()
    return redirect(url_for('chose_auto'))


@app.route('/about', methods=['GET', 'POST'])
def author_page():
    if current_user.is_authenticated:
        id = current_user.id
        seller = Seller.query.filter_by(id=id).first()
        if seller:
            return render_template('author_seller.html')
        else:
            return render_template('author.html')
    else:
        return render_template('anonauth.html')


@app.route('/seller_mainpage', methods=['GET'])
@flask_login.login_required
def seller_main_page():
    return render_template('seller_mainpage.html')


@app.route('/reg_type', methods=['GET', 'POST'])
def reg_type():
    return render_template('chose_reg_type.html')


@app.route('/customer_type', methods=['GET', 'POST'])
def customer_type():
    return render_template('customer_type.html')


@app.route('/orders', methods=['GET'])
def orders():
    id = current_user.id
    customer = Customer.query.filter_by(id=id).first()
    orders = Order.query.filter_by(customer_id=id).all()
    return render_template('orders.html', orders=orders, user=customer)


@app.route('/contracts', methods=['GET'])
def contracts():
    id = current_user.id
    customer = Customer.query.filter_by(id=id).first()
    contracts = Contract.query.filter_by(customer_id=id).all()
    return render_template('contracts.html', contracts=contracts, user=customer)



@app.route('/buy_car/<string:car>', methods=['GET', 'POST'])
def buy_car(car):
    customer = current_user
    user_id = int(str(customer).split(' ')[-1][:-1])
    customer = Customer.query.filter_by(id=user_id).first()
    car_id = int(str(car).split(' ')[-1][:-1])
    car = Auto.query.filter_by(id=car_id).first()
    if not car:
        return redirect(url_for('user_main_page'))
    if car.sold:
        return redirect(url_for('user_main_page'))
    user = Seller.query.filter_by(id=car.fil_id).first()
    style = 'none'
    if request.method == 'POST':
        style = 'block'
        car.sold = True
        db.session.commit()
        if customer.sign:
            doc = DocxTemplate(f"{PATH_TO_DOCUMENT_IC}/шаблон_юрлиц.docx")
            context = {'date': datetime.now().date(),
                       'brand': car.brand,
                       'model': car.model,
                       'price': car.price,
                       'company_name': customer.com_name,
                       'customer_name': str(str(customer.fname)[0] + '. ' + customer.lname),
                       'fil_name': user.fil_name,
                       'seller_name': str(str(user.fname)[0] + '. ' + user.lname),
                       'inn': user.inn,
                       'address': user.address}
            doc.render(context)
            n = len(os.listdir(f"{PATH_TO_DOCUMENT_DIR}/{customer.email}"))
            doc.save(f"{PATH_TO_DOCUMENT_DIR}/{customer.email}/Договор-{n + 1}.docx")
            contract = Contract(date=datetime.now().date(), document=f"Договор-{n + 1}",
                                car_id=car_id, customer_id=user_id)
            db.session.add(contract)
            db.session.commit()
            user.trades += 1
            db.session.commit()
            data['amount'] = str(int(car.price)) + '00'
            return redirect(checkout.url(data).get('checkout_url'))
        else:
            doc = DocxTemplate(f"{PATH_TO_DOCUMENT_IC}/шаблон_физлиц.docx")
            context = {'date': datetime.now().date(),
                       'brand': car.brand,
                       'model': car.model,
                       'customer_name': str(str(customer.fname)[0] + '. ' + customer.lname),
                       'fil_name': user.fil_name,
                       'seller_name': str(str(user.fname)[0] + '. ' + user.lname),
                       'inn': user.inn,
                       'price': car.price,
                       'address': user.address}
            doc.render(context)
            n = len(os.listdir(f"{PATH_TO_DOCUMENT_DIR}/{customer.email}"))
            doc.save(f"{PATH_TO_DOCUMENT_DIR}/{customer.email}/Договор-{n+1}.docx")
            contract = Contract(date=datetime.now().date(), document=f"Договор-{n+1}",
                                car_id=car_id, customer_id=user_id)
            db.session.add(contract)
            db.session.commit()
            user.trades += 1
            db.session.commit()
        return render_template('buy_car.html', car=car, user=user, customer=customer, style=style)
    return render_template('buy_car.html', car=car, user=user, customer=customer, style=style)


@app.route('/order', methods=['GET', 'POST'])
@flask_login.login_required
def order():
    id = current_user.id
    customer = Customer.query.filter_by(id=id).first()
    if request.method == 'POST':
        try:
            model = request.form['model']
            gear = request.form['gear']
            helm = request.form['helm']
            time = request.form['time']
            color = request.form['color']
            power = int(request.form.get('power'))
            pl = price_list
            price = pl[time] * (pl[model] + pl[gear] + pl[helm] + pl[power])
            doc = DocxTemplate(f"{PATH_TO_DOCUMENT_IC}/заказ_шаблон.docx")
            context = {'date': datetime.now().date(),
                       'gear': gear,
                       'model': model,
                       'name': str(str(customer.fname)[0] + '. ' + customer.lname),
                       'helm': helm,
                       'power': power,
                       'time': time,
                       'price': price,
                       'color': color}
            doc.render(context)
            n = len(os.listdir(f"{PATH_TO_ORDER_DIR}/{customer.email}"))
            doc.save(f"{PATH_TO_ORDER_DIR}/{customer.email}/Заказ-{n + 1}.docx")
            order = Order(model=model, gear=gear, helm=helm,
                          time=time, color=color, power=power,
                          date=datetime.now().date(), customer_id=id,
                          document=f"Заказ-{n + 1}", price=price)
            db.session.add(order)
            db.session.commit()
            flash('Заказ создан. Проверьте вкладку Заказы.')
        except KeyError:
            flash('Не выбраны некоторые параметры')
    return render_template('order.html')


@app.route('/add_auto', methods=['GET', 'POST'])
@flask_login.login_required
def add_auto():
    id = current_user.id
    seller = Seller.query.filter_by(id=id).first()
    if request.method == 'POST':
        ValErr1, ValErr2 = False, False
        price = request.form.get('price')
        brand = request.form.get('brand')
        model = request.form.get('model')
        distance = request.form.get('distance')
        image = request.files['image']
        try:
            price = abs(float(price))
        except ValueError:
            ValErr1 = True
        try:
            distance = abs(int(distance))
        except ValueError:
            ValErr2 = True
        if ValErr1:
            flash(f'Цена должна быть числом')
        elif ValErr2:
            flash(f'Пробег должен быть числом')
        elif not (price and brand and model and distance):
            flash('Не заполнены обязательные поля!')
        elif image.filename == '':
            flash('Не прикреплено изображение')
        elif not allowed_img(image.filename):
            flash('Разрешенные разрширения изображения: PNG, JPG, JPEG ')
        else:
            filename = secure_filename(image.filename)
            image.save(os.path.join(f"{PATH_TO_FILIAL_IMG}/{seller.fil_name}/cars", filename))
            new_car = Auto(price=price, brand=brand, model=model,
                           distance=distance, fil_id=seller.id,
                           image=filename, sold=False)
            db.session.add(new_car)
            db.session.commit()
            flash('Автомобиль успешно добавлен!')
    return render_template('add_auto.html')


"""
ПРОФИЛИ
"""


@app.route('/profile_seller', methods=['GET', 'POST'])
@flask_login.login_required
def profile_seller():
    val_err = False
    id = current_user.id
    user = Seller.query.filter_by(id=id).first()
    if request.method == 'POST':
        email = request.form.get('email')
        password2 = request.form.get('password2')
        password = request.form.get('password')
        fil_name = request.form.get('fil_name')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        image = request.files['image']
        inn = request.form.get('inn')
        address = request.form.get('address')
        try:
            inn = abs(int(inn))
        except ValueError:
            val_err = True
        if Customer.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(email=email).first() and (Seller.query.filter_by(email=email).first().id != id):
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(fil_name=fil_name).first() and (
                Seller.query.filter_by(fil_name=fil_name).first().id != id):
            flash(f"Филиал {fil_name} уже был зарегестрирован")
        elif val_err:
            flash(f'ИНН должно быть числом')
        elif not (email and fil_name and password and password2 and fname and lname and inn and address) and (
                (user.email != email) or (user.fname != fname) or (user.lname != lname) or
                (user.fil_name != fil_name) or (user.address != address) or (user.inn != inn)):
            flash('Не заполнены обязательные поля!')
        elif password != password2:
            flash('Пароли не совпадают')
        elif (image.filename != '') and (not allowed_img(image.filename)):
            flash('Разрешенные разрширения изображения: PNG, JPG, JPEG ')
        else:
            if user.fil_name != fil_name:
                os.rename(f"{PATH_TO_FILIAL_IMG}/{user.fil_name}", f"{PATH_TO_FILIAL_IMG}/{fil_name}")
            if image.filename != '':
                filename = secure_filename(image.filename)
                os.rename(f"{PATH_TO_FILIAL_IMG}/{user.fil_name}", f"{PATH_TO_FILIAL_IMG}/{fil_name}")
                os.remove(f"{PATH_TO_FILIAL_IMG}/{user.fil_name}/{user.image}")
                image.save(os.path.join(f"{PATH_TO_FILIAL_IMG}/{fil_name}", filename))
                user.image = filename
            hash_pwd = generate_password_hash(password)
            user.email = email
            user.password = hash_pwd
            user.fname = fname
            user.lname = lname
            user.fil_name = fil_name
            user.inn = inn
            user.address = address
            db.session.commit()
            flash('Изменения сохранены')
    return render_template('profile_seller.html', user=user, car=None)


@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def profile():
    id = current_user.id
    user = Customer.query.filter_by(id=id).first()
    if request.method == 'POST':
        email = request.form.get('email')
        password2 = request.form.get('password2')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        if Customer.query.filter_by(email=email).first() and (Customer.query.filter_by(email=email).first().id != id):
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif not (email and password and password2 and fname and lname) and (
                (user.email != email) or (user.fname != fname) or (user.lname != lname)):
            flash('Не заполнены обязательные поля!')
        elif password != password2:
            flash('Пароли не совпадают')
        else:
            if user.email != email:
                os.rename(f"{PATH_TO_DOCUMENT_DIR}/{user.email}", f"{PATH_TO_DOCUMENT_DIR}/{email}")
                os.rename(f"{PATH_TO_ORDER_DIR}/{user.email}", f"{PATH_TO_ORDER_DIR}/{email}")
                user.email = email
            hash_pwd = generate_password_hash(password)
            user.password = hash_pwd
            user.fname = fname
            user.lname = lname
            db.session.commit()
            flash('Изменения сохранены')
    if user.sign:
        return redirect(url_for('profile_com'))
    else:
        return render_template('profile.html', user=user)


@app.route('/profile_car', methods=['GET', 'POST'])
@flask_login.login_required
def profile_car():
    car = request.args.get('car')
    id = int(str(car).split(' ')[-1][:-1])
    car = Auto.query.filter_by(id=id).first()
    seller = Seller.query.filter_by(id=car.fil_id).first()
    if request.method == 'POST':
        ValErr1, ValErr2 = False, False
        price = request.form.get('price')
        brand = request.form.get('brand')
        model = request.form.get('model')
        distance = request.form.get('distance')
        image = request.files['image']
        password2 = request.form.get('password2')
        password = request.form.get('password')
        try:
            price = abs(float(price))
        except ValueError:
            ValErr1 = True
        try:
            distance = abs(int(distance))
        except ValueError:
            ValErr2 = True
        if ValErr1:
            flash(f'Цена должна быть числом')
        elif ValErr2:
            flash(f'Пробег должен быть числом')
        elif not (price and brand and model and distance) and (
                (car.price != price) and (car.brand != brand) and (car.model != model)
                and (car.distance != distance)):
            flash('Не заполнены обязательные поля!')
        elif (image.filename != '') and (not allowed_img(image.filename)):
            flash('Разрешенные разрширения изображения: PNG, JPG, JPEG ')
        elif password != password2:
            flash('Пароли не совпадают')
        else:
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(f"{PATH_TO_FILIAL_IMG}/{seller.fil_name}/cars", filename))
                car.image = filename
            car.price = price
            car.brand = brand
            car.model = model
            car.distance = distance
            db.session.commit()
            flash('Изменения сохранены')
    return render_template('profile_car.html', car=car)


@app.route('/profile_com', methods=['GET', 'POST'])
@flask_login.login_required
def profile_com():
    id = current_user.id
    user = Customer.query.filter_by(id=id).first()
    if request.method == 'POST':
        email = request.form.get('email')
        password2 = request.form.get('password2')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        com_name = request.form.get('com_name')
        if Customer.query.filter_by(email=email).first().id != id:
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif not (email and password and password2 and fname and lname and com_name) and (
                (user.email != email) or (user.fname != fname) or (user.lname != lname) or (user.com_name != com_name)):
            flash('Не заполнены обязательные поля!')
        elif password != password2:
            flash('Пароли не совпадают')
        else:
            if user.email != email:
                os.rename(f"{PATH_TO_DOCUMENT_DIR}/{user.email}", f"{PATH_TO_DOCUMENT_DIR}/{email}")
                os.rename(f"{PATH_TO_ORDER_DIR}/{user.email}", f"{PATH_TO_ORDER_DIR}/{email}")
                user.email = email
            hash_pwd = generate_password_hash(password)
            user.password = hash_pwd
            user.fname = fname
            user.lname = lname
            user.com_name = com_name
            db.session.commit()
            flash('Изменения сохранены')
    return render_template('profile_com.html', user=user)


"""
АВТОРИЗАЦИЯ
"""


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            seller = Seller.query.filter_by(email=login).first()
            if seller and check_password_hash(seller.password, password):
                login_user(seller)
                print(f'{seller} вошел как продавец')
                return redirect(url_for('seller_main_page'))
            customer = Customer.query.filter_by(email=login).first()
            if customer and check_password_hash(customer.password, password):
                login_user(customer)
                print(f'{customer} вошел как покупатель')
                return redirect(url_for('user_main_page'))
            else:
                flash('Неправильный логин или пароль!')
        else:
            flash('Не заполнены обязательные поля!')
    return render_template('sign_in.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password2 = request.form.get('password2')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        if Customer.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif not (email and password and password2 and fname and lname):
            flash('Не заполнены обязательные поля!')
        elif password != password2:
            flash('Пароли не совпадают')
        else:
            hash_pwd = generate_password_hash(password)
            os.mkdir(f"{PATH_TO_DOCUMENT_DIR}/{email}")
            os.mkdir(f"{PATH_TO_ORDER_DIR}/{email}")
            new_user = Customer(email=email, password=hash_pwd, sign=False,
                                com_name=None, fname=fname, lname=lname)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('sign_in'))
    return render_template('sign_up.html')


@app.route('/sign_up_fil', methods=['GET', 'POST'])
def sign_up_fil():
    if request.method == 'POST':
        ValErr = False
        email = request.form.get('email')
        password2 = request.form.get('password2')
        password = request.form.get('password')
        fil_name = request.form.get('fil_name')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        image = request.files['image']
        inn = request.form.get('inn')
        address = request.form.get('address')
        try:
            inn = abs(int(inn))
        except ValueError:
            ValErr = True
        if Customer.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(fil_name=fil_name).first():
            flash(f"Филиал {fil_name} уже был зарегестрирован")
        elif ValErr:
            flash(f'ИНН должно быть числом')
        elif not (email and fil_name and password and password2 and fname and lname and inn and address):
            flash('Не заполнены обязательные поля!')
        elif password != password2:
            flash('Пароли не совпадают')
        elif image.filename == '':
            flash('Не прикреплено изображение')
        elif not allowed_img(image.filename):
            flash('Разрешенные разрширения изображения: PNG, JPG, JPEG ')
        else:
            filename = secure_filename(image.filename)
            os.mkdir(f"{PATH_TO_FILIAL_IMG}/{fil_name}")
            os.mkdir(f"{PATH_TO_FILIAL_IMG}/{fil_name}/cars")
            image.save(os.path.join(f"{PATH_TO_FILIAL_IMG}/{fil_name}", filename))
            hash_pwd = generate_password_hash(password)
            new_user = Seller(email=email, password=hash_pwd, image=filename,
                              fil_name=fil_name, fname=fname, lname=lname,
                              inn=inn, address=address, trades=0)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('sign_in'))
    return render_template('sign_up_fil.html')


@app.route('/sign_up_com', methods=['GET', 'POST'])
def sign_up_com():
    if request.method == 'POST':
        email = request.form.get('email')
        password2 = request.form.get('password2')
        password = request.form.get('password')
        com_name = request.form.get('com_name')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        if Customer.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif Seller.query.filter_by(email=email).first():
            flash(f'Почта {email} уже была зарегестрирована')
        elif not (email and com_name and password and password2 and fname and lname):
            flash('Не заполнены обязательные поля!')
        elif password != password2:
            flash('Пароли не совпадают')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = Customer(email=email, password=hash_pwd, sign=True,
                                com_name=com_name, fname=fname, lname=lname)
            os.mkdir(f"{PATH_TO_DOCUMENT_DIR}/{email}")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('sign_in'))
    return render_template('sign_up_com.html')


@app.route('/logout', methods=['GET', 'POST'])
@flask_login.login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.after_request
def redirect_to_next(response):
    if response.status[:3] == 401:
        return redirect(url_for('sign_in') + '?next=' + request.url)
    return response

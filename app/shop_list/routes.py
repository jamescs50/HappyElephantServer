from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
#from langdetect import detect, LangDetectException
#from app.translate import translate
from app import db
from app.shop_list.forms import ProductForm
from app.models import  User,ShopListProduct
from app.shop_list import bp


@bp.route('/products', methods=['GET', 'POST'])
#@login_required
def products():
    if request.method == 'POST':
        action = request.form['action']
        p_id = request.form['p_id']
        product = ShopListProduct.query.get(p_id)
        if action == 'delete':
            db.session.delete(product)
            db.session.commit()
            flash('Product deleted successfully!', 'success')
        elif action == 'update':
            description = request.form['description']
            barcode = request.form['barcode']
            product.description = description
            product.barcode = barcode
            db.session.commit()
            flash('Product updated successfully!', 'success')
        return redirect(url_for('shop_list.products'))

    p = ShopListProduct.query.all()
    return  render_template('shop_list/products.html',title='Items',products=p)
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
#from langdetect import detect, LangDetectException
#from app.translate import translate
from app import db
from app.shop_list.forms import ProductForm,EmptyForm
from app.models import  User,ShopListProduct
from app.shop_list import bp



@bp.route('/products')
@login_required
#@login_required
def products():
    p = ShopListProduct.query.all()
    return  render_template('shop_list/products.html',title='Items',products=p)


#@bp.route('/popup/product/<productId>')
#def product_popup(productId):
#    p = ShopListProduct.query.get(productId)
#    form = EmptyForm()
#    return render_template('shop_list/product_popup.html', product=p, form=form)

@bp.route('/product/<productId>', methods=['GET', 'POST'])
@login_required
def product_form(productId):
    p = ShopListProduct.query.get(productId)
    form = ProductForm()
    if form.validate_on_submit():
        p.description = form.description.data
        p.barcode = form.barcode.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('shop_list.product_form',productId = productId))
    elif request.method == 'GET':
        form.description.data = p.description
        form.barcode.data = p.barcode

    return render_template('shop_list/product.html', form=form,product=p)

@bp.route('/product/add', methods=['GET', 'POST'])
@login_required
def newproduct_form():
    form = ProductForm()
    if form.validate_on_submit():
        p = ShopListProduct()
        p.description = form.description.data
        p.barcode = form.barcode.data
        db.session.add(p)
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('shop_list.product_form',productId = p.id))
    return render_template('shop_list/product.html', form=form)
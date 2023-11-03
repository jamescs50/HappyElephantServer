from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
#from langdetect import detect, LangDetectException
#from app.translate import translate
from app import db
from app.shop_list.forms import ProductForm,EmptyForm
from app.models import  User,ShopListProduct,ShopListRequest,ShopListRequestStatus
from app.shop_list import bp

#region products
@bp.route('/products', methods=['GET','POST'])
@login_required
#@login_required
def products():
    p = ShopListProduct.query.all()
    form = EmptyForm()
    if request.method == 'POST':
        action = request.form['action']
        productId = request.form['product_id']
        product = ShopListProduct.query.get(productId)
        if action == 'remove_from_list':
            for o in product.open_requests:
                o.status = ShopListRequestStatus.Cancelled
            db.session.commit()
        elif action == 'add_to_list':
            product.make_request()
    return  render_template('shop_list/products.html',title='Items',products=p,form=form)

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

#endregion

#region mylist
@bp.route('/mylist', methods=['GET', 'POST'])
@login_required
def mylist():
    my_reqs = current_user.shop_list_requests

@bp.route('/shoppinglist',methods=['GET','POST'])
@login_required
def shoppinglist():
    openlist = ShopListRequest.query.fi

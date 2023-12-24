from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
#from langdetect import detect, LangDetectException
import markdown
#from app.translate import translate
from app import db
from app.main.forms import EmptyForm,EditProfileForm
from app.models import  User,WeatherData,MarkdownContent
from app.main import bp



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('app/dashboard.html', title=('Home'))

#region user
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    form = EmptyForm()
    return render_template('user.html', user=user, form=form)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)

#endregion

@bp.route('/page/<title>')
def page(title):
    mdc = markdown.Markdown(extensions=["fenced_code","codehilite"])
    md = MarkdownContent.query.filter_by(title=title).first_or_404()
    md.md_content = mdc.convert(md.md_content)
    return render_template('app/page.html',md=md)


@bp.route('/data')
@login_required
def data():
    d = WeatherData.query.all()
    return  render_template('app/data.html',title='Data',data=d)
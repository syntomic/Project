# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response

from cleanlog.extensions import db
from cleanlog.forms import HelloForm
from cleanlog.models import Message, Post, Category, Comment
from cleanlog.utils import redirect_back

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/', methods=['GET', 'POST'])
def index():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    form = HelloForm()

    if form.validate_on_submit():
        name = form.name.data
        body = form.body.data
        message = Message(body=body, name=name)
        db.session.add(message)
        db.session.commit()
        flash('Your message have been sent to the world')
        return redirect_back(url_for('blog.index'))

    return render_template('blog/index.html', form=form, messages=messages)

@blog_bp.route('/math')
def math():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['CLEANLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items

    return render_template('blog/math.html', pagination=pagination, posts=posts)

@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


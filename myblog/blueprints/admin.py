# -*- coding: utf-8 -*-

import os
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint
from flask_login import login_required, current_user

from myblog.extensions import db
from myblog.forms import SettingForm, PostForm, CategoryForm, TopicForm, ThoughtForm
from myblog.models import Post, Category, Topic, Comment, Thought
from myblog.utils import redirect_back


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    form = SettingForm()

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.about = form.about.data

        db.session.commit()
        
        flash('Setting updated.', 'success')

        return redirect(url_for('blog.about'))

    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.about.data = current_user.about

    return render_template('admin/settings.html', form=form)


@admin_bp.route('/thought/new', methods=['GET', 'POST'])
@login_required
def new_thought():
    form = ThoughtForm()

    if form.validate_on_submit():
        body = form.body.data
        thought = Thought(body=body)
        db.session.add(thought)
        db.session.commit()
        flash('Thought created.', 'success')
    
        return redirect(url_for('blog.thought'))
    
    return render_template('admin/new_thought.html', form=form)
        

@admin_bp.route('/thought/manage')
@login_required
def manage_thought():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_MANAGE_THOUGHT_PER_PAGE']
    pagination = Thought.query.order_by(Thought.timestamp.desc()).paginate(page, per_page=per_page)
    thoughts = pagination.items

    return render_template('admin/manage_thought.html', page=page, pagination=pagination, thoughts=thoughts)


@admin_bp.route('/thought/<int:thought_id>/edit', methods=['GET', 'POST'])
def edit_thought(thought_id):
    form = ThoughtForm()
    thought = Thought.query.get_or_404(thought_id)
    
    if form.validate_on_submit():
        thought.body = form.body.data
        db.session.commit()
        flash('Thought updated.', 'success')
        return redirect(url_for('blog.thought'))

    form.body.data = thought.body
    return render_template('admin/edit_thought.html', form=form)


@admin_bp.route('/thought/<int:thought_id>/delete', methods=['POST'])
def delete_thought(thought_id):
    thought = Thought.query.get_or_404(thought_id)
    db.session.delete(thought)
    db.session.commit()
    flash('Thought deleted.', 'success')
    return redirect_back()


@admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(
        page, per_page=current_app.config['MYBLOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items

    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        theme = request.files.getlist('image')[0].filename
        body = form.body.data
        category = Category.query.get(form.category.data)
        topic = Topic.query.get(form.topic.data)
        post = Post(title=title, subtitle=subtitle, theme=theme, body=body, category=category, topic=topic)
        # same with:
        # category_id = form.category.data
        # post = Post(title=title, body=body, category_id=category_id)
        db.session.add(post)
        db.session.commit()

        img_list = request.files.getlist('image')
        img_path = current_app.root_path  + '/static/img/' + str(topic.name)
        if img_list[0].filename:

            for f in img_list:
                filename = f.filename
                f.save(os.path.join(img_path, filename))

        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.body = form.body.data
        post.update_time = datetime.utcnow()
        post.category = Category.query.get(form.category.data)
        post.topic = Topic.query.get(form.topic.data)
        db.session.commit()

        img_path = current_app.root_path  + '/static/img/' + str(post.topic.name)
        for f in request.files.getlist('image'):
            filename = f.filename
            f.save(os.path.join(img_path, filename))

        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))

    form.title.data = post.title
    form.subtitle.data = post.subtitle
    form.body.data = post.body
    form.category.data = post.category_id
    form.topic.data = post.topic_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
    filter_rule = request.args.get('filter', 'all')  # 'all', 'unreviewed', 'admin'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment published.', 'success')
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@admin_bp.route('/topic/manage')
@login_required
def manage_topic():
    return render_template('admin/manage_topic.html')


@admin_bp.route('/topic/new', methods=['GET', 'POST'])
@login_required
def new_topic():
    form = TopicForm()
    if form.validate_on_submit():
        name = form.name.data
        image = form.image.data
        theme = image.filename
        category = Category.query.get(form.category.data)
        description = form.description.data
        topic = Topic(name=name, category=category, theme=theme, description=description)
        db.session.add(topic)
        db.session.commit()

        img_path = current_app.root_path  + '/static/img/' + str(topic.name)
        os.mkdir(img_path)  
        image.save(os.path.join(img_path, theme))

        flash('Topic created.', 'success')
        return redirect(url_for('.manage_topic'))
    return render_template('admin/new_topic.html', form=form)


@admin_bp.route('/topic/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_topic(topic_id):
    form = TopicForm()
    topic = Topic.query.get_or_404(topic_id)
    
    if topic.id == 1:
        flash('You can not edit the default topic.', 'warning')
        return redirect(url_for('blog.index'))

    if form.validate_on_submit():
        topic.name = form.name.data
        topic.category = Category.query.get(form.category.data)
        topic.description = form.description.data
        db.session.commit()
        flash('Topic updated.', 'success')
        return redirect(url_for('.manage_topic'))

    form.name.data = topic.name
    form.category.data = topic.category.name
    form.description.data = topic.description
    return render_template('admin/edit_topic.html', form=form)


@admin_bp.route('/topic/<int:topic_id>/delete', methods=['POST'])
@login_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if topic.id == 1:
        flash('You can not delete the default topic.', 'warning')
        return redirect(url_for('blog.index'))

    topic.delete()
    flash('Topic deleted.', 'success')
    return redirect(url_for('.manage_topic'))
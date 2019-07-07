# -*- coding: utf-8 -*-
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint
from flask_login import login_required, current_user

from myblog.extensions import db
from myblog.forms import ThoughtForm, SettingForm, PostForm, CategoryForm, TopicForm, AdminCommentForm, CommentForm
from myblog.models import Post, Category, Topic, Comment, Thought
from myblog.utils import redirect_back


blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(page, per_page=per_page)
    posts = pagination.items

    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/thought')
def thought():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_THOUGHT_PER_PAGE']
    pagination = Thought.query.order_by(Thought.timestamp.desc()).paginate(page, per_page=per_page)
    thoughts = pagination.items

    return render_template('blog/thought.html', thoughts=thoughts, pagination=pagination)

@blog_bp.route('/archive')
def archive():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(page, per_page=100)
    posts = pagination.items

    return render_template('blog/archive.html', posts=posts, pagination=pagination)


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.create_time.desc()).paginate(page, per_page)
    posts = pagination.items

    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/topic/<int:topic_id>')
def show_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(topic).order_by(Post.create_time.desc()).paginate(page, per_page)
    posts = pagination.items

    return render_template('blog/topic.html', topic=topic, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(page, per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed)

        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
        db.session.add(comment)
        db.session.commit()

        if current_user.is_authenticated:  # send message based on authentication status
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')

        return redirect(url_for('.show_post', post_id=post_id))

    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')

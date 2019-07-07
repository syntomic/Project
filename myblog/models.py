# -*- coding: utf-8 -*-

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from myblog.extensions import db


class Admin(db.Model, UserMixin):
    """管理员模型, 存储网页标题, 关于界面, 博客昵称, 管理员用户和密码"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    """类型模型, 存储类型名称, 建立关系属性: 话题, 文章"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    topics = db.relationship('Topic', back_populates='category')
    posts = db.relationship('Post', back_populates='category')
    #links = db.relationship('Link', back_populates='category')


class Topic(db.Model):
    """话题模型, 存储话题名称, 描述, 及其类型, 建立关系属性: 类型, 文章"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    theme = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(255), unique=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    category = db.relationship('Category', back_populates='topics')
    posts = db.relationship('Post', back_populates='topic')

    def delete(self):
        """删除话题以后,其下的文章将会成为第一个话题下的文章"""
        first_topic = Topic.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.topic = first_topic

        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    """文章模型, 存储文章的标题, 副标题, 内容, 创建时间和修改时间, 是否可评论, 及其类型和话题, 建立关系属性: 类型, 话题, 评论"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    subtitle = db.Column(db.String(255))
    theme = db.Column(db.String(60))
    body = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, index = True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    category = db.relationship('Category', back_populates='posts')
    topic = db.relationship('Topic', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')


class Comment(db.Model):
    """评论模型, 存储作者, 邮箱, 是否来自管理员, 是否审查过, 创建时间, 及其文章, 回复, 建立关系属性: 文章, 回复(邻接列表关系)"""
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    #site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
  
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    
    post = db.relationship('Post', back_populates='comments')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')


class Thought(db.Model):
    """想法模型, 存储想法和时间"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
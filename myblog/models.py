# -*- coding: utf-8 -*-

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from myblog.extensions import db

class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Admin(db.Model, UserMixin):
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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    topics = db.relationship('Topic', back_populates='category')
    posts = db.relationship('Post', back_populates='category')
    links = db.relationship('Link', back_populates='category')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    category_id = db.Column(db.String(20), db.ForeignKey('category.id'))
    
    category = db.relationship('Category', back_populates='topics')
    posts = db.relationship('Post', back_populates='topic')

    def delete(self):
        """posts of deleted topic will become first_topic"""
        first_topic = Topic.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.topic = first_topic

        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    subtitle = db.Column(db.String(255))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, index = True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')

    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    topic = db.relationship('Topic', back_populates='posts')
    
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
  
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates="links")
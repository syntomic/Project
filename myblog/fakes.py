# -*- coding: utf-8 -*-

import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from myblog.extensions import db
from myblog.models import Admin, Thought, Category, Topic, Post, Comment, Link

fake = Faker()

def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='Cleanlog',
        name='Syntomic',
        about='just for share my knowledge..,'
    )

    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()

def fake_thoughts(count=20):
    for i in range(count):
        thought = Thought(
            body=fake.sentence(),
            timestamp=fake.date_time_this_year())

        db.session.add(thought)

    db.session.commit()

def fake_categories():
    Math = Category(name="Math")
    Computer = Category(name="CS")
    Physics = Category(name="Physics")
    Others = Category(name="Others")

    db.session.add_all([Math, Computer, Physics, Others])
    db.session.commit()
    

def fake_topics(count=10):
    for i in range(count):
        topic = Topic(
            name=fake.word(),
            category=Category.query.get(random.randint(1, Category.query.count()))
            )
        db.session.add(topic)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    

def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            subtitle=fake.text(255),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            topic = Topic.query.get(random.randint(1, Topic.query.count())),
            create_time=fake.date_time_this_decade(),
            update_time=fake.date_time_this_decade(),
            can_comment=True
        )

        db.session.add(post)

    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # unreviewed comments
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # from admin
        comment = Comment(
            author='Syntomic',
            email='mima@example.com',
            site='example.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    # replies
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    db.session.commit()


def fake_links(count=10):

    for i in range(count):
        link = Link(
            name = fake.word(), 
            category = Category.query.get(random.randint(1, Category.query.count())),
            url = '#'
        )
        db.session.add(link)

    db.session.commit()
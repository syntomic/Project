# -*- coding: utf-8 -*-

import os

import click
from flask import Flask

from cleanlog.blueprints.blog import blog_bp
from cleanlog.extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment
from cleanlog.models import Message, Category, Post, Comment, Link
from cleanlog.settings import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('cleanlog')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_template_context(app)
    register_commands(app)

    return app


def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog_bp)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Message=Message, Post=Post, Category=Category, Comment=Comment)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()

        return dict(categories=categories, links=links)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue', abort=True)
            db.drop_all()
            click.echo('Drop tables')

        db.create_all()
        click.echo('Initialized databases.')

    @app.cli.command()
    @click.option('--message', default=20, help='Quantity of messages, default is 20.')
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(message, category, post, comment):
        """Generate fake datas."""
        from cleanlog.fakes import fake_messages, fake_categories, fake_comments, fake_links, fake_posts

        db.drop_all()
        db.create_all()

        click.echo('Generating %d messages...' % message)
        fake_messages(message)

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')

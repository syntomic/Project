# -*- coding: utf-8 -*-

import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Linux
prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    SSL_DISABLED = True

    MYBLOG_THOUGHT_PER_PAGE = 15
    MYBLOG_ARCHIVE_PER_PAGE = 10
    MYBLOG_POST_PER_PAGE = 10
    MYBLOG_MANAGE_THOUGHT_PER_PAGE = 20
    MYBLOG_MANAGE_POST_PER_PAGE = 15
    MYBLOG_COMMENT_PER_PAGE = 15
    MYBLOG_SLOW_QUERY_THRESHOLD = 1


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SSL_DISABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
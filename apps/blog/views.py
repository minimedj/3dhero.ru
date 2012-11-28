# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, render_template, url_for
from apps.blog.models import Post

mod = Blueprint(
    'blog',
    __name__,
    url_prefix='/blog',
    template_folder='templates'
)

@mod.route('/')
def index():
    posts = Post.query().order(-Post.created)
    return render_template(
        'blog/index.html',
        posts=posts
    )

@mod.route('/<int:key_id>/', endpoint='post')
def get_post(key_id):
    post = Post.retrieve_by_id(key_id)
    if not post:
        return redirect(url_for('blog.index'))
    return render_template(
        'blog/post.html',
        post=post
    )
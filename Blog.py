from flask import Flask, render_template, flash, redirect, url_for, abort, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from MyForms import *


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/blog'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}, {self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


@app.route("/")
def layout():
    return render_template('layout.html')
@app.route("/home")
def home():
    posts = Post.query.all()
    count = Post.query.count()
    return render_template('home.html', posts=posts, count=count)

@app.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = CreatePostForm()
    if form.validate():
        current_user = User.query.first()
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create.html', form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    print(post.content, post.title)
    #current_user = User.query.first()
    # if post.author != current_user:
    #     abort(403)
    form = CreatePostForm()
    if form.validate():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your Post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create.html', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete")
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    #current_user = User.query.first()
    # if post.author != current_user:
    #     abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been Deleted', 'success')
    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Post(FlaskForm):
    title = StringField('Blog Title', validators=[DataRequired()])
    subtitle = StringField('Blog Subtitle', validators=[DataRequired()])
    author = StringField('Your Name', validators=[DataRequired()])
    img_url = StringField('Blog img_url', validators=[DataRequired()])
    body = CKEditorField('Blog Body', validators=[DataRequired()])
    create_button = SubmitField('Create Post')

    def to_dict(self):
        dictionary = {field_name: value for (field_name,value) in self.data.items()}
        dictionary.pop("create_button")
        dictionary.pop("csrf_token")
        return dictionary

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary

with app.app_context():
    db.create_all()


def to_dict(data):
    dictionary = {key:val for (key,val) in data.items()}
    return dictionary

@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = BlogPost.query.all()
    # posts = []
    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/show-post/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    # requested_post = "Grab the post from your database"
    requested_post = BlogPost.query.get(post_id)
    if requested_post is None:
        return jsonify({'error': 'Requested post not found'}, 404)
    return render_template("post.html", post=requested_post)




# TODO: add_new_post() to create a new blog post
@app.route('/create-post', methods=['GET', 'POST'])
def add_new_post():
    form = Post()
    if request.method == 'POST':
        form_dict = form.to_dict()
        curr_date = date.today().strftime("%B %d, %Y")
        form_dict['date'] = f'{curr_date}'
        db.session.add(BlogPost(**form_dict))
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template('make-post.html', form=form)


# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    if requested_post is None:
        return jsonify({'error': 'Requested post not found'}, 404)

    form = Post(
        title=requested_post.title,
        date=requested_post.date,
        subtitle=requested_post.subtitle,
        author=requested_post.author,
        img_url=requested_post.img_url,
        body=requested_post.body,
    )

    if request.method == 'POST':
        form_dict = form.to_dict()
        requested_post.date = form_dict['date']
        requested_post.subtitle = form_dict['subtitle']
        requested_post.author = form_dict['author']
        requested_post.img_url = form_dict['img_url']
        requested_post.body = form_dict['body']
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form)

# TODO: delete_post() to remove a blog post from the database

@app.route('/delete-post/<int:post_id>', methods=['GET'])
def delete_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    if requested_post is None:
        return jsonify({'error': 'Requested post not found'}, 404)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)


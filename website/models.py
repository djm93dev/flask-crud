from email.policy import default
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# User model

class User(db.Model, UserMixin):
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    bio = db.Column(db.String(400))
    website = db.Column(db.String(150))
    following = db.Column(db.String(150), default='0,')
    # One-to-many
    posts = db.relationship('Post', primaryjoin="User.username==Post.name", backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)
    channels = db.relationship('Channel', foreign_keys='Channel.user_name', backref='user')
    
    def __repr__(self):
        return f'<User {self.username}>'

    
#Channel

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    # Many to the one
    user_name = db.Column(db.String, db.ForeignKey('user.username'))
    followers = db.Column(db.Integer, db.ForeignKey('user.username'))


    def __repr__(self):
        return f'<Channel {self.name}>'


#Posts

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    youtube_id = db.Column(db.String(20), default='')
    embed = db.Column(db.String(500))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String, db.ForeignKey('user.username'))
    channel = db.Column(db.String, db.ForeignKey('channel.name'))
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('Like', backref='post', passive_deletes=True)

#Comments

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)

#Likes

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

#Image upload

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('user.username', ondelete='CASCADE'), nullable=False)

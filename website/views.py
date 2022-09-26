from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response
from flask_login import login_required, current_user
import datetime
from .models import Post, User, Comment, Like, Img, Channel
from . import db
from werkzeug.utils import secure_filename
from string import Template


views = Blueprint('views', __name__)

HTML_TEMPLATE = Template("""
  <iframe src="https://www.youtube.com/embed/${youtube_id}" width="853" height="480" frameborder="0" allowfullscreen></iframe>""")



@views.route('/')
@views.route('/home')
@login_required
def home():
    dt = datetime.datetime.utcnow()
    posts = Post.query.all()
    channels = Channel.query.all()
    
    channel_id = []
    for channel in channels:
        channel_id.append(channel.id)


    channel_name = Channel.query.filter_by(name=current_user.username).first()

    # check to see if current_user.username is in the channel table
    if channel_name is None:
            flash("We noticed you havent created a channel yet... you can create your channel on the edit profile page", category='error')
            pass


    return render_template('home.html', user=current_user, posts=posts, dt=dt, channels=channels, channel_id=channel_id, channel_name=channel_name)


@views.route('/videos/<vid>')
def videos(vid):
    return HTML_TEMPLATE.substitute(youtube_id=vid)


@views.route('/profile/<username>' , methods=['GET'])
@login_required
def profile(username):
    if username != current_user.username:
        flash('You can only view your own profile.', category='error')
        return redirect(url_for('views.home'))
    posts = Post.query.all()
    user = User.query.filter_by(username=username).first()
    

    if not user:
        flash('User not found', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template('profile.html', user=current_user, posts=posts, username=username)
    

@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    youtube_id = ''
    if request.method == 'POST':
        text = request.form.get('text')
        embed = request.form.get('embed')

        # if embded contains youtube link, extract the video id
        if 'youtube.com' in embed:
            youtube_id = embed.split('v=')[1]
            prefix = embed.split('v=')[0]
            embed = prefix
            



        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id, embed=embed, name=current_user.username, channel=current_user.username, youtube_id=youtube_id)
            db.session.add(post)
            db.session.commit()
            flash('Post created', category='success')
            return redirect(url_for('views.home'))
    
    return render_template('create_post.html', user=current_user)

@views.route('/delete-post/<id>')
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Post not found', category='error')

    elif current_user.id != post.author:
        flash('You cannot delete this post', category='error')

    else: 
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category='success')

    return redirect(url_for('views.home'))


@views.route('/following', methods=['GET'])
@login_required
def following():
    user = User.query.filter_by(username=current_user.username).first()
    posts = Post.query.all()
    following = User.query.filter_by(following=current_user.following).all()

    return render_template('following.html', user=user, posts=posts, following=following)
    

@views.route('/posts/<username>')
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()
    channels = Channel.query.filter_by(id=user.id)

    if not user:
        flash('User not found', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    id = user.id

    
    return render_template('posts.html', user=current_user, posts=posts, username=username, id=id)



@views.route('/create-comment/<post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty', category='error')
    else:    
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment created', category='success')
            return redirect(url_for('views.home'))
        else:
            flash('Post not found', category='error')    
    return redirect(url_for('views.home'))



@views.route('/delete-comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment not found', category='error')

    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You cannot delete this comment', category='error')

    else: 
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted', category='success')

    return redirect(url_for('views.home'))
    

@views.route('/like-post/<post_id>' , methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({"error": "Post not found"}, 400)

    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({'likes': len(post.likes), 'liked': current_user.id in map(lambda x: x.author, post.likes)})

@views.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype, username=current_user.username)
    # grab the first img the in the db by username
    username = current_user.username
    img_old = Img.query.filter_by(username=username).first()
    if img_old:
        db.session.delete(img_old)
        db.session.commit()
    
    db.session.add(img)
    db.session.commit()

    flash('Img Uploaded!', category='success')

    return redirect(url_for('views.home'))

@views.route('/edit-profile')
def upload_image():
    return render_template('edit_profile.html', user=current_user)


@views.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)


@views.route('/profile-image/<username>')
def img_get(username):
    img = Img.query.filter_by(username=username).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)


@views.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():
    user = User.query.filter_by(username=current_user.username).first()
    username = request.form.get('username')
    bio = request.form.get('bio')
    website = request.form.get('website')
    email = request.form.get('email')
    # set channel_id and channel_name to user id and username
    channel = Channel(id=user.id, name=user.username)
    channel_id = user.id
    channel_name = user.username
    channel.user_name = user.username
    channel.followers = current_user.username

    channel_old = Channel.query.filter_by(id=channel_id).first()
    if channel_old:
        db.session.delete(channel_old)
        db.session.commit()

    if channel_id and channel_name:
        channel.id = channel_id
        channel.name = channel_name

    if username:
        user.username = username
    #  update fields that are filled in
    if email:
        user.email = email
    if username:
        user.username = username
    if bio:
        user.bio = bio
    if website:
        user.website = website

    db.session.add(channel)
    db.session.add(user)
    db.session.commit()
    flash('Profile updated', category='success')

    return redirect(url_for('views.home'))


@views.route('/follow/channel/<id>', methods=['GET', 'POST'])
@login_required
def follow_channel(id):
    channel = Channel.query.filter_by(id=id).first()
    user = User.query.filter_by(username=current_user.username).first()
    post = Post.query.filter_by(author=id).first()
    newfollow = post.author

    
    # if newfollow not in user.following:
    if str(newfollow) not in user.following:
        user.following += (str(newfollow)) + ','
        db.session.commit()
        flash('You are now following this channel', category='success')
        if request.referrer == 'http://127.0.0.1:5000/following':
            return redirect(url_for('views.following'))
        else:
            return redirect(url_for('views.home'))
        


    # delete the newfollow from the following list if it is already in the list
    else:
        if str(newfollow) in user.following:
            user.following = user.following.replace(str(newfollow), "").replace(",,", ",")
            db.session.commit()
            flash('You are no longer following this channel', category='success')
            if request.referrer == 'http://127.0.0.1:5000/following':
                return redirect(url_for('views.following'))
            else:
                return redirect(url_for('views.home'))
            

    if not channel:
        flash('Channel not found', category='error')
        
      
        db.session.add(user)    
        db.session.commit()
        flash('Unfollowed', category='success')
        if request.referrer == 'http://127.0.0.1:5000/following':
            return redirect(url_for('views.following'))
        else:
            return redirect(url_for('views.home'))    
 
    else:
        if  current_user.username not in channel.followers:
            channel.followers = (str([channel.followers, current_user.username])).replace('[', '').replace(']', '').replace("'", '').replace('"', '').replace(' ', '')
        
        db.session.add(channel)
        db.session.commit()
        flash('You are now following this channel', category='success')
        if request.referrer == 'http://127.0.0.1:5000/following':
            return redirect(url_for('views.following'))
        else:
            return redirect(url_for('views.home'))
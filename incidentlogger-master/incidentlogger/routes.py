import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request,abort
from incidentlogger import app, db, bcrypt
from incidentlogger.forms import RegistrationForm, LoginForm, IncidentForm, GameForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, PostForm
from incidentlogger.models import User, Incident, Game, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


systems = ['PS4', 'XBOX1', 'Switch']
categories = []

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@app.route("/ghome")
def ghome():
    page = request.args.get('page', 1, type=int)
    posts = Game.query.order_by(Game.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('ghome.html', posts=posts)


@app.route("/blhome")
def blhome():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('blhome.html', posts=posts)    

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password, priv=form.admin.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Try again', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/game/create", methods=['GET', 'POST'])
@login_required
def game():
    if current_user.priv != True:
        abort(403)
    form = GameForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_game_pic(form.picture.data)
            post.image_file = picture_file
        post = Game(system= form.system.data,title=form.title.data, descript=form.descript.data ,tags=form.tags.data, rank=form.rank.data, date_released=form.date_released.data, author=current_user, image_file = form.picture.data  )
        db.session.add(post)
        db.session.commit()
        flash('Your game has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('game.html', title='Post Game',
                           form=form, systems=systems, legend='Post Game')

@app.route("/game/<int:game_id>")
def game_post(game_id):
    post = Game.query.get_or_404(game_id)
    form = GameForm()
    if current_user.priv != True:
        abort(403)
    image_file = url_for('static', filename='game_cover/' + post.image_file)
    return render_template('game_post.html', image_file = image_file, title= post.title, form=form,post=post)


@app.route("/game/<int:game_id>/update", methods=['GET','POST'])
@login_required
def game_update(game_id):
    post = Game.query.get_or_404(game_id)
    if post.author != current_user:
        abort(403)
    form = GameForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_game_pic(form.picture.data)
            post.image_file = picture_file
        post.title = form.title.data
        post.descript = form.descript.data
        post.system = form.system.data
        post.tags = form.tags.data
        post.rank = form.rank.data
        post.date_released = form.date_released.data
        db.session.commit()
        flash('Your Post has been updated', 'success')
        return redirect(url_for('game_post', game_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.descript.data = post.descript
        form.system.data = post.system
        form.tags.data = post.tags
    image_file = url_for('static', filename='game_cover/' + post.image_file)
    return render_template('game.html', title='Update Game',
                           form=form, image_file=image_file ,legend='Update Game')


@app.route("/game/<int:game_id>/delete", methods=['POST'])
@login_required
def game_delete(game_id):
    post = Game.query.get_or_404(game_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted', 'success')
    return redirect(url_for('home'))

@app.route("/incident/create", methods=['GET', 'POST'])
@login_required
def incident():
    form = IncidentForm()
    if form.validate_on_submit():
        post = Incident(contact= current_user.username ,category= form.category.data,title=form.title.data, content=form.content.data, state='Inactive' ,tags=form.tags.data , current_assignee=' ' , history="Created by " + current_user.username,author=current_user)
        if form.category.data not in  categories:
            categories.append(form.category.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('incident.html', title='New Post',
                           form=form, categories=categories ,legend='New Post')


@app.route("/incident/<int:incident_id>")
def incident_post(incident_id):
    post = Incident.query.get_or_404(incident_id)
    return render_template('incident_post.html', title= post.title, post=post)

@app.route("/incident/<int:incident_id>/update", methods=['GET','POST'])
@login_required
def incident_update(incident_id):
    post = Incident.query.get_or_404(incident_id)
    #if post.author != current_user:
    #    abort(403)
    form = IncidentForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.tags = form.tags.data
        post.history = post.history + '\n Updated by ' + current_user.username
        post.state = 'Active'
        post.current_assignee = current_user.username
        if form.category.data not in  categories:
            categories.append(form.category.data)
        db.session.commit()
        flash('Your Post has been updated', 'success')
        return redirect(url_for('incident_post', incident_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
        form.tags.data = post.tags
    return render_template('incident.html', title='Update Incident',
                           form=form, legend='Update Incident')


@app.route("/incident/<int:incident_id>/delete", methods=['POST'])
@login_required
def incident_delete(incident_id):
    post = Incident.query.get_or_404(incident_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, rank=form.rank.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/post/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_game_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/game_cover', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/user/game/<string:username>")
def user_games(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Game.query.filter_by(author=user)\
    .order_by(Game.date_posted.desc())\
    .paginate(page=page, per_page=5)
    return render_template('contact_posts.html', posts=posts, user=username)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

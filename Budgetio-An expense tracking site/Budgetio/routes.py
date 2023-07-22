import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from Budgetio import app, db, bcrypt
from Budgetio.forms import RegistrationForm, LoginForm, Trackerform, Sorter, Updateuser, Write_a_post, delete_me
from Budgetio.Models import User, Post, User_data
from flask_login import login_user,current_user,logout_user,login_required


@app.route('/')
@app.route('/home')
def nice():
    datab = User
    datac = Post
    datad = User_data
    return render_template("layout.html", current_url="/home",alt_current_url='/',datab=datab,datac=datac,datad=datad)

@app.route('/blogpage')
def blogpage():
    ROWS_PER_PAGE = 5
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template("blog_page.html", posts=posts)

@app.route('/all_your_posts')
@login_required
def user_blogpage():
    ROWS_PER_PAGE = 5
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template("blog_page.html", posts=posts)

@app.route('/p')
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route('/articles')
def articles():
    return render_template("articles.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('nice'))

@app.route('/contact')
def contact():
    return render_template("contact_us.html")

@app.route('/a1')
def article1():
    return render_template("Article_1.html")

@app.route('/a2')
def article2():
    return render_template("Article_2.html")

@app.route('/a3')
def article3():
    return render_template("Article_3.html")

@app.route('/a4')
def article4():
    return render_template("Article_4.html")

@app.route('/a5')
def article5():
    return render_template("Article_5.html")

@app.route('/r', methods=["POST","GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('nice'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account for {form.username.data} has been created! Please Login in!')
        return redirect(url_for('login'))

    return render_template("registration.html", title='Register', form=form)


@app.route('/l', methods=["POST","GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('nice'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user,remember=form.remember.data)
                flash(f'Welcome Back! {form.username.data}!')
                return redirect(url_for('blogpage'))
            else:
                flash(f'Login Unsuccessful! Please check Credentials!')

    return render_template("login.html", title='Login', form=form)



@app.route('/t', methods=["POST","GET"])
def tracker():
    if not current_user.is_authenticated:
        return redirect(url_for('nice'))
    else:
        form = Trackerform()
        form_f = Sorter()
        if form_f.month.data:
            month_f = form_f.month.data
        else:
            month_f = 'January'

        datab = User_data
        if form.submit.data and form.validate:
            if form.type.data == 'Income':
                new_data = User_data(month=form.month.data, type=form.type.data,description=form.description.data, expense=form.expense.data, owner=current_user)
                db.session.add(new_data)
                db.session.commit()
                flash(f'Entry Added')
                return redirect(url_for('tracker'))
            elif form.type.data == 'Expenditure':
                new_data = User_data(month=form.month.data, type=form.type.data,description=form.description.data, expense=(-1 *(form.expense.data)), owner=current_user)
                db.session.add(new_data)
                db.session.commit()
                flash(f'Entry Added')
                return redirect(url_for('tracker'))
        if form_f.submit1.data and form_f.validate:
            month_f = form_f.month.data

    return render_template("Tracker.html", title='Tracker',form=form, form_f=form_f, datab=datab, month_f=month_f)


@app.route('/entries/delete/<this>')
@login_required
def delete(this):
    trash=User_data.query.get_or_404(this)
    db.session.delete(trash)
    db.session.commit()
    return redirect(url_for('tracker'))

@app.route('/entries/edit/<this>', methods=["POST","GET"])
@login_required
def edit(this):
    entry=User_data.query.get_or_404(this)
    form = Trackerform()
    if form.validate_on_submit():
        entry.month=form.month.data
        if form.type.data == 'Income':
            entry.type = form.type.data
            entry.expense = abs(form.expense.data)
        elif form.type.data == 'Expenditure':
            entry.type = form.type.data
            entry.expense = -1*abs(form.expense.data)
        entry.description=form.description.data
        db.session.add(entry)
        db.session.commit()
        flash(f'Entry Updated')
        return redirect(url_for('tracker'))
    form.month.data = entry.month
    form.description.data = entry.description
    form.expense.data = entry.expense
    return render_template("editor.html", title='Edit Entry', form=form)




def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile pics', picture_fn)
    output_size = (125,125)
    i= Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/user_profile', methods=["POST","GET"])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('nice'))
    else:
        form = Updateuser()
        if form.validate_on_submit():
            if form.pic.data:
                picture_file = save_picture(form.pic.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash(f'Your profile information is updated successfully')
            return redirect(url_for('profile'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
    image_file = url_for('static', filename='profile pics/'+ current_user.image_file)
    return render_template("profile_page.html", title='profile page', form=form, image_file=image_file)

@app.route('/chart', methods=["POST","GET"])
def chart():
    if not current_user.is_authenticated:
        flash(f'Please log in to view charts!')
        return redirect(url_for('blogpage'))
    datab=User_data
    form_f=Sorter()
    if form_f.month.data:
        month_f = form_f.month.data
    else:
        month_f = 'January'
    if form_f.submit1.data and form_f.validate:
        month_f = form_f.month.data
    return render_template("chart.html",datab=datab,form_f=form_f,month_f=month_f)


@app.route('/write_post',methods=["POST","GET"])
def write_post():
    form = Write_a_post()
    if not current_user.is_authenticated:
        return redirect(url_for('nice'))
    else:
        if form.validate_on_submit():
            new_post = Post(title=form.headline.data, content=form.description.data, author=current_user, )
            db.session.add(new_post)
            db.session.commit()
            flash(f'You post has been published!')
            return redirect(url_for('blogpage'))

    return render_template("write_post.html", form=form, legend='Write a Post', value="Publish" )

@app.route('/posts/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title = post.title,post=post)



@app.route('/posts/<int:post_id>/update',methods=["POST","GET"])
@login_required
def update_post(post_id):
    string_id = str(post_id)
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = Write_a_post()
    if form.validate_on_submit():
        post.title = form.headline.data
        post.content = form.description.data
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form.headline.data=post.title
        form.description.data = post.content
    return render_template("write_post.html", title = 'Update Post',post=post,form=form, legend='Update Post', current_path="/posts/"+string_id+"/update")



@app.route('/posts/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!')
    return redirect(url_for('blogpage'))

@app.route('/killme',methods=["POST","GET"])
@login_required
def killme():
    form = delete_me()
    if form.validate_on_submit():
        if form.delete_posts.data == True:
            delete_user_posts()
            flash(f'All your posts has been deleted!')
        if form.delete_entries.data == True:
            delete_entries()
            flash(f'All your entries has been deleted!')
        if form.delete_account.data == True:
            delete_account()
        if form.delete_posts.data == False and form.delete_entries.data == False and form.delete_account.data == False:
            flash(f'Select something for deletion')
        return redirect(url_for('nice'))
    return render_template("kill_me.html",form=form)

def delete_user_posts():
    posts = Post.query.filter_by(author=current_user).all()
    if posts:
        for post in posts:
            db.session.delete(post)
            db.session.commit()
    else:
        pass

def delete_entries():
    entries = User_data.query.filter_by(owner=current_user).all()
    if entries:
        for entry in entries:
            db.session.delete(entry)
            db.session.commit()
    else:
        pass

def delete_account():
    user = User.query.get_or_404(current_user.id)
    if user.id != current_user.id:
        abort(403)
    delete_entries()
    delete_user_posts()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been deleted! Bye Bye!')

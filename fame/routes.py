import os
import sys
import secrets
from datetime import date
from PIL import Image
from fame.Rank import get_matchup,rank_matchup,starting_points
from flask import render_template, url_for, flash, redirect, request, jsonify
from fame import app, db, bcrypt
#from fame import mail
from fame.forms import (SearchBar,AddCategory,AddNoun,RegistrationForm,LoginForm,EditAccount,
                    RequestResetForm, ResetPasswordForm)
from fame.models import Category,CategoryRequest,Noun,NounRequest,User
from flask_login import login_user, current_user, logout_user, login_required
from fame.decorators import admin_required
from wtforms.validators import  ValidationError
from sqlalchemy import asc,desc
import shutil
from fame import search_engine
from fame.search_engine import *
from fame.functions import *

if 'restart' in sys.argv:
    drop_all()
    exit()

#Name, function name for redirect
function_cat_dict={
    'Leaderboard':'category_leaderboard',
    'Game':'category_game'
    #'Matchup':'matchup',
    #'Add Item':'item_add'
}



@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    popular_categories=get_popular_categories()
    image_files=get_category_images(popular_categories)
    return render_template('home.html',pagename='Home',search=search,categories=popular_categories,image_files=image_files)

@app.route('/search/<search_input>',methods=['GET','POST'])
def search(search_input,search_size=16):
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    categories=search_engine.search_site(search_input,Category)
    image_files=get_category_images(categories)
    return render_template('search.html',search=search,search_input=search_input,categories=categories[:search_size],image_files=image_files)

@app.route('/add_category_request',methods=['GET','POST'])
def add_category_request():
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    form=AddCategory()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            category_request = CategoryRequest(name=form.name.data,image_file=picture_file)
        else:
            category_request = CategoryRequest(name=form.name.data)
        db.session.add(category_request)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_category_request.html',search=search,form=form)

@app.route("/<category_url>/home", methods=['GET','POST'])
def category(category_url):
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    category= Category.query.filter_by(name=category_url.replace("_"," ")).first()
    #TEMPORARY
    if True:
        return redirect(url_for('category_leaderboard',category_url=category_url))
    #ranks=get_noun_points_rank_array(category)
    if category:
        return render_template('category.html',pagename=category.name +' Home ',search=search, category=category,function_cat_dict=function_cat_dict)
    else:
        return redirect(url_for('home'))

@app.route("/<category_url>/leaderboard", methods=['GET','POST'])
def category_leaderboard(category_url):
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    category=Category.query.filter_by(name=category_url.replace('_',' ')).first()
    image_files=get_noun_images(category.nouns,category.name)
    if category:
        return render_template('category_leaderboard.html',pagename=category.name +' Leaderboard ',search=search, category=category,function_cat_dict=function_cat_dict,image_files=image_files,
        enumerated=enumerate(category.nouns),category_url=category_url)
    else:
        return redirect(url_for('home'))

@app.route("/<category_url>/game", methods=['GET','POST'])
def category_game(category_url):

    category=  Category.query.filter_by(name=category_url.replace('_',' ')).first()
    if category== None:
        return redirect(url_for('home'))
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    if len(category.nouns)>=2:
        matchup=get_matchup(category.name.replace(' ',"_"))
    else:
        flash('Error: Not enough nouns')
        return redirect(url_for('home'))
    return render_template('category_game.html',pagename='Game',search=search,category=category,matchup=matchup,function_cat_dict=function_cat_dict)

@app.route("/get_category_url/<category_id>", methods=['GET','POST'])
def get_category_url(category_id):
    category_url=Category.query.get(category_id).name.replace(' ','_')
    results={'category_url':category_url}
    return results

@app.route("/<category_url>/noun_request", methods=['GET','POST'])
def category_add_noun_request(category_url):
    category=Category.query.filter_by(name=category_url.replace('_',' ')).first()
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    form=AddNoun()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data,category.name,KEY='REQUEST_NOUN')
            noun_request =NounRequest(name=form.name.data,description=form.description.data,category_name=category.name,image_file=picture_file)
        else:
            noun_request = NounRequest(name=form.name.data,description=form.description.data,category_name=category.name)
        db.session.add(noun_request)
        db.session.commit()
        return redirect(url_for('category_leaderboard',category_url=category_url))
    return render_template('add_noun_request.html',search=search,form=form,category=category,category_url=category_url,function_cat_dict=function_cat_dict)

@app.route('/game_results',methods=['GET','POST'])
def game_results():
    if request.method == 'POST':
        try:
            current_user.all_time_matchups_played +=1
            db.session.commit()
        except Exception as e:
            print(e)
        data= request.get_json()


        winner=data[0]['winner']
        loser=data[1]['loser']
        rank_matchup(winner,loser,data[2]['category_url'])
        results={'processed':'true'}
        return results

@app.route('/matchup', methods=['GET','POST'])
def matchup():
    if request.method == 'POST':
        data=request.get_json()
        matchup= get_matchup(data[0]['category_url'])
        results={
            'noun1_id':matchup[0].noun_id,
            'noun1_name':matchup[0].name,
            'noun1_image':url_for('static',filename='categories/'+data[0]['category_url'].replace('_'," ")+'/images/'+matchup[0].image_file),
            'noun2_id':matchup[1].noun_id,
            'noun2_name':matchup[1].name,
            'noun2_image':url_for('static',filename='categories/'+data[0]['category_url'].replace('_'," ")+'/images/'+matchup[1].image_file),
            'category_url':data[0]['category_url']
        }
        return jsonify(results)

'''
@app.route("/category_js_redirect", methods=['GET','POST'])
def category_js_redirect():

    if request.method == 'POST':
        data=request.get_json()
        category_name=data[0]['name']
        print('REDIRECTING')
        return redirect(url_for('category',category_url=category_name.replace(' ','_')))
'''

#USER
#USER
#USER
@app.route("/register", methods=['GET', 'POST'])
def register():
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        try:
            user = User(name=form.username.data, email=form.email.data, password=hashed_password,date_joined=date.today())
        except Exception as e:
            print(e)
            flash('Internet Connection Problem Possible')
            return redirect(url_for('home'))
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('user/register.html', title='Register',search=search, form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
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
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('user/login.html', title='Login',search=search ,form=form)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account/<user_id>", methods=['GET', 'POST'])
@login_required
def account(user_id):
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    try:
        user= User.query.get(user_id)
    except:
        flash('Account Does Not Exist')
        return url_for('home')
    return render_template('user/account.html',search=search,user=user,current_user=current_user)

@app.route("/account/<user_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_account(user_id):
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    try:
        user= User.query.get(user_id)
    except:
        flash('Account Does Not Exist')
        return url_for('home')
    form=EditAccount()
    if form.validate_on_submit():
        user.name=form.name.data
        flash('Username Changed Successfully')
        return redirect(url_for('account',user_id=user_id))
    if request.method=='GET':
        form.name.data=user.name
    return render_template('user/edit_account.html',search=search,user=user,current_user=current_user,form=form)

'''
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    form = RequestResetForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent')
        return redirect(url_for('login'))

    return render_template('user/reset_request.html',form=form,search=search)

'''

@app.route("/reset_password/no_token", methods=['GET', 'POST'])
def reset_password_no_token():
    flash('Email Service No Longer Supported')
    return redirect(url_for('home'))
    


'''
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('search',search_input=search.content.data))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token')
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    return render_template('user/reset_password.html',form=form,search=search)
'''

#ADMIN
#ADMIN
#ADMIN

@app.route("/admin", methods=['GET','POST'])
@login_required
@admin_required
def admin():
    print(current_user.name)
    #if current_user.is_admin==False:
    #    return redirect(url_for('home'))
    #ADMIN VALIDATION
    return render_template('admin/admin.html',pagename='Admin')

def get_category_images(categories,key=None):
    category_id__image_file={}
    for category in categories:
        if not key:
            category_id__image_file[category.category_id] = url_for('static',filename='categories/'+category.name+'/images'+'/'+category.image_file)
        #Use for request category
        elif key=='REQUEST':
            category_id__image_file[category.category_id] = url_for('static',filename='category_request_images/'+category.image_file)
        else:
            raise Exception('Not a key for (get_category_images)')
    return category_id__image_file

@app.route("/admin/category_requests", methods=['GET','POST'])
@login_required
@admin_required
def admin_category_requests():
    form=AddCategory()
    category_requests=CategoryRequest.query.all()
    image_files=get_category_images(category_requests,key='REQUEST')
    return render_template('admin/category_requests.html',categories=category_requests,image_files=image_files)

@app.route("/admin/deny_category_request/<category_request_id>", methods=['GET','POST'])
@login_required
@admin_required
def admin_deny_category_request(category_request_id):
    category_request=CategoryRequest.query.get(category_request_id)
    try:
        if category_request.image_file !='../images/default.jpg':
            os.remove(os.path.join(app.root_path,'static',"category_request_images",category_request.image_file))
    except: Exception(f'File {category_request.image_file} no longer exists')
    db.session.delete(category_request)
    db.session.commit()
    return redirect(url_for('admin_category_requests'))

@app.route("/admin/accept_category_request/<category_request_id>", methods=['GET','POST'])
@login_required
@admin_required
def admin_accept_category_request(category_request_id):
    category_request= CategoryRequest.query.get(category_request_id)
    try:
        add_category(category_request.name,category_request.image_file,KEY='REQUEST')
    except Exception as e:
        print(e)
        print('Can\'t add this category')
        flash('Can\'t add this category')
        return redirect(url_for('admin_category_requests'))
    return redirect(url_for('admin_deny_category_request',category_request_id=category_request.category_id))

@app.route("/admin/edit_category_request/<category_request_id>", methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_category_request(category_request_id):
    form = AddCategory()
    category_request=CategoryRequest.query.get(category_request_id)

    if form.validate_on_submit():
        category_request.name=form.name.data
        if form.picture.data:
            #Check that photo is not default now
            if category_request.image_file != '../images/default.jpg':
                os.remove(os.path.join(app.root_path,'static',"category_request_images",category_request.image_file))
            picture_file = save_picture(form.picture.data)
            category_request.image_file = picture_file
        db.session.commit()
        return redirect(url_for('admin_accept_category_request',category_request_id=category_request.category_id))
    elif request.method == 'GET':
        form.name.data = category_request.name
        form.picture.data=category_request.image_file
    return render_template('admin/edit_category_request.html',category=category_request,form=form)

@app.route("/admin/all_categories",methods=['GET','POST'])
@app.route("/admin/all_categories/<sort_by>", methods=['GET','POST'])
@login_required
@admin_required
def admin_all_categories(sort_by='.ID'):
    search=SearchBar()
    if search.validate_on_submit():
        return redirect(url_for('admin_all_categories',sort_by=search.content.data))
    all_categories=Category.query.all()
    categories=search_site(sort_by,Category)
    image_files=get_category_images(categories)
    form=AddCategory()
    if form.validate_on_submit():
        add_category(name=form.name.data,picture=form.picture.data)
        return redirect(url_for('admin_all_categories'))
    return render_template('admin/all_categories.html',pagename='Admin/All Categories',categories=categories,image_files=image_files,form=form,search=search,len=len)

@app.route("/admin/drop_all_categories", methods=['GET','POST'])
@login_required
@admin_required
def admin_drop_all_categories():
    drop_all()
    return redirect(url_for('admin'))

@app.route("/admin/delete_category/<int:category_id>", methods=['GET','POST'])
@login_required
@admin_required
def admin_delete_category(category_id):
    category=Category.query.filter_by(category_id=category_id).first()
    for noun in category.nouns:
        db.session.delete(noun)
    for request in category.noun_requests:
        db.session.delete(request)
    shutil.rmtree(os.path.join(app.root_path,'static',"categories",category.name))
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin_all_categories'))

@app.route("/admin/reset_category_ranks/<int:category_id>",methods=['GET','POST'])
@login_required
@admin_required
def admin_reset_category_ranks(category_id):
    category=Category.query.get(category_id)
    category.matchup_count=0
    for noun in category.nouns:
        noun.points=starting_points
    db.session.commit()
    return redirect(url_for('admin_all_categories'))

@app.route("/admin/edit_category/<int:category_id>", methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_category(category_id):
    category=Category.query.get(category_id)
    form=AddCategory()
    if form.validate_on_submit():
        #Check Name
        if form.name.data==category.name:
            category= Category.query.get(category_id)
            category.name=form.name.data
        elif Category.query.filter_by(name=form.name.data).first():
            flash('That Name Exists','danger')
            return render_template('admin/edit_category.html',pagename='Admin',form=form,category=category)
        else:
            category= Category.query.get(category_id)
            os.rename(category.name,form.name.data)
            category.name=form.name.data

        if form.picture.data:
            #Check that photo is not default now
            if category.image_file != '../../../images/default.jpg':
                os.remove(os.path.join(app.root_path,'static',"categories",category.name,'images',category.image_file))
            picture_file = save_picture(form.picture.data,category.name)
            category.image_file = picture_file
        db.session.commit()
        return redirect(url_for('admin_all_categories'))
    elif request.method == 'GET':
        form.name.data = category.name
        form.picture.data=category.image_file
    return render_template('admin/edit_category.html',pagename='Admin',form=form,category=category)

@app.route("/admin/delete_noun/<int:noun_id>/<category_url>", methods=['GET','POST'])
@login_required
@admin_required
def admin_delete_noun(noun_id,category_url):
    noun=Noun.query.get(noun_id)
    if noun.image_file!= '../../../images/default.jpg':
        os.remove(os.path.join(app.root_path,'static','categories',category_url.replace('_'," "),'images',noun.image_file))
    noun=Noun.query.get(noun_id)
    db.session.delete(noun)
    db.session.commit()
    return redirect(url_for('admin_all_nouns',category_url=category_url))

@app.route("/admin/all_nouns/<category_url>", methods=['GET','POST'])
@login_required
@admin_required
def admin_all_nouns(category_url):
    category_name=category_url.replace('_'," ")
    category=Category.query.filter_by(name=category_name).first()
    nouns=category.nouns
    search=SearchBar()
    if search.validate_on_submit():
        nouns=search_site(search.content.data,Noun,items=nouns)
    noun_requests=category.noun_requests
    image_files=get_noun_images(nouns,category_name)
    image_request_files=get_noun_images(noun_requests,category_name,KEY='REQUEST')
    form=AddNoun()
    if form.validate_on_submit():
        add_noun(form.name.data,form.description.data,category_name,form.picture.data)
        return redirect(url_for('admin_all_nouns',category_url=category_url))
    return render_template('admin/all_category_nouns.html',pagename='Admin/All Nouns',nouns=nouns,noun_requests=noun_requests,image_files=image_files,image_request_files=image_request_files,
    form=form,category_url=category_url,category_name=category_name,search=search)

@app.route("/admin/edit_noun/<category_url>/<noun_id>", methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_noun(category_url,noun_id):
    category=Category.query.filter_by(name=category_url.replace('_'," ")).first()
    noun=Noun.query.get(noun_id)
    form=AddNoun()
    if form.validate_on_submit():
        #Check Name
        if form.name.data==noun.name:
            noun= Noun.query.get(noun_id)
            noun.name=form.name.data
            noun.description=form.description.data
        elif Noun.query.filter_by(name=form.name.data).first():
            flash('That Name Exists','danger')
            return render_template('admin/edit_noun.html',pagename='Admin',form=form,noun=noun)
        else:
            noun= Noun.query.get(noun_id)
            noun.name=form.name.data
            noun.description=form.description.data

        if form.picture.data:
            #Check that photo is not default now
            if noun.image_file != '../../../images/default.jpg':
                os.remove(os.path.join(app.root_path,'static',"categories",category.name,'images',noun.image_file))
            picture_file = save_picture(form.picture.data,category.name)
            noun.image_file = picture_file
        db.session.commit()
        return redirect(url_for('admin_all_nouns',category_url=category_url))
    elif request.method == 'GET':
        form.name.data = noun.name
        form.picture.data=noun.image_file
    return render_template('admin/edit_noun.html',pagename='Admin',form=form,noun=noun)

@app.route("/admin/all_noun_requests", methods=['GET','POST'])
@login_required
@admin_required
def admin_all_noun_requests():
    noun_requests=NounRequest.query.all()
    image_files=get_noun_images(noun_requests,category_name=None,KEY='REQUEST')
    return render_template('admin/all_noun_requests.html',noun_requests=noun_requests,image_files=image_files,nouns=noun_requests)

@app.route("/admin/category_noun_requests", methods=['GET','POST'])
@login_required
@admin_required
def admin_category_noun_reqeusts():
    pass

@app.route("/admin/deny_noun_request/<noun_request_id>", methods=['GET','POST'])
@app.route("/admin/deny_noun_request/<noun_request_id>/<KEY>", methods=['GET','POST'])
@login_required
@admin_required
def admin_deny_noun_request(noun_request_id,KEY=None):
    noun_request=NounRequest.query.get(noun_request_id)
    category_url=noun_request.category_name.replace(' ','_')
    db.session.delete(noun_request)
    db.session.commit()
    if KEY==None:
        return redirect(url_for('admin_all_noun_requests'))
    elif KEY=='ALL':
        return redirect(url_for('admin_all_nouns',category_url=category_url))

@app.route("/admin/accept_noun_request/<noun_request_id>", methods=['GET','POST'])
@app.route("/admin/accept_noun_request/<noun_request_id>/<KEY>", methods=['GET','POST'])
@login_required
@admin_required
def admin_accept_noun_request(noun_request_id,KEY=None):
    noun_request= NounRequest.query.get(noun_request_id)
    try:
        add_noun(name=noun_request.name,description=noun_request.description,image_file=noun_request.image_file,category_name=noun_request.category_name,KEY='REQUEST')
    except Exception as e:
        print(e)
        print('Can\'t add this noun')
        flash('Can\'t add this noun')
        if KEY=='ALL':
            return(redirect(url_for('admin_all_noun_requests')))
        elif KEY==None:
            return redirect(url_for('admin_all_nouns',category_url=noun_request.category_name.replace(" ","_")))
    return redirect(url_for('admin_deny_noun_request',noun_request_id=noun_request.noun_id,KEY=KEY))

#WORK ON
@app.route("/admin/edit_noun_request/<noun_request_id>", methods=['GET','POST'])
@app.route("/admin/edit_noun_request/<noun_request_id>/<KEY>", methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_noun_request(noun_request_id,KEY=None):
    form = AddNoun()
    noun_request=NounRequest.query.get(noun_request_id)
    if form.validate_on_submit():
        noun_request.name=form.name.data
        noun_request.description=form.description.data
        if form.picture.data:
            #Check that photo is not default now
            if noun_request.image_file:
                os.remove(os.path.join(app.root_path,'static',"categories",noun_request.category_name,'request_images',noun_request.image_file))
            picture_file = save_picture(form.picture.data,category=noun_request.category_name,KEY='REQUEST_NOUN')
            noun_request.image_file = picture_file

        db.session.commit()
        return redirect(url_for('admin_accept_noun_request',noun_request_id=noun_request.noun_id,KEY=KEY))
    elif request.method == 'GET':
        form.name.data = noun_request.name
        form.description.data= noun_request.description
        form.picture.data=noun_request.image_file
    return render_template('admin/edit_noun_request.html',noun=noun_request,form=form)

@app.route("/admin/all_users", methods=['GET','POST'])
@app.route("/admin/all_users/<sort_by>", methods=['GET','POST'])
@login_required
@admin_required
def admin_all_users(sort_by='.ID'):
    all_users=User.query.all()
    users=sort_users(all_users,sort_by='.MATCHUPS_PLAYED')
    search=SearchBar()
    if search.validate_on_submit():
        users=search_site(search.content.data,User,items=users)
    return render_template('admin/all_users.html',users=users,search=search)

@app.route("/admin/delete_user/<user_id>", methods=['GET','POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    try:
        user=User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
    except:
        flash('User Does Not Exist')
        return redirect(url_for('home'))
    return redirect(url_for('admin_all_users'))


@app.route("/admin/upload_test_data", methods=['GET','POST'])
@login_required
@admin_required
def admin_upload_test_data():
    try:
        upload_test_data()
    except Exception as e:
        print(e)
        flash('Can\'t upload images')
    return redirect(url_for('home'))

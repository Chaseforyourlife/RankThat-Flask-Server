import os
import secrets
import shutil
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
#from flask_mail import Message
from fame import app, db, bcrypt
#from fame import mail
from fame.Rank import get_matchup,rank_matchup,starting_points
from fame.models import Category,CategoryRequest,Noun,NounRequest,User


category_image_size=(250,250)





def add_category(name,picture,KEY=None):
    if name not in [category.name for category in Category.query.all()]:
        os.mkdir(os.path.join(app.root_path,'static',"categories",name))
        os.mkdir(os.path.join(app.root_path,'static',"categories",name,"images"))
        os.mkdir(os.path.join(app.root_path,'static',"categories",name,"request_images"))
    else:
        riase: Exception("Can't add category because name already exists")
    if KEY=='REQUEST':
        if picture=='../images/default.jpg':
            category=Category(name=name)
        else:
            os.rename(os.path.join(app.root_path,'static','category_request_images',picture),os.path.join(app.root_path,'static','categories',name,'images',picture))
            picture_file=picture
            category=Category(name=name,image_file=picture_file)
    elif KEY=='TEST':
        if picture:
            shutil.copy(os.path.join(app.root_path,'test_data','IMAGES',picture),os.path.join(app.root_path,'static','categories',name,'images',picture))
            picture_file=picture
            category=Category(name=name,image_file=picture_file)
        else:
            category=Category(name=name)



    elif picture:
        picture_file = save_picture(picture,name)
        category = Category(name=name,image_file=picture_file)

    else:
        category = Category(name=name)
    db.session.add(category)
    db.session.commit()

def add_noun(name,description,category_name,image_file=None,KEY=None):
    if image_file:
        if KEY=='REQUEST':
            os.rename(os.path.join(app.root_path,'static','categories',category_name,'request_images',image_file),os.path.join(app.root_path,'static','categories',category_name,'images',image_file))
            noun=Noun(name=name,description=description,category_name=category_name,points=starting_points,image_file=image_file)
        elif KEY=='TEST':
            shutil.copy(os.path.join(app.root_path,'test_data',category_name,image_file),os.path.join(app.root_path,'static','categories',category_name,'images',image_file))
            noun=Noun(name=name,description=description,category_name=category_name,points=starting_points,image_file=image_file)
        elif KEY==None:
            picture_file = save_picture(image_file,category_name)
            noun=Noun(name=name,description=description,category_name=category_name,points=starting_points,image_file=picture_file)
    else:
        noun = Noun(name=name,description=description,category_name=category_name,points=starting_points)
    db.session.add(noun)
    db.session.commit()


def drop_all():
    for category in Category.query.all():
        try:
            shutil.rmtree(os.path.join(app.root_path,'static',"categories",category.name))
        except Exception as e:
            print("ERROR:",e)
    for category_request in CategoryRequest.query.all():
        try:
            os.remove(os.path.join(app.root_path,'static','category_request_images',category_request.image_file))
        except Exception as e:
            print("ERROR:",e)
    db.drop_all()
    db.create_all()
    chase_admin=User(name='admin',email='admin@gmail.com',is_admin=True,password=bcrypt.generate_password_hash("password").decode('utf-8'))
    db.session.add(chase_admin)
    db.session.commit()

def get_noun_images(nouns,category_name=None,KEY=None):
    noun_id__image_file={}
    if KEY=='REQUEST':
        for noun_request in nouns:
            if noun_request.image_file:
                if category_name:
                    noun_id__image_file[noun_request.noun_id] = url_for('static',filename="/".join(['categories',category_name,'request_images',noun_request.image_file]))
                if not category_name:
                    noun_id__image_file[noun_request.noun_id] = url_for('static',filename="/".join(['categories',noun_request.category_name,'request_images',noun_request.image_file]))
    elif KEY==None:
        for noun in nouns:
            noun_id__image_file[noun.noun_id] = url_for('static',filename='categories/'+category_name+'/images'+'/'+noun.image_file)
    return noun_id__image_file

def get_noun_points_rank_array(category):
    ranks=[]
    for count,rank in enumerate(category.ranks):
        noun_name=Noun.query.get(rank.noun_id).name
        person_rank=count+1
        person_points=rank.points
        person_id=rank.person_id
        ranks.append(person_name,person_rank,person_points,person_id)
    return ranks



def save_picture(form_picture,category=None,KEY=None):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    #If picture is a request form
    if KEY=='REQUEST_NOUN':
        picture_path = os.path.join(app.root_path,'static',"categories",category,'request_images',picture_fn)
    elif KEY==None:
        if category==None:
            picture_path = os.path.join(app.root_path,'static',"category_request_images",picture_fn)
        else:
            picture_path = os.path.join(app.root_path,'static',"categories",category,'images',picture_fn)
    output_size = (category_image_size) if category_image_size else (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body=f'''To reset your password, visit the following link:
    {url_for('reset_password',token=token, _external=True)}
    If you did not make this request, simply ignore this email and no changes will be made.'''
    mail.send(msg)





def upload_test_data():
    category_images=os.listdir(os.path.join(app.root_path,'test_data','IMAGES'))
    categories= os.listdir(os.path.join(app.root_path,'test_data'))
    categories.pop(categories.index('IMAGES'))
    for category in categories:
        image=None
        if category+'.jpg' in category_images:
            image=category+'.jpg'
        elif category+'.png' in category_images:
            image=category+'.png'
        add_category(category,picture=image,KEY='TEST')
        nouns= os.listdir(os.path.join(app.root_path,'test_data',category))
        for noun in nouns:
            name=".".join(noun.split('.')[:-1])
            add_noun(name,None,category,image_file=noun,KEY='TEST')

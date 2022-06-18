##IMPORTS


from fame import db
from fame.models import Category, Noun
import time
import random
import math

##VARIABLES
standard_difference =5
starting_points = 1000


##FUNCTIONS

def get_matchup(category_url):

    category=Category.query.filter_by(name=category_url.replace('_'," ")).first()

    num_nouns=len(category.nouns)
    noun_1=category.nouns[(random.randint(0,num_nouns-1))]
    noun_2=category.nouns[(random.randint(0,num_nouns-1))]
    while noun_2==noun_1:
        noun_2=category.nouns[(random.randint(0,num_nouns-1))]
    return(noun_1,noun_2)

def rank_matchup(winner,loser,category_url):

    category_id=Category.query.filter_by(name=category_url.replace('_',' ')).first().category_id
    Category.query.get(category_id).matchup_count+=1
    winner_noun=Noun.query.get(winner)
    loser_noun=Noun.query.get(loser)
    winner_rank_points = winner_noun.points
    #print("initial winner rank points:",winner_rank_points,"\n nounid:",winner)
    loser_rank_points = loser_noun.points

    point_diff = winner_rank_points-loser_rank_points
    ##COULD TRY LOG FUNCTION
    change=-1*(point_diff / 100)**3+standard_difference
    if change<0:
        change=0
    elif change>(standard_difference*2):
        change=standard_difference*2

    winner_rank_points+=change
    loser_rank_points-=change
    #print("final winner rank points:",winner_rank_points,"\n nounid:",winner)
    winner_noun.points = winner_rank_points
    loser_noun.points = loser_rank_points
    db.session.commit()

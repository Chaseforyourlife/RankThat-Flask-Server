from fame import db
from fame.models import Category, Noun
from fame.models import *
import math


class Phrase:
    def __init__(self, name,points=0):
        self.name = name
        self.words = [Word(word) for word in name.split(' ')]
        self.points= points

    def __str__(self):
        return self.name


    def rank(self,search_phrase):
        for word in self.words:
            for search_word in search_phrase.words:
                self.points+=word.rank_points(search_word)
        self.points=self.points/(len(self.words))


class Word:
    def __init__(self,name,points=0):
        self.name = name.lower()
        self.variations= self.scramble()
        self.word_points=points

    def scramble(self):
        variations=[]
        # starts at 0,letter
        for window,letter in enumerate(self.name):
            #starts at 0
            for i in range(len(self.name)-window):
                #if window ends within list:
                try:
                    combination=self.name[i:i+window+1]
                #if window ends outside of list:
                except Exception:
                    combination=self.name[i:]
                variations.append(combination)
        return variations

    def rank_points(self,search_word):

        set_of_variations= set(self.variations)
        set_of_search_word= set(search_word.variations)
        intersection_set = set_of_search_word.intersection(set_of_variations)
        #TEST
        for combination in intersection_set:
            self.word_points+=math.pow(3,len(combination)-1)
        return self.word_points



#MAIN FUNCTION
def search_site(search_input,object_type,items=None,glide=False):
    all_items=object_type.query.all() if not items else items
    all_names=[item.name for item in all_items]
    if object_type==Category and glide==False:
        return sort_category(all_items,search_input)
    if object_type==Noun and glide==False:
        return sort_nouns(all_items,search_input)
    #else:
    #    raise Exception('KEY not recognized')

    #Make Phrase objects
    category_phrase_array= [Phrase(name) for name in all_names]
    search_phrase=Phrase(search_input)
    #Rank phrase relevance
    for category in category_phrase_array:
        category.rank(search_phrase)
    names_of_objects = order_by_points(category_phrase_array)
    print(names_of_objects)
    return_objects= [object_type.query.filter_by(name=name).first() for name in names_of_objects]
    return return_objects

def order_by_points(phrase_array):
    point_phrase_array=[]
    for phrase in phrase_array:
        point_phrase_array.append((phrase.points,phrase.name))
    points=[i[0] for i in sorted(point_phrase_array,reverse=True)]
    print(points)
    names=[i[1] for i in sorted(point_phrase_array,reverse=True)]
    return names


#sort_by is always a string
#USED recursively with SEARCH_SITE function
def sort_category(categories,sort_by='.ID'):
    print("SORT_BY:",sort_by)
    if sort_by=='.ID':
        sorted_id_array=sorted([(category.category_id) for category in categories])
        return [Category.query.get(id) for id in sorted_id_array]
    elif sort_by=='.NOUN_REQUESTS':
        sorted_noun_requests__category_array=sorted([(len(category.noun_requests),category.category_id) for category in categories],reverse=True)
        return [Category.query.get(id) for noun_requests,id in sorted_noun_requests__category_array]
    elif sort_by=='.NOUN_COUNT':
        sorted_noun_count__category_array=sorted([(len(category.nouns),category.category_id) for category in categories],reverse=True)
        return [Category.query.get(id) for noun_count,id in sorted_noun_count__category_array]
    elif sort_by=='.MATCHUP_COUNT':
        sorted_matchup_count__category_array=sorted([(category.matchup_count,category.category_id) for category in categories],reverse=True)
        return [Category.query.get(id) for noun_requests,id in sorted_matchup_count__category_array]

    else:
        return search_site(sort_by,Category,items=categories,glide=True)

def sort_nouns(nouns,sort_by='.ID'):
    if sort_by=='.ID':
        sorted_id_array=sorted([(noun.noun_id) for noun in nouns])
        return [Noun.query.get(id) for id in sorted_id_array]
    else:
        return search_site(sort_by,Noun,items=nouns,glide=True)

def sort_users(users,sort_by='.ID'):
    if sort_by=='.ID':
        sorted_id_array=sorted([(user.id) for user in users])
        return [User.query.get(id) for id in sorted_id_array]
    if sort_by=='.MATCHUPS_PLAYED':
        sorted_id_array=sorted([(user.id) for user in users])
        return [User.query.get(id) for id in sorted_id_array]
    else:
        return search_site(sort_by,User,items=users,glide=True)




#Later will be changed to include time variations
def get_popular_categories(object_type=Category,number_of_categories=16):
    all_time_count_item_array=[]
    all_items=object_type.query.all()
    all_names=[item.name for item in all_items]
    for item in all_items:
        all_time_count_item_array.append((item.matchup_count,item.name))
    names=[i[1] for i in sorted(all_time_count_item_array,reverse=True)]
    return_objects= [object_type.query.filter_by(name=name).first() for name in names]
    return return_objects[:number_of_categories]

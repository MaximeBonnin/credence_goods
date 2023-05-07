from otree.api import *
import random


doc = """
Welcome pages and cosnent making for credence goods game
"""


class C(BaseConstants):
    NAME_IN_URL = 'credence_goods_welcome'
    PLAYERS_PER_GROUP = 8
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    #TODO maybe as dropdown?
    year_of_birth = models.IntegerField(label="Your year of birth (e.g. 1995)")
    occupation = models.StringField(label="Your current occupation (e.g. Student, Employed)")




# PAGES
class WelcomePage(Page):
    form_model = "player"
    form_fields = ["year_of_birth", "occupation"]


class Explanation(Page):
    pass


class Consent(Page):
    pass


page_sequence = [WelcomePage, Explanation, Consent]

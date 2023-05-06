from otree.api import *
import random


doc = """
Welcome pages and match making for credence goods game
"""


class C(BaseConstants):
    NAME_IN_URL = 'credence_goods_welcome'
    PLAYERS_PER_GROUP = 8
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment_investment_option = models.StringField(choices=["skill", "algo"])
    treatment_investment_frequency = models.StringField(choices=["once", "repeated"])
    treatment_investment_visible = models.BooleanField()


class Player(BasePlayer):
    pass



# PAGES
class WelcomePage(Page):
    pass


class Explanation(Page):
    pass


class Consent(Page):
    pass


page_sequence = [WelcomePage, Explanation, Consent]

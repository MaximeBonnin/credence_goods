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
    pass


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

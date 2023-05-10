from otree.api import *
import random


doc = """
Welcome pages and consent for credence goods game
"""


class C(BaseConstants):
    NAME_IN_URL = 'credence_goods_welcome'
    PLAYERS_PER_GROUP = 6
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    #TODO maybe as dropdown?
    year_of_birth = models.IntegerField(label="Your year of birth (e.g. 1995)")
    occupation = models.StringField(label="Your current occupation (e.g. Student, Employed)")


def creating_session(subsession: Subsession):
    print("Creating session...")
    print(f"Skill visible: {subsession.session.config['treatment_skill_visible']} | to change this go to settings -> SESSION_CONFIGS -> treatment_skill_visible")
    for player in subsession.get_players():
        #TODO make this random not just even/uneven
        if player.id_in_group % 2 == 0:
            player.participant.is_expert = True
        else:
            player.participant.is_expert = False

        player.participant.treatment_skill_visible = subsession.session.config['treatment_skill_visible']

# PAGES
class WelcomePage(Page):
    form_model = "player"
    form_fields = ["year_of_birth", "occupation"]


class Explanation(Page):
    pass


class Consent(Page):
    pass


page_sequence = [WelcomePage, Explanation, Consent]

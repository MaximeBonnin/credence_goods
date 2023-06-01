from otree.api import *
import itertools


doc = """
Welcome pages and general introduction
"""


class C(BaseConstants):
    NAME_IN_URL = 'credence_goods_welcome'
    PLAYERS_PER_GROUP = 8
    NUM_ROUNDS = 1
    VALID_DEVICES = ["Laptop", "Desktop PC"]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    #TODO maybe as dropdown?
    valid_player = models.BooleanField(initial=False)
    year_of_birth = models.IntegerField(label="Your year of birth (e.g. 1995)")
    occupation = models.StringField(label="Your current occupation (e.g. Student, Employed)")
    device = models.StringField(choices=["Smartphone", "Laptop", "Tablet", "Desktop PC"], widget=widgets.RadioSelect, label="",)


def creating_session(subsession: Subsession):
    print("Creating session...")
    print(f"Skill visible: {subsession.session.config['treatment_skill_visible']} | to change this go to settings -> SESSION_CONFIGS -> treatment_skill_visible")
    n_experts = 0
    for player in subsession.get_players():
        #TODO make this random not just even/uneven
        if player.id_in_group % 2 == 0:
            player.participant.is_expert = True
            n_experts += 1
            # itertools doesn't work, this will
            if n_experts % 2 == 0:
                player.participant.ability_level = "high"
            else:
                player.participant.ability_level = "low"
        else:
            player.participant.is_expert = False

        player.participant.treatment_skill_visible = subsession.session.config['treatment_skill_visible']

# PAGES

class Device(Page):
    form_model = "player"
    form_fields = ["device"]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.device in C.VALID_DEVICES:
            player.valid_player = True
        else:
            print(f"Player excluded because of device choice ({player.device}).")



class Explanation(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.valid_player


class InvalidPlayer(Page):
    @staticmethod
    def is_displayed(player: Player):
        return not player.valid_player
    

page_sequence = [Device, Explanation, InvalidPlayer]

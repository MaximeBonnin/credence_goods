from otree.api import *
import itertools
import random
import string

doc = """
Welcome pages and general introduction
"""


class C(BaseConstants):
    NAME_IN_URL = 'credence_goods_welcome'
    PLAYERS_PER_GROUP = 6
    NUM_ROUNDS = 1
    VALID_DEVICES = ["Laptop", "Desktop PC", "Tablet"]


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
    completion_code = models.StringField()
    


def creating_session(subsession: Subsession):
    print("Creating session...")
    print(f"Skill visible: {subsession.session.config['treatment_skill_visible']} | to change this go to settings -> SESSION_CONFIGS -> treatment_skill_visible")
    n_experts = 0
    for player in subsession.get_players():
        player.participant.number_of_timeouts = 0
        #TODO make this random not just even/uneven
        if player.id_in_group % 2 == 0:
            player.participant.is_expert = True
            n_experts += 1
            # itertools doesn't work, this will
            if n_experts % 3 == 0:
                player.participant.ability_level = "high"
            else:
                player.participant.ability_level = "low"
        else:
            player.participant.is_expert = False

        player.participant.treatment_skill_visible = subsession.session.config['treatment_skill_visible']
        # generate completion code
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(7))) + str(random.randint(1, 8))
        player.completion_code = result_str
        player.participant.vars['completion_code'] = result_str        

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

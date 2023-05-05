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


class MatchingWaitPage(WaitPage):

    group_by_arrival_time = True

    title_text = "Matching in progress"
    body_text = "You are currently waiting to be matched with other players. This will only take a minute..."

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.group.treatment_investment_option = random.choice(["skill", "algo"])
        player.group.treatment_investment_frequency = random.choice(["once", "repeated"])
        player.group.treatment_investment_visible = random.choice([True, False])
        print(f"Group matched: {player.group.treatment_investment_option=} | {player.group.treatment_investment_frequency=} | {player.group.treatment_investment_visible=}")
    

class Explanation(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [WelcomePage, MatchingWaitPage, Explanation, ResultsWaitPage, Results]

from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'credence_goods'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_EXPERTS = 4             # consumers = players - experts
    TIMEOUT_IN_SECONDS = 60 

    


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    import random                           # why is this recommended here by the docs?
    expert_sample = random.sample([p.id_in_group for p in subsession.get_players()], C.NUM_EXPERTS)

    for player in subsession.get_players():
        if player.id_in_group in expert_sample:
            player.is_expert = True

        print(f"Player {player.id_in_group} is expert: {player.is_expert}")


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    is_expert = models.BooleanField(initial=False)

    # expert variables
    prices_small_service = models.IntegerField()
    prices_large_service = models.IntegerField()



# PAGES

# Intro
class Intro(Page):
    timeout_seconds = 60 * 5    # 5 min

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1  # only display in first round


# Expert set prices
class ExpertSetPrices(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player):
        return player.is_expert


# Consumer choose expert
class ConsumerChooseExpert(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player):
        return not player.is_expert


# Expert diagnosis I
class ExpertDiagnosisI(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player):
        return player.is_expert


# Expert diagnosis II
class ExpertDiagnosisII(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player):
        return player.is_expert


# Consumer Results
class ConsumerResults(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player):
        return not player.is_expert

# Expert Results
class ExpertResults(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player):
        return player.is_expert




class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Intro, 
                 ExpertSetPrices, 
                 ConsumerChooseExpert, 
                 ExpertDiagnosisI, 
                 ExpertDiagnosisII, 
                 ConsumerResults, 
                 ExpertResults, 
                 ResultsWaitPage, 
                 Results
                 ]

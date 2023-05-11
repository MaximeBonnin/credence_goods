from otree.api import *


doc = """
Role-specific introduction and practice rounds before grouping.
"""


class C(BaseConstants):
    NAME_IN_URL = 'practice_round'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # vars for excluding dropouts
    valid_player = models.BooleanField(initial=True)
    is_dropout = models.BooleanField(initial=False)

# PAGES

class Introduction(Page):
    pass


class SimulatedConsumerChooseExpert(Page):
    @staticmethod
    def is_displayed(player):
        return not player.participant.is_expert

class SimualtedExpertChoosePrices(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.is_expert
class SimualtedExpertDiagnosisI(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.is_expert

class SimualtedExpertDiagnosisII(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.is_expert

class SimulatedResults(Page):
    pass


page_sequence = [
    Introduction,
    SimulatedConsumerChooseExpert,
    SimualtedExpertChoosePrices,
    SimualtedExpertDiagnosisI,
    SimualtedExpertDiagnosisII,
    SimulatedResults
    ]

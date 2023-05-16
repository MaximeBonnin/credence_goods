from otree.api import *


doc = """
Role-specific introduction and practice rounds before grouping.
"""


class C(BaseConstants):
    NAME_IN_URL = 'practice_round'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    PLAYERS_PER_GROUP = 6
    TIMEOUT_IN_SECONDS = 1500               # Intro page is different
    DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS = 3 # players get excluded from the experiment if they have X number of timeouts

    NUM_EXPERTS_PER_GROUP = 3                         # consumers = players - experts #TODO currently not working, every second person is set to expert
    NUM_CONSUMERS_PER_GROUP = PLAYERS_PER_GROUP - NUM_EXPERTS_PER_GROUP

    ENDOWMENT = 10                      #TODO maybe different for consumers and experts?


    COST_OF_PROVIDING_SMALL_SERVICE = 1     # c_k
    COST_OF_PROVIDING_LARGE_SERVICE = 2     # c_g

    CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT = 40 # %

    PRICE_VECTOR_OPTIONS = {                # (price_small, price_large, profit_small, profit_large)
        "bias_small": (4, 4, 
                       4-COST_OF_PROVIDING_SMALL_SERVICE, 4-COST_OF_PROVIDING_LARGE_SERVICE),
        "bias_large": (2, 5, 
                       2-COST_OF_PROVIDING_SMALL_SERVICE, 5-COST_OF_PROVIDING_LARGE_SERVICE),
        "no_bias": (3, 4, 
                    3-COST_OF_PROVIDING_SMALL_SERVICE, 4-COST_OF_PROVIDING_LARGE_SERVICE)
    }

    EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT = { # currently just random.choice() for selection
        "low": 50,
        "high": 75,
        "invested": 90
    }

    CONSUMER_PAYOFFS = {
        "no_market_entry": 0,
        "problem_remains": 0,
        "problem_solved": 10
    }

    INVESTMENT_STARTING_ROUND = 2
    INVESTMENT_COST = {
        "once": 20,
        "repeated": 2
    }


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

class Role(Page):
    pass

class ExperimentalProcedure(Page):
    pass

class SettingPrices(Page):
    pass

class Diagnosis(Page):
    pass

class Payoffs(Page):
    pass

class RoundOverview(Page):
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
    Role,
    ExperimentalProcedure,
    SettingPrices,
    Diagnosis,
    Payoffs,
    RoundOverview,
    SimulatedConsumerChooseExpert,
    SimualtedExpertChoosePrices,
    SimualtedExpertDiagnosisI,
    SimualtedExpertDiagnosisII,
    SimulatedResults
    ]
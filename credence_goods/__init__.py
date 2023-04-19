from otree.api import *
import random


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'credence_goods'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2

    NUM_EXPERTS = 4             # consumers = players - experts
    TIMEOUT_IN_SECONDS = 6000     # Intro page is different

    COST_OF_PROVIDING_SMALL_SERVICE = 1 # c_k
    COST_OF_PROVIDING_LARGE_SERVICE = 2 # c_g

    
class Subsession(BaseSubsession):
    # expert_list = []
    pass


class Player(BasePlayer):
    is_expert = models.BooleanField(initial=False)

    # expert variables
    expert_color = models.StringField() #TODO do this at participant level?

    price_small_service = models.IntegerField(initial=2, choices=(1, 2, 3))                # p_k   #TODO make this dynamic
    price_large_service = models.IntegerField(initial=5, choices=(4, 5, 6))                # p_g

    ability_level = models.StringField(choices=("high", "low"))                 # 
    diagnosis_accuracy = models.FloatField()                                    # depends on high / low ability

    service_result_of_formula = models.StringField(choices=("small", "large"))
    service_chosen_as_expert = models.StringField(choices=("small", "large"))   # seems odd since it should be same as service_result_of_formula

    # customer variables
    expert_chosen = models.IntegerField(initial="none") # this should be a player.id_in_group
    service_needed = models.StringField(choices=("small", "large"), initial="none")
    service_recieved = models.StringField(choices=("small", "large", "none"), initial="none")

    # variables for documentation
    cost_of_providing_small_service =  models.IntegerField(initial=C.COST_OF_PROVIDING_SMALL_SERVICE) # c_k
    cost_of_providing_large_service =  models.IntegerField(initial=C.COST_OF_PROVIDING_LARGE_SERVICE) # c_g


def setup_players(subsession):

    print(f"Round {subsession.round_number} player setup...") # the numbers don't display correctly, but it works

    # in later rounds, just use previous values
    if subsession.round_number != 1:
        print("Use values from previous rounds...")
        for player in subsession.get_players():
            player.is_expert = player.in_round(1).is_expert
            player.ability_level = player.in_round(1).ability_level
            player.expert_color = player.in_round(1).expert_color
            player.diagnosis_accuracy = player.in_round(1).diagnosis_accuracy

            # service needed changes each round
            player.service_needed = random.choice(("small", "large"))

            if player.is_expert:
                print(f"Expert {player.id_in_group} ({player.expert_color}): {player.ability_level} ability")
            else:
                print(f"Consumer {player.id_in_group}: {player.service_needed} service needed")
        return
    

    # in first round, setup player values
    expert_sample = random.sample([p.id_in_group for p in subsession.get_players()], C.NUM_EXPERTS)
    for player in subsession.get_players():

        if player.id_in_group in expert_sample:
            player.is_expert = True

            # setup experts
            player.ability_level = random.choice(("low", "high"))
            if player.ability_level == "high":
                player.diagnosis_accuracy = 0.85    #TODO make dynamic
            else:
                player.diagnosis_accuracy = 0.75

            player.price_small_service = 2 #TODO remove this, should work without once experts choose
            player.price_large_service = 5

            
            player.expert_color = ["red", "green", "blue", "yellow", 
                                   "cyan", "pink", "salmon", "grey"][player.id_in_group-1] #TODO add more colors

        else:
            # setup consumers #TODO this does need to change between rounds
            player.service_needed = random.choice(("small", "large"))

        if player.is_expert:
                print(f"Expert {player.id_in_group} ({player.expert_color}): {player.ability_level} ability")
        else:
            print(f"Consumer {player.id_in_group}: {player.service_needed} service needed")



def creating_session(subsession):
    print("Creating subsession...")
    setup_players(subsession) # this runs twice for some reason

    


class Group(BaseGroup):
    pass





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
    form_model = "player"
    form_fields = ["price_small_service", "price_large_service"]

    @staticmethod
    def is_displayed(player):
        return player.is_expert


# Consumer choose expert
class ConsumerChooseExpert(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["expert_chosen"]

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

class ConsumerWaitPage(WaitPage):
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

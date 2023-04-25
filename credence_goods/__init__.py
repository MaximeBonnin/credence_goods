from otree.api import *
import random
import json


doc = """
Your app description
"""


class C(BaseConstants):
    # DEV VARS FOR TESTING
    ENABLE_WAITING_PAGES = False

    #

    NAME_IN_URL = 'credence_goods'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4
    INVESTMENT_STARTING_ROUND = 2

    NUM_EXPERTS = 4             # consumers = players - experts
    TIMEOUT_IN_SECONDS = 6000     # Intro page is different #TODO results page different too?

    COST_OF_PROVIDING_SMALL_SERVICE = 1 # c_k
    COST_OF_PROVIDING_LARGE_SERVICE = 2 # c_g

    CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT = 40 # %

    PRICE_VECTOR_OPTIONS = { # (price_small, price_large, profit_small, profit_large)
        "bias_small": (4, 4, 
                       4-COST_OF_PROVIDING_SMALL_SERVICE, 4-COST_OF_PROVIDING_LARGE_SERVICE),
        "bias_large": (2, 5, 
                       2-COST_OF_PROVIDING_SMALL_SERVICE, 5-COST_OF_PROVIDING_LARGE_SERVICE),
        "no_bias": (3, 4, 
                    3-COST_OF_PROVIDING_SMALL_SERVICE, 4-COST_OF_PROVIDING_LARGE_SERVICE)
    }

    
class Subsession(BaseSubsession):
    # expert_list = []
    pass


class Player(BasePlayer):
    is_expert = models.BooleanField(initial=False)

    # expert variables
    expert_color = models.StringField()
    price_vector_chosen = models.StringField(choices=["bias_small", "bias_large", "no_bias"], initial="no_bias")
    price_small_service = models.IntegerField(initial=C.PRICE_VECTOR_OPTIONS["no_bias"][0]) # initialize as small value of "no_bias" option in constants
    price_large_service = models.IntegerField(initial=C.PRICE_VECTOR_OPTIONS["no_bias"][1]) # initialize as large value of "no_bias" option in constants

    ability_level = models.StringField(choices=("high", "low"))                 # 
    diagnosis_accuracy_percent = models.IntegerField()                                    # depends on high / low ability

    # service_result_of_formula = models.StringField(choices=("small", "large"))
    services_provided_to_all_consumers = models.LongStringField()

    investment_decision = models.StringField(choices=["skill", "algo", "none"], initial="none")

    # customer variables
    enter_market = models.BooleanField(initial=True)
    expert_chosen = models.IntegerField(initial=0) # this should be a player.id_in_group
    expert_chosen_color = models.StringField()
    service_needed = models.StringField(choices=("small", "large"), initial="none")
    service_recieved = models.StringField(choices=("small", "large", "none"))

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
            player.diagnosis_accuracy_percent = player.in_round(1).diagnosis_accuracy_percent

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
                player.diagnosis_accuracy_percent = 85    #TODO make dynamic
            else:
                player.diagnosis_accuracy_percent = 75

            
            player.expert_color = ["Red", "Aquamarine", "Coral", "Yellow", 
                                   "Cyan", "Pink", "Salmon", "Grey",
                                   "Lime", "Teal", "Silver", "White"][player.id_in_group-1] #TODO add more colors

        else:
            # setup consumers
            if random.randint(1, 100) <= C.CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT:
                player.service_needed = "large"
            else:
                player.service_needed = "small"

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
    

# Expert investment choice
class InvestmentChoice(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS  
    form_model = "player"
    form_fields = ["investment_decision"]

    @staticmethod
    def is_displayed(player):
        if (player.round_number == C.INVESTMENT_STARTING_ROUND) and player.is_expert:
            return True


# Expert set prices
class ExpertSetPrices(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["price_vector_chosen"]

    @staticmethod
    def is_displayed(player):
        return player.is_expert
    
    @staticmethod
    def js_vars(player):
        return dict(
            price_vectors=C.PRICE_VECTOR_OPTIONS,
        )
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # set prices as the vector options
        player.price_small_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][0]
        player.price_large_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][1]
        return



# Consumer choose expert
class ConsumerEnterMarket(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["enter_market"]

    @staticmethod
    def is_displayed(player):
        return not player.is_expert

# Consumer choose expert
class ConsumerChooseExpert(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["expert_chosen"]

    @staticmethod
    def is_displayed(player):
        if not player.is_expert:
            return player.enter_market
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.expert_chosen:
            player.expert_chosen_color = player.group.get_player_by_id(
                player.expert_chosen).expert_color


# Expert diagnosis I
class ExpertDiagnosisI(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player):
        return player.is_expert


def get_service_from_json_by_id(json_string, id) -> str:
    mydict = json.loads(json_string)
    return mydict[str(id)]


# Expert diagnosis II
class ExpertDiagnosisII(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["services_provided_to_all_consumers"]

    @staticmethod
    def is_displayed(player):
        return player.is_expert
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # apply service
        for p in player.get_others_in_subsession():
            if (not p.is_expert) and (p.expert_chosen == player.id_in_group):
                p.service_recieved = get_service_from_json_by_id(player.services_provided_to_all_consumers, p.id_in_group)
                print(p.service_recieved)


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




class GeneralWaitPage(WaitPage):
    title_text = "Waiting for other players"
    body_text = "You are currently waiting for other players to join. It will only take a minute..."

    @staticmethod
    def is_displayed(player):
        if C.ENABLE_WAITING_PAGES:
            return player.round_number == 1
        else:
            print("Waiting page skipped due to settings.")


class ExpertWaitPage(WaitPage):
    title_text = "Waiting for consumers"
    body_text = "You are currently waiting for the consumers to make a decision. It will only take a minute..."

    @staticmethod
    def is_displayed(player):
        if C.ENABLE_WAITING_PAGES:
            return player.is_expert
        else:
            print("Waiting page skipped due to settings.")
            return False


class ConsumerWaitPage(WaitPage):
    title_text = "Waiting for experts"
    body_text = "You are currently waiting for the consumers to make a decision. It will only take a minute..."


    @staticmethod
    def is_displayed(player):
        if C.ENABLE_WAITING_PAGES:
            return not player.is_expert
        else:
            print("Waiting page skipped due to settings.")
            return False


class Results(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS
    pass


page_sequence = [GeneralWaitPage,
                 Intro,
                 InvestmentChoice,
                 ExpertSetPrices,
                 ConsumerWaitPage, 
                 ConsumerEnterMarket,
                 ConsumerChooseExpert, 
                 ExpertWaitPage, 
                 ExpertDiagnosisI, 
                 ExpertDiagnosisII,
                 ConsumerWaitPage, 
                 ConsumerResults, 
                 ExpertResults, 
                 Results
                 ]

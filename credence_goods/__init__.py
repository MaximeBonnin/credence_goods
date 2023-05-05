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
    NUM_ROUNDS = 4
    PLAYERS_PER_GROUP = 8
    TIMEOUT_IN_SECONDS = 15               # Intro page is different
    DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS = 3 # players get excluded from the experiment if they have X number of timeouts

    NUM_EXPERTS = 4                         # consumers = players - experts

    INVESTMENT_STARTING_ROUND = 2
    ENDOWMENT = cu(10)                      #TODO maybe different for consumers and experts?

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
        "low": 75,
        "high": 85
    }

    CONSUMER_PAYOFFS = {
        "no_market_entry": 0,
        "problem_remains": 0,
        "problem_solved": 10
    }

    
class Subsession(BaseSubsession):
    # expert_list = []
    pass


class Player(BasePlayer):
    # vars for excluding dropouts
    is_dropout = models.BooleanField(initial=False)

    is_expert = models.BooleanField(initial=False)
    player_color = models.StringField()
    currency = models.CurrencyField(initial=0)

    # expert variables
    price_vector_chosen = models.StringField(choices=["bias_small", "bias_large", "no_bias"], initial="no_bias")
    price_small_service = models.IntegerField(initial=C.PRICE_VECTOR_OPTIONS["no_bias"][0]) # initialize as small value of "no_bias" option in constants
    price_large_service = models.IntegerField(initial=C.PRICE_VECTOR_OPTIONS["no_bias"][1]) # initialize as large value of "no_bias" option in constants

    ability_level = models.StringField(choices=("high", "low"))                             # 
    diagnosis_accuracy_percent = models.IntegerField()                                      # depends on high / low ability
    services_provided_to_all_consumers = models.LongStringField()

    investment_decision = models.BooleanField(initial=False)

    # customer variables
    enter_market = models.BooleanField(initial=True)
    expert_chosen = models.IntegerField(initial=0)                                          # this should be a player.id_in_group
    expert_chosen_color = models.StringField()
    service_needed = models.StringField(choices=("small", "large"), initial="none")
    service_recieved = models.StringField(choices=("small", "large", "none"))

    # variables for documentation
    cost_of_providing_small_service =  models.IntegerField(initial=C.COST_OF_PROVIDING_SMALL_SERVICE) # c_k
    cost_of_providing_large_service =  models.IntegerField(initial=C.COST_OF_PROVIDING_LARGE_SERVICE) # c_g


def setup_players(subsession):
    print(f"Round {subsession.round_number} player setup...")

    # in later rounds, just use previous values
    if subsession.round_number != 1:
        print("Use values from previous rounds...")
        for group in subsession.get_groups():
            group.treatment_investment_option = group.in_round(1).treatment_investment_option
            group.treatment_investment_frequency = group.in_round(1).treatment_investment_option
            group.treatment_investment_visible = group.in_round(1).treatment_investment_visible

        for player in subsession.get_players():
            player.is_expert = player.in_round(1).is_expert
            player.ability_level = player.in_round(1).ability_level
            player.player_color = player.in_round(1).player_color
            player.diagnosis_accuracy_percent = player.in_round(1).diagnosis_accuracy_percent

            # service needed changes each round
            player.service_needed = random.choice(("small", "large"))
        return
    

    # in first round, setup player values
    for group in subsession.get_groups():
        group.treatment_investment_option = random.choice(["skill", "algo"])
        group.treatment_investment_frequency = random.choice(["once", "repeated"])
        group.treatment_investment_visible = random.choice([True, False])
        print(f"Group treatment set: {group.treatment_investment_option} | {group.treatment_investment_frequency} | {group.treatment_investment_visible}")

        # experts are different between groups
        expert_sample = random.sample(range(1, C.PLAYERS_PER_GROUP+1), C.NUM_EXPERTS)
        
        for player in group.get_players():
            player.participant.number_of_timeouts = 0
            player.participant.is_dropout = False
            player.currency = C.ENDOWMENT
            player.player_color = ["Red", "Aquamarine", "Coral", "Yellow", 
                                    "Cyan", "Pink", "Salmon", "Grey",
                                    "Lime", "Teal", "Silver", "White"][player.id_in_group-1] #TODO add more colors

            if player.id_in_group in expert_sample:
                player.is_expert = True

                # setup experts
                player.ability_level = random.choice(("low", "high"))
                player.diagnosis_accuracy_percent = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT[player.ability_level]


            else:
                # setup consumers
                if random.randint(1, 100) <= C.CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT:
                    player.service_needed = "large"
                else:
                    player.service_needed = "small"


def creating_session(subsession):
    print("Creating subsession...")
    setup_players(subsession) # this runs once for each round when setting up the game


class Group(BaseGroup):
    treatment_investment_option = models.StringField(choices=["skill", "algo"])
    treatment_investment_frequency = models.StringField(choices=["once", "repeated"])
    treatment_investment_visible = models.BooleanField()





# PAGES

# Tutorial
class Tutorial(Page):
    timeout_seconds = 60 * 5 # 5 min


# Intro
class Intro(Page):
    timeout_seconds = C.TIMEOUT_IN_SECONDS # timeout doesnt need to get checked on first page

    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            player.participant.number_of_timeouts += 1
            if player.participant.number_of_timeouts >= C.DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS:
                player.participant.is_dropout = True
                player.is_dropout = True
                print(f"Player {player.id_in_group} excluded due to timeout.")
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1  # only display in first round


# Expert investment choice
class InvestmentChoice(Page):

    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS
        
    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            player.participant.number_of_timeouts += 1
            if player.participant.number_of_timeouts >= C.DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS:
                player.participant.is_dropout = True
                player.is_dropout = True
                print(f"Player {player.id_in_group} excluded due to timeout.")


    form_model = "player"
    form_fields = ["investment_decision"]

    @staticmethod
    def is_displayed(player):
        if (player.round_number == C.INVESTMENT_STARTING_ROUND) and player.is_expert:
            return True


# Expert set prices
class ExpertSetPrices(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS
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
        # handle timeout and setting is_dropout status
        if timeout_happened:
            player.participant.number_of_timeouts += 1
            player.price_vector_chosen = random.choice(["bias_small", "bias_large", "no_bias"]) # random choice if timeout happened
            if player.participant.number_of_timeouts >= C.DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS:
                player.participant.is_dropout = True
                player.is_dropout = True
                print(f"Player {player.id_in_group} excluded due to timeout.")

        # set prices as the vector options
        player.price_small_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][0]
        player.price_large_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][1]
        return


# Consumer choose expert
class ConsumerEnterMarket(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["enter_market"]

    @staticmethod
    def is_displayed(player):
        return not player.is_expert
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            player.participant.number_of_timeouts += 1
            if player.participant.number_of_timeouts >= C.DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS:
                player.participant.is_dropout = True
                player.is_dropout = True
                print(f"Player {player.id_in_group} excluded due to timeout.")


# Consumer choose expert
class ConsumerChooseExpert(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["expert_chosen"]

    @staticmethod
    def is_displayed(player):
        if not player.is_expert:
            return player.enter_market
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            player.participant.number_of_timeouts += 1
            if player.participant.number_of_timeouts >= C.DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS:
                player.participant.is_dropout = True
                player.is_dropout = True
                print(f"Player {player.id_in_group} excluded due to timeout.")

        if player.expert_chosen:
            player.expert_chosen_color = player.group.get_player_by_id(
                player.expert_chosen).player_color


# Expert diagnosis I
class ExpertDiagnosisI(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS
        
    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            player.participant.number_of_timeouts += 1
            if player.participant.number_of_timeouts >= C.DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS:
                player.participant.is_dropout = True
                player.is_dropout = True
                print(f"Player {player.id_in_group} excluded due to timeout.")

    @staticmethod
    def is_displayed(player):
        return player.is_expert


def get_service_from_json_by_id(json_string, id) -> str:
    mydict = json.loads(json_string)
    return mydict[str(id)]


# Expert diagnosis II
class ExpertDiagnosisII(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = ["services_provided_to_all_consumers"]

    @staticmethod
    def js_vars(player):
        return dict(
            price_vectors=C.PRICE_VECTOR_OPTIONS,
        )

    @staticmethod
    def is_displayed(player):
        return player.is_expert
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            player.participant.number_of_timeouts += 1
            if player.participant.number_of_timeouts >= C.DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS:
                player.participant.is_dropout = True
                player.is_dropout = True
                print(f"Player {player.id_in_group} excluded due to timeout.")

        # apply service
        for p in player.get_others_in_subsession():
            if (not p.is_expert) and (p.expert_chosen == player.id_in_group):
                p.service_recieved = get_service_from_json_by_id(player.services_provided_to_all_consumers, p.id_in_group)
                print(p.service_recieved)

                # set consumer payoffs
                if (p.service_needed == p.service_recieved) or (p.service_recieved == "large"):
                    p.payoff = C.CONSUMER_PAYOFFS["problem_solved"]
                else:
                    p.payoff = C.CONSUMER_PAYOFFS["problem_remains"]

                # set expert payoff
                if p.service_recieved == "small":
                    player.payoff += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][2]
                elif p.service_recieved == "large":
                    player.payoff += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][3]


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
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = []

    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            print("Timeout happened. No timeout given because results page.")


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
                 Results
                 ]

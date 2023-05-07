from otree.api import *
import random
import json


doc = """
Your app description
"""


class C(BaseConstants):
    # DEV VARS FOR TESTING
    ENABLE_WAITING_PAGES = True

    #

    NAME_IN_URL = 'credence_goods'
    NUM_ROUNDS = 4
    PLAYERS_PER_GROUP = 8
    TIMEOUT_IN_SECONDS = 1500               # Intro page is different
    DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS = 3 # players get excluded from the experiment if they have X number of timeouts

    NUM_EXPERTS = 4                         # consumers = players - experts #TODO currently not working, every second person is set to expert

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
    # expert_list = []
    pass


class Player(BasePlayer):
    # vars for excluding dropouts
    is_dropout = models.BooleanField(initial=False)

    is_expert = models.BooleanField(initial=False)
    player_color = models.StringField()
    coins = models.IntegerField(initial=0)

    # expert variables
    price_vector_chosen = models.StringField(choices=["bias_small", "bias_large", "no_bias"], initial="no_bias")
    price_small_service = models.IntegerField(initial=C.PRICE_VECTOR_OPTIONS["no_bias"][0]) # initialize as small value of "no_bias" option in constants
    price_large_service = models.IntegerField(initial=C.PRICE_VECTOR_OPTIONS["no_bias"][1]) # initialize as large value of "no_bias" option in constants

    ability_level = models.StringField(choices=("high", "low"))                             # 
    diagnosis_accuracy_percent = models.IntegerField()                                      # depends on high / low ability
    services_provided_to_all_consumers = models.LongStringField()
    number_of_services_provided = models.IntegerField(initial=0)

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


def setup_player(player: Player):
    # sets up a single player
    if player.round_number == 1:
        # first round setup
        player.participant.number_of_timeouts = 0
        player.participant.is_dropout = False
        player.coins = C.ENDOWMENT
        player.player_color = ["Red", "Aquamarine", "Coral", "Yellow", 
                                "Cyan", "Pink", "Salmon", "Grey",
                                "Lime", "Teal", "Silver", "White"][player.id_in_group-1] #TODO add more colors

        if (player.id_in_group % 2) == 0 :  # id is even
            player.is_expert = True

            # setup expert
            player.ability_level = random.choice(("low", "high"))
            player.diagnosis_accuracy_percent = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT[player.ability_level]


        else:
            # setup consumer
            if random.randint(1, 100) <= C.CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT:
                player.service_needed = "large"
            else:
                player.service_needed = "small"

        return player
    
    else:
        # later rounds setup
        player.is_expert = player.in_round(1).is_expert
        player.player_color = player.in_round(1).player_color
        player.coins = player.in_previous_rounds()[-1].coins

        if player.is_expert:
            player.ability_level = player.in_round(1).ability_level
            player.diagnosis_accuracy_percent = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT[player.ability_level]

            # if single investment decision, use that in all later rounds. Reset if repeated.
            if player.group.treatment_investment_frequency == "once" and player.round_number > C.INVESTMENT_STARTING_ROUND:
                player.investment_decision = player.in_round(C.INVESTMENT_STARTING_ROUND).investment_decision

        else:
            if random.randint(1, 100) <= C.CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT:
                player.service_needed = "large"
            else:
                player.service_needed = "small"


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
        # setup_players(player.subsession)
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

        if player.investment_decision:
            player.coins -= C.INVESTMENT_COST[player.group.treatment_investment_frequency]


    form_model = "player"
    form_fields = ["investment_decision"]

    @staticmethod
    def is_displayed(player):
        # only experts see this page
        if not player.is_expert:
            return False
        
        # display only once if treatment "once"
        if player.group.treatment_investment_frequency == "once":
            return player.round_number == C.INVESTMENT_STARTING_ROUND
        
        # display every round (after set invest starting round) if set to "repeated"
        return player.round_number >= C.INVESTMENT_STARTING_ROUND
    
    @staticmethod
    def js_vars(player: Player):
        return dict(
            investment_cost = C.INVESTMENT_COST[player.group.treatment_investment_frequency]
        )


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
            
    @staticmethod
    def js_vars(player: Player):
        return dict(
            price_vector = C.PRICE_VECTOR_OPTIONS
        )


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
        for p in player.get_others_in_group():
            if (not p.is_expert) and (p.expert_chosen == player.id_in_group):
                consumer = p
                consumer.service_recieved = get_service_from_json_by_id(player.services_provided_to_all_consumers, consumer.id_in_group)
                player.number_of_services_provided += 1
                # print(p.service_recieved)

                # set consumer coin payoff
                if (consumer.service_needed == consumer.service_recieved) or (consumer.service_recieved == "large"):
                    consumer.coins += C.CONSUMER_PAYOFFS["problem_solved"]
                else:
                    consumer.coins += C.CONSUMER_PAYOFFS["problem_remains"]

                # set expert coin payoff and consumer pay price
                if consumer.service_recieved == "small":
                    player.coins += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][2]   # profit small
                    consumer.coins -= C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][0]        # price small
                elif consumer.service_recieved == "large":
                    player.coins += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][3]   # profit large
                    consumer.coins -= C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][1]        # price large



class MatchingWaitPage(WaitPage):

    group_by_arrival_time = True

    title_text = "Matching in progress"
    body_text = "You are currently waiting to be matched with other players. This will only take a minute..."

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        # set treatment
        group.treatment_investment_option = random.choice(["skill", "algo"])
        group.treatment_investment_frequency = random.choice(["once", "repeated"])
        group.treatment_investment_visible = random.choice([True, False])
        print(f"Group treatment set: {group.treatment_investment_option} | {group.treatment_investment_frequency} | {group.treatment_investment_visible}")

        for player in group.get_players():
            player = setup_player(player)


class SetupWaitPage(WaitPage):
    title_text = "Setup in progress..."
    body_text = "You are currently waiting for other players to arrive. This will only take a minute..."

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number != 1
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        # set treatment
        group.treatment_investment_option = group.in_round(1).treatment_investment_option
        group.treatment_investment_frequency = group.in_round(1).treatment_investment_frequency
        group.treatment_investment_visible = group.in_round(1).treatment_investment_visible

        for player in group.get_players():
            player = setup_player(player)



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


page_sequence = [MatchingWaitPage,  # only first round
                 Intro,             # only first round
                 SetupWaitPage,     # all later rounds
                 InvestmentChoice,  # only later rounds
                 ExpertSetPrices,   # Experts | all rounds
                 ConsumerEnterMarket,   # Consumers | all rounds
                 ConsumerWaitPage,      # Consumers | all rounds
                 ConsumerChooseExpert,  # Consumers | all rounds
                 ExpertWaitPage,    # Experts | all rounds
                 ExpertDiagnosisI,  # Experts | all rounds
                 ExpertDiagnosisII, # Experts | all rounds
                 ConsumerWaitPage,  # Consumers | all rounds
                 Results            # all rounds
                 ]

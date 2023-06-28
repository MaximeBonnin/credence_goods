from otree.api import *
import random
import json


doc = """
Credence Goods experiments
"""


class C(BaseConstants):
    # REMEMBER TO COPY ANY CHANGES TO practice_round FOR CORRECT INTRO

    ### DEV VARS FOR TESTING ###
    ENABLE_WAITING_PAGES = True
    RANDOMIZE_DIV_ORDER = True              # randomized order of choice cards on Choose Expert and Diagnosis 1 & 2. Consistent order through all rounds.


    ### STRUCTURAL VARIABLES ###
    NAME_IN_URL = 'credence_goods'
    # colors: #f1eef6, #bdc9e1, #74a9cf, #0570b0
    NUM_ROUNDS = 6
    PLAYERS_PER_GROUP = 6
    NUM_EXPERTS_PER_GROUP = PLAYERS_PER_GROUP // 2                          # consumers = players - experts
    NUM_CONSUMERS_PER_GROUP = PLAYERS_PER_GROUP - NUM_EXPERTS_PER_GROUP

    TIMEOUT_IN_SECONDS = 60 * 4                                             # Investment Explain page is different
    EXPLANATION_TIMEOUT_IN_SECONDS = TIMEOUT_IN_SECONDS * 5
    RESULTS_TIMEOUT_IN_SECONDS = 45
    DROPOUT_AT_GIVEN_NUMBER_OF_TIMEOUTS = 3                                 # players get excluded from the experiment if they have X number of timeouts


    ### ECONOMIC VARIABLES ###

    ENDOWMENT = 0                      

    CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT = 40
    CHANCE_TO_HAVE_SMALL_PROBLEM_IN_PERCENT = 100-CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT

    COST_OF_PROVIDING_SMALL_SERVICE = 20                    # c_k
    COST_OF_PROVIDING_LARGE_SERVICE = 60                    # c_g

    EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT = { 
        "low": 50,
        "high": 75,
        "invested": 90
    }

    EXPERT_PAYOFF_NO_CONSUMER = 10
    CONSUMER_PAYOFFS = {
        "no_market_entry": 10,
        "problem_remains": 0,
        "problem_solved": 150
    }

    INVESTMENT_STARTING_ROUND = 2
    INVESTMENT_COST = {
        "once": 150,
        "repeated": 10
    }

    PRICE_VECTOR_OPTIONS = {
        "bias_small": (80,                                   # price_small
                       100,                                   # price_large
                       80-COST_OF_PROVIDING_SMALL_SERVICE,   # profit_small
                       100-COST_OF_PROVIDING_LARGE_SERVICE),  # profit_large
        "bias_large": (40,
                       100,
                       40-COST_OF_PROVIDING_SMALL_SERVICE,
                       100-COST_OF_PROVIDING_LARGE_SERVICE),
        "no_bias": (60,
                    100,
                    60-COST_OF_PROVIDING_SMALL_SERVICE,
                    100-COST_OF_PROVIDING_LARGE_SERVICE)
    }

    PRICE_MULTIPLIER_AFTER_INVESTING = 1
    PRICE_VECTOR_OPTIONS_MULTIPLIED = {
        "once": {                                   # (price_small, price_large, profit_small, profit_large)
            "bias_small": (
                int(INVESTMENT_COST["once"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_small"][0],
                int(INVESTMENT_COST["once"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_small"][1],
                PRICE_VECTOR_OPTIONS["bias_small"][2],
                PRICE_VECTOR_OPTIONS["bias_small"][3]
                ),
            "bias_large": (
                int(INVESTMENT_COST["once"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_large"][0],
                int(INVESTMENT_COST["once"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_large"][1],
                PRICE_VECTOR_OPTIONS["bias_large"][2],
                PRICE_VECTOR_OPTIONS["bias_large"][3]
                ),
            "no_bias": (
                int(INVESTMENT_COST["once"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["no_bias"][0],
                int(INVESTMENT_COST["once"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["no_bias"][1],
                PRICE_VECTOR_OPTIONS["no_bias"][2],
                PRICE_VECTOR_OPTIONS["no_bias"][3]
                )
        },
        "repeated": {                               # (price_small, price_large, profit_small, profit_large)
            "bias_small": (
                int(INVESTMENT_COST["repeated"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_small"][0],
                int(INVESTMENT_COST["repeated"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_small"][1],
                PRICE_VECTOR_OPTIONS["bias_small"][2],
                PRICE_VECTOR_OPTIONS["bias_small"][3]
                ),
            "bias_large": (
                int(INVESTMENT_COST["repeated"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_large"][0],
                int(INVESTMENT_COST["repeated"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["bias_large"][1],
                PRICE_VECTOR_OPTIONS["bias_large"][2],
                PRICE_VECTOR_OPTIONS["bias_large"][3]
                ),
            "no_bias": (
                int(INVESTMENT_COST["repeated"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["no_bias"][0],
                int(INVESTMENT_COST["repeated"] * PRICE_MULTIPLIER_AFTER_INVESTING) + PRICE_VECTOR_OPTIONS["no_bias"][1],
                PRICE_VECTOR_OPTIONS["no_bias"][2],
                PRICE_VECTOR_OPTIONS["no_bias"][3]
                )
        }
    }

    
class Subsession(BaseSubsession):
    # expert_list = []
    pass


class Player(BasePlayer):
    # vars for excluding dropouts
    is_dropout = models.BooleanField(initial=False)

    is_expert = models.BooleanField(initial=False)
    player_name = models.StringField()
    coins = models.IntegerField(initial=0)
    coins_this_round = models.IntegerField(initial=0)

    # general variables

    # expert variables
    price_vector_chosen = models.StringField(choices=["bias_small", "bias_large", "no_bias"], initial="no_bias")
    price_small_service = models.IntegerField() # initialize as small value of "no_bias" option in constants
    price_large_service = models.IntegerField() # initialize as large value of "no_bias" option in constants

    ability_level = models.StringField(choices=("high", "low"))                             # 
    base_diagnosis_accuracy_percent = models.IntegerField()                                 # depends on high / low ability
    total_diagnosis_accuracy_percent = models.IntegerField()                                # depends on high/low ability and investment
    diagnosis_correct_for_all_patients = models.StringField()                           # json/dict format string
    services_provided_to_all_consumers = models.StringField()                           # json/dict format string 
    number_of_services_provided = models.IntegerField(initial=0)

    investment_decision = models.BooleanField(initial=False)
    ignore_algorithmic_decision_per_consumer = models.StringField()                        # json/dict format string

    # customer variables
    enter_market = models.BooleanField(initial=True)
    expert_chosen = models.IntegerField(initial=0)                                          # this should be a player.id_in_group
    expert_chosen_name = models.StringField()
    service_needed = models.StringField(choices=("small", "large"), initial="none")
    service_recieved = models.StringField(choices=("small", "large", "none"))

    # variables for documentation
    cost_of_providing_small_service =  models.IntegerField(initial=C.COST_OF_PROVIDING_SMALL_SERVICE) # c_k
    cost_of_providing_large_service =  models.IntegerField(initial=C.COST_OF_PROVIDING_LARGE_SERVICE) # c_g

    #dem
    dem_page = models.IntegerField(initial=1)

    # demographics
    dem_risk = models.IntegerField(
        choices=[
            [1, "1"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7"],
            [8, "8"],
            [9, "9"],
            [10, "10"]
        ], widget=widgets.RadioSelectHorizontal, blank=False
    )

    dem_year = models.IntegerField(blank=False, min=1900, max=2023)

    dem_sex = models.IntegerField(
        choices=[
            [1, "Male"],
            [2, "Female"],
            [3, "Other"],
            [4, "Prefer not to answer"]
        ], widget=widgets.RadioSelect, blank=False
    )

    dem_employment = models.IntegerField(
        choices=[
            [1, "Working (paid employee)"],
            [2, "Working (self-employed)"],
            [3, "Not working (temporary layoff from a job)"],
            [4, "Not working (looking for work)"],
            [5, "Not working (retired)"],
            [6, "Not working (diabled)"],
            [7, "Not working (other)"],
            [8, "Prefer not to answer"]
        ], widget=widgets.RadioSelect, blank=False
    )

    dem_education = models.IntegerField(
        choices=[
            [1, "Less than high school degree"],
            [2, "High school graduate (high school diploma or equivalent including GED)"],
            [3, "Some college but no degree"],
            [4, "Associate degree in college (2-year)"],
            [5, "Bachelor's degree in college (4-year)"],
            [6, "Master's degree"],
            [7, "Doctoral degree"],
            [8, "Professional degree (JD, MD)"]
        ], widget=widgets.RadioSelect, blank=False
    )

    dem_ethnicity = models.IntegerField(
        choices=[
            [1, "African American"],
            [2, "American Indian"],
            [3, "Asian"],
            [4, "Hispanic/Latino"],
            [5, "White/Caucasion"],
            [6, "Other"]
        ], widget=widgets.RadioSelect, blank=False
    )



def setup_player(player: Player) -> Player:
    # add multiplier to data
    player.group.treatment_price_multiplier = C.PRICE_MULTIPLIER_AFTER_INVESTING

    # sets up a single player
    if player.round_number == 1:
        ids_of_others_in_group = [p.id_in_group for p in player.get_others_in_group()]
        player.participant.randomized_others_in_group = json.dumps(random.sample(ids_of_others_in_group, len(ids_of_others_in_group)))

        # first round setup
        player.participant.number_of_timeouts = 0
        player.participant.is_dropout = False
        player.coins = C.ENDOWMENT
        player.player_name = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[player.id_in_group-1]

        if (player.participant.is_expert):
            player.is_expert = True

            # setup expert
            player.ability_level = player.participant.ability_level
            player.base_diagnosis_accuracy_percent = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT[player.ability_level]
            player.total_diagnosis_accuracy_percent = player.base_diagnosis_accuracy_percent

            


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
        player.player_name = player.in_round(1).player_name
        player.coins = player.in_previous_rounds()[-1].coins

        if player.is_expert:
            player.ability_level = player.in_round(1).ability_level
            player.base_diagnosis_accuracy_percent = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT[player.ability_level]
            player.total_diagnosis_accuracy_percent = player.base_diagnosis_accuracy_percent # override this later if investment happens

            # if single investment decision, use that in all later rounds. Reset if repeated.
            if player.group.treatment_investment_frequency == "once" and player.round_number > C.INVESTMENT_STARTING_ROUND:
                player.investment_decision = player.in_round(C.INVESTMENT_STARTING_ROUND).investment_decision
                player.total_diagnosis_accuracy_percent = player.in_round(C.INVESTMENT_STARTING_ROUND).total_diagnosis_accuracy_percent

        else:
            if random.randint(1, 100) <= C.CHANCE_TO_HAVE_LARGE_PROBLEM_IN_PERCENT:
                player.service_needed = "large"
            else:
                player.service_needed = "small"


class Group(BaseGroup):
    treatment_investment_option = models.StringField(choices=["skill", "algo"])
    treatment_investment_frequency = models.StringField(choices=["once", "repeated"])
    treatment_skill_visible = models.BooleanField()
    treatment_price_multiplier = models.FloatField(initial=0)





# PAGES


# Transition after matching
class MatchSuccessful(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS


# Explain investment
class InvestmentExplanation(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.EXPLANATION_TIMEOUT_IN_SECONDS
        
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.INVESTMENT_STARTING_ROUND


# Explain investment
class InvestmentExplanation2(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.EXPLANATION_TIMEOUT_IN_SECONDS

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.INVESTMENT_STARTING_ROUND


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
            # player.coins -= C.INVESTMENT_COST[player.group.treatment_investment_frequency]
            player.total_diagnosis_accuracy_percent = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT["invested"]
            player.price_small_service = C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][0]
            
        


    form_model = "player"
    form_fields = ["investment_decision"]

    @staticmethod
    def is_displayed(player):
        # only experts see this page
        if not player.is_expert:
            return False
        
        # display every round until invested
        if player.group.treatment_investment_frequency == "once":
            return (player.round_number >= C.INVESTMENT_STARTING_ROUND) and (not player.investment_decision)
        
        # display every round (after set invest starting round) if set to "repeated"
        return player.round_number >= C.INVESTMENT_STARTING_ROUND
    
    @staticmethod
    def js_vars(player: Player):
        return dict(
            investment_cost = C.INVESTMENT_COST[player.group.treatment_investment_frequency],
            accuracies = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT
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
        if not player.investment_decision:
            player.price_small_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][0]
            player.price_large_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][1]
        else:
            player.price_small_service = C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][0]
            player.price_large_service = C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][1]

        diagnosis_correct_for_all_patients = {}
        for consumer in player.get_others_in_group():
            if not consumer.is_expert:
                diagnosis_correct_for_all_patients[str(consumer.id_in_group)] = int(random.randint(1, 100) <= player.total_diagnosis_accuracy_percent)
        player.diagnosis_correct_for_all_patients = json.dumps(diagnosis_correct_for_all_patients)
        # print(player.diagnosis_correct_for_all_patients)

        return


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
            player.expert_chosen_name = player.group.get_player_by_id(
                player.expert_chosen).player_name
        else:
            player.enter_market = False
            player.coins += C.CONSUMER_PAYOFFS["no_market_entry"]
            
    @staticmethod
    def js_vars(player: Player):
        return dict(
            price_vector = C.PRICE_VECTOR_OPTIONS,
            price_vectors_multi = C.PRICE_VECTOR_OPTIONS_MULTIPLIED,
        )


# Expert diagnosis I
class ExpertDiagnosisI(Page):
    form_model = "player"
    form_fields = ["ignore_algorithmic_decision_per_consumer"]

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
        
        # set diagnosis_correct_for_all_patients based on ignore_algorithmic_decision_per_consumer
        if player.group.treatment_investment_option == "algo":
            diagnosis_correct_for_all_patients = json.loads(player.diagnosis_correct_for_all_patients)
            ignore_algorithmic_decision_per_consumer = json.loads(player.ignore_algorithmic_decision_per_consumer)
            for consumer in player.get_others_in_group():
                if ignore_algorithmic_decision_per_consumer.get(str(consumer.id_in_group), 0):
                    diagnosis_correct_for_all_patients[str(consumer.id_in_group)] = int(random.randint(1, 100) <= player.base_diagnosis_accuracy_percent)
            player.diagnosis_correct_for_all_patients = json.dumps(diagnosis_correct_for_all_patients)

    @staticmethod
    def js_vars(player: Player):
        return dict(
            diagnosis_correct_for_all_patients = json.loads(player.diagnosis_correct_for_all_patients),
            price_vectors=C.PRICE_VECTOR_OPTIONS
        )

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
            price_vectors_multi = C.PRICE_VECTOR_OPTIONS_MULTIPLIED,
            diagnosis_correct_for_all_patients = json.loads(player.diagnosis_correct_for_all_patients),
            ignore_algorithmic_decision_per_consumer = json.loads(player.ignore_algorithmic_decision_per_consumer)
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

        
class CalculateResults(Page):
    @staticmethod
    def get_timeout_seconds(player):
        return 3 #TODO change this back  

    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        if not player.is_expert:
            return

        # apply service
        for p in player.get_others_in_group():
            if (not p.is_expert) and (p.expert_chosen == player.id_in_group):
                
                consumer = p
                consumer.service_recieved = get_service_from_json_by_id(player.services_provided_to_all_consumers, consumer.id_in_group)
                player.number_of_services_provided += 1

                # set consumer coin payoff
                if (consumer.service_needed == consumer.service_recieved) or (consumer.service_recieved == "large"):
                    consumer.coins += C.CONSUMER_PAYOFFS["problem_solved"]
                    consumer.coins_this_round += C.CONSUMER_PAYOFFS["problem_solved"]
                else:
                    consumer.coins += C.CONSUMER_PAYOFFS["problem_remains"]
                    consumer.coins_this_round += C.CONSUMER_PAYOFFS["problem_remains"]

                # set expert coin payoff and consumer pay price
                if player.investment_decision:
                    # multiplied price vector
                    if consumer.service_recieved == "small":
                        player.coins += C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][2]   # profit small
                        consumer.coins -= C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][0]        # price small

                        player.coins_this_round += C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][2]   # profit small
                        consumer.coins_this_round -= C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][0]        # price small
                    
                    elif consumer.service_recieved == "large":
                        player.coins += C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][3]   # profit large
                        consumer.coins -= C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][1]        # price large

                        player.coins_this_round += C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][3]   # profit large
                        consumer.coins_this_round -= C.PRICE_VECTOR_OPTIONS_MULTIPLIED[player.group.treatment_investment_frequency][player.price_vector_chosen][1]        # price large

                else:
                    # normal price vector
                    if consumer.service_recieved == "small":
                        player.coins += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][2]   # profit small
                        consumer.coins -= C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][0]        # price small

                        player.coins_this_round += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][2]   # profit small
                        consumer.coins_this_round -= C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][0]        # price small

                    elif consumer.service_recieved == "large":
                        player.coins += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][3]   # profit large
                        consumer.coins -= C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][1]        # price large

                        player.coins_this_round += C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][3]   # profit large
                        consumer.coins_this_round -= C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][1]        # price large

        if player.number_of_services_provided == 0:
            # small payoff for when expert not chosen
            player.coins += C.EXPERT_PAYOFF_NO_CONSUMER
            player.coins_this_round += C.EXPERT_PAYOFF_NO_CONSUMER


def group_by_arrival_time_method(subsession, waiting_players):

    experts = [e for e in waiting_players if e.participant.is_expert]
    experts_low = [l for l in experts if l.participant.ability_level == "low"]
    experts_high = [h for h in experts if h.participant.ability_level == "high"]
    number_of_low_ability_experts_waiting = len(experts_low)
    number_of_high_ability_experts_waiting = len(experts_high)

    number_of_low_ability_needed = 2                               # integer division 
    number_of_high_ability_needed = C.NUM_EXPERTS_PER_GROUP - number_of_low_ability_needed      # get full group

    consumers = [c for c in waiting_players if not c.participant.is_expert]
    number_of_consumers_waiting = len(consumers)
    number_of_consumers_needed = C.NUM_CONSUMERS_PER_GROUP

    print(f"Currently waiting:\n-> {number_of_low_ability_experts_waiting}/{number_of_low_ability_needed} low-ability experts \n" +
          f"-> {number_of_high_ability_experts_waiting}/{number_of_high_ability_needed} high-ability experts \n" + 
          f"-> {number_of_consumers_waiting}/{number_of_consumers_needed} Consumers")
    
    # create group when all roles can be filled
    if (number_of_low_ability_experts_waiting >= number_of_low_ability_needed) and (number_of_high_ability_experts_waiting >= number_of_high_ability_needed) and (number_of_consumers_waiting >= number_of_consumers_needed):
        print('Creating group...')
        grouped_players = experts_low[0:number_of_low_ability_needed] + experts_high[0:number_of_high_ability_needed] + consumers[0:number_of_consumers_needed]
        return grouped_players
    
    print('not enough players yet to create a group')


class MatchingWaitPage(WaitPage):

    template_name = 'credence_goods/MatchingWaitPage.html'

    group_by_arrival_time = True

    title_text = "Matching in progress"
    body_text = r"You are currently waiting to be matched with other players. Please keep this browser tab active (🟢 symbol) in order to be matched."

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        # set treatment
        group.treatment_investment_option = random.choice(["skill", "algo"])
        if group.subsession.session.config['treatment_investment_frequency'] == "random":
            group.treatment_investment_frequency = random.choice(["once", "repeated"])
        else:
            group.treatment_investment_frequency = group.subsession.session.config['treatment_investment_frequency']
        group.treatment_skill_visible = group.subsession.session.config['treatment_skill_visible']
        print(f"Group treatment set: {group.treatment_investment_option} | {group.treatment_investment_frequency} | {group.treatment_skill_visible}")

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
        group.treatment_skill_visible = group.in_round(1).treatment_skill_visible

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
    template_name = 'credence_goods/ConsumerWaitPage.html'

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
            return C.RESULTS_TIMEOUT_IN_SECONDS
    form_model = "player"
    form_fields = []

    @staticmethod
    def before_next_page(player, timeout_happened):
        # handle timeout and setting is_dropout status
        if timeout_happened:
            print("Timeout happened. No timeout given because results page.")

    @staticmethod
    def js_vars(player):
        return dict(
            price_vectors=C.PRICE_VECTOR_OPTIONS
        )


class Demographics(Page):
    form_model = "player"


    @staticmethod
    def is_displayed(player: Player):
        # last round
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def get_form_fields(player: Player):
        if player.dem_page == 1:
            return ["dem_risk"]
        elif player.dem_page == 2:
            return ["dem_year", "dem_sex", "dem_employment", "dem_education", "dem_ethnicity"]

    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.coins > 0:
            player.payoff += player.coins * player.subsession.session.config["real_world_currency_per_point"]
        else:
            player.payoff = 0

        player.dem_page += 1
    

class PayoffCode(Page):
    @staticmethod
    def is_displayed(player: Player):
        # last round
        return player.round_number == C.NUM_ROUNDS
    

class TimeoutExclusion(Page):
    @staticmethod
    def is_displayed(player: Player):
        # last round
        return player.round_number == C.NUM_ROUNDS and player.is_dropout
    
    

page_sequence = [MatchingWaitPage,          # only first round
                 MatchSuccessful,           # only first round
                 SetupWaitPage,             # all later rounds
                 InvestmentExplanation,     # only invesment starting round
                 InvestmentExplanation2,    # only invesment starting round
                 InvestmentChoice,          # only later rounds
                 ExpertSetPrices,           # Experts | all rounds
                 ConsumerWaitPage,          # Consumers | all rounds
                 ConsumerChooseExpert,      # Consumers | all rounds
                 ExpertDiagnosisI,          # Experts | all rounds
                 ExpertDiagnosisII,         # Experts | all rounds
                 ConsumerWaitPage,          # Consumers | all rounds
                 ExpertWaitPage,            # Experts | all rounds
                 CalculateResults,          # all rounds
                 Results,                   # all rounds
                 TimeoutExclusion,          # last round and player timed out
                 Demographics,              # last round
                 Demographics,              # last round
                 PayoffCode                 # last round
                 ]

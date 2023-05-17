from otree.api import *
import random
import json


doc = """
Your app description
"""


class C(BaseConstants):
    # DEV VARS FOR TESTING
    ENABLE_WAITING_PAGES = True

    #TODO REMEMBER TO COPY ANY CHANGES TO practice_round FOR CORRECT INTRO

    # colors: #f1eef6, #bdc9e1, #74a9cf, #0570b0

    NAME_IN_URL = 'credence_goods'
    NUM_ROUNDS = 8
    PLAYERS_PER_GROUP = 6
    TIMEOUT_IN_SECONDS = 1500               # Investment Explain page is different
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
    # expert_list = []
    pass


class Player(BasePlayer):
    # vars for excluding dropouts
    is_dropout = models.BooleanField(initial=False)

    is_expert = models.BooleanField(initial=False)
    player_name = models.StringField()
    coins = models.IntegerField(initial=0)

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


def setup_player(player: Player) -> Player:
    # sets up a single player
    if player.round_number == 1:
        # first round setup
        player.participant.number_of_timeouts = 0
        player.participant.is_dropout = False
        player.coins = C.ENDOWMENT
        player.player_name = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[player.id_in_group-1]

        if (player.id_in_group % 2) == 0 :  # id is even
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
            player.total_diagnosis_accuracy_percent = player.base_diagnosis_accuracy_percent #TODO override this later if investment happens

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





# PAGES


# Explain investment
class InvestmentExplanation(Page):
    # handle timer for dropouts
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return C.TIMEOUT_IN_SECONDS * 5
        
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
            player.coins -= C.INVESTMENT_COST[player.group.treatment_investment_frequency]
            player.total_diagnosis_accuracy_percent = C.EXPERT_ABILITY_LEVEL_TO_DIAGNOSIS_ACCURACY_PERCENT["invested"]


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
        player.price_small_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][0]
        player.price_large_service = C.PRICE_VECTOR_OPTIONS[player.price_vector_chosen][1]

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
            
    @staticmethod
    def js_vars(player: Player):
        return dict(
            price_vector = C.PRICE_VECTOR_OPTIONS
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


def group_by_arrival_time_method(subsession, waiting_players):

    experts = [e for e in waiting_players if e.participant.is_expert]
    consumers = [c for c in waiting_players if not c.participant.is_expert]

    print(f"Currently waiting: {len(experts)}/{C.NUM_EXPERTS_PER_GROUP} Experts | {len(consumers)}/{C.NUM_CONSUMERS_PER_GROUP} Consumers")
    if (len(experts) >= C.NUM_EXPERTS_PER_GROUP) and (len(consumers) >= C.NUM_CONSUMERS_PER_GROUP):
        print('Creating group...')
        grouped_players = experts[0:C.NUM_EXPERTS_PER_GROUP] + consumers[0:C.NUM_CONSUMERS_PER_GROUP]
        return grouped_players
    
    print('not enough players yet to create a group')


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
            return C.TIMEOUT_IN_SECONDS
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

    @staticmethod
    def is_displayed(player: Player):
        # last round
        return player.round_number != C.NUM_ROUNDS


class FinalResults(Page):
    @staticmethod
    def js_vars(player):
        return dict(
            price_vectors=C.PRICE_VECTOR_OPTIONS
        )

    @staticmethod
    def is_displayed(player: Player):
        # last round
        return player.round_number == C.NUM_ROUNDS
    
page_sequence = [MatchingWaitPage,  # only first round
                 SetupWaitPage,     # all later rounds
                 InvestmentExplanation, # only invesment starting round
                 InvestmentChoice,  # only later rounds
                 ExpertSetPrices,   # Experts | all rounds
                 ConsumerWaitPage,      # Consumers | all rounds
                 ConsumerChooseExpert,  # Consumers | all rounds
                 ExpertWaitPage,    # Experts | all rounds
                 ExpertDiagnosisI,  # Experts | all rounds
                 ExpertDiagnosisII, # Experts | all rounds
                 ConsumerWaitPage,  # Consumers | all rounds
                 Results,           # all rounds
                 FinalResults       # last round
                 ]

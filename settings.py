from os import environ

SESSION_CONFIGS = [
    dict(
        name='credence_goods_skill_visible',
        app_sequence=["credence_goods_welcome",'practice_round', 'credence_goods'],
        num_demo_participants=24,
        treatment_skill_visible = True,
    ), dict(
        name='credence_goods_skill_not_visible',
        app_sequence=["credence_goods_welcome",'practice_round', 'credence_goods'],
        num_demo_participants=24,
        treatment_skill_visible = False,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.006, participation_fee=4.50, doc="", treatment_investment_frequency="repeated"
)

PARTICIPANT_FIELDS = ['treatment_skill_visible', "is_expert", "number_of_timeouts", "is_dropout", "ability_level", "randomized_others_in_group", "completion_code"]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '6639616511460'

"""ShopPinkki state machine — 9 states using transitions library."""

import logging
from transitions import Machine

logger = logging.getLogger(__name__)

STATES = [
    'IDLE',
    'REGISTERING',
    'TRACKING',
    'SEARCHING',
    'WAITING',
    'ITEM_ADDING',
    'GUIDING',
    'RETURNING',
    'ALARM',
]

TRANSITIONS = [
    {'trigger': 'start_session',      'source': 'IDLE',          'dest': 'REGISTERING'},
    {'trigger': 'registration_done',  'source': 'REGISTERING',   'dest': 'TRACKING'},
    {'trigger': 'owner_lost',         'source': 'TRACKING',      'dest': 'SEARCHING'},
    {'trigger': 'owner_found',        'source': 'SEARCHING',     'dest': 'TRACKING'},
    {'trigger': 'to_waiting',         'source': ['TRACKING', 'SEARCHING'], 'dest': 'WAITING'},
    {'trigger': 'to_tracking',        'source': 'WAITING',       'dest': 'TRACKING'},
    {'trigger': 'to_item_adding',     'source': 'WAITING',       'dest': 'ITEM_ADDING'},
    {'trigger': 'item_adding_done',   'source': 'ITEM_ADDING',   'dest': 'WAITING'},
    {'trigger': 'navigate_to',        'source': 'WAITING',       'dest': 'GUIDING'},
    {'trigger': 'guiding_done',       'source': 'GUIDING',       'dest': 'WAITING'},
    {'trigger': 'start_returning',    'source': 'WAITING',       'dest': 'RETURNING'},
    {'trigger': 'session_ended',      'source': 'RETURNING',     'dest': 'IDLE'},
    {'trigger': 'battery_low',        'source': '*',             'dest': 'ALARM'},
    {'trigger': 'zone_out',           'source': '*',             'dest': 'ALARM'},
    {'trigger': 'payment_error',      'source': 'WAITING',       'dest': 'ALARM'},
    {'trigger': 'dismiss_to_idle',    'source': 'ALARM',         'dest': 'IDLE'},
    {'trigger': 'dismiss_to_waiting', 'source': 'ALARM',         'dest': 'WAITING'},
    {'trigger': 'admin_force_idle',   'source': '*',             'dest': 'IDLE'},
]


class ShopPinkkiSM:
    """ShopPinkki state machine wrapper."""

    def __init__(self):
        self.current_alarm = None
        self._battery_alarm_fired = False

        self._machine = Machine(
            model=self,
            states=STATES,
            transitions=TRANSITIONS,
            initial='IDLE',
            ignore_invalid_triggers=False,
            after_state_change='_after_state_change',
        )

    def _after_state_change(self):
        logger.info(f'[SM] state → {self.state}')

    # --- on_enter callbacks (stubs) ---

    def on_enter_IDLE(self):
        logger.info('[SM] on_enter_IDLE')

    def on_enter_REGISTERING(self):
        logger.info('[SM] on_enter_REGISTERING')

    def on_enter_TRACKING(self):
        logger.info('[SM] on_enter_TRACKING')

    def on_enter_SEARCHING(self):
        logger.info('[SM] on_enter_SEARCHING')

    def on_enter_WAITING(self):
        logger.info('[SM] on_enter_WAITING')

    def on_enter_ITEM_ADDING(self):
        logger.info('[SM] on_enter_ITEM_ADDING')

    def on_enter_GUIDING(self):
        logger.info('[SM] on_enter_GUIDING')

    def on_enter_RETURNING(self):
        logger.info('[SM] on_enter_RETURNING')

    def on_enter_ALARM(self):
        logger.info(f'[SM] on_enter_ALARM alarm={self.current_alarm}')

    # --- on_exit callbacks (stubs) ---

    def on_exit_IDLE(self):
        logger.info('[SM] on_exit_IDLE')

    def on_exit_REGISTERING(self):
        logger.info('[SM] on_exit_REGISTERING')

    def on_exit_TRACKING(self):
        logger.info('[SM] on_exit_TRACKING')

    def on_exit_SEARCHING(self):
        logger.info('[SM] on_exit_SEARCHING')

    def on_exit_WAITING(self):
        logger.info('[SM] on_exit_WAITING')

    def on_exit_ITEM_ADDING(self):
        logger.info('[SM] on_exit_ITEM_ADDING')

    def on_exit_GUIDING(self):
        logger.info('[SM] on_exit_GUIDING')

    def on_exit_RETURNING(self):
        logger.info('[SM] on_exit_RETURNING')

    def on_exit_ALARM(self):
        logger.info('[SM] on_exit_ALARM')

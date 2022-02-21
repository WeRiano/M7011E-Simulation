from time import sleep
from typing import Dict
import threading

from .delta import Delta
from .state import State


class Manager:
    instances: Dict[int, Delta] = {}

    @staticmethod
    def set_delta(delta, user_id):
        if not Manager.__sim_exists(user_id):
            Manager.__start_instance(user_id)
        result = Manager.instances[user_id].set_delta(delta)
        return result

    @staticmethod
    def set_ratios(saving, using, user_id):
        if not Manager.__sim_exists(user_id):
            Manager.__start_instance(user_id)
        result = Manager.instances[user_id].set_ratios(saving, using)
        return result

    @staticmethod
    def get_conditions(filter_slug, user_id):
        if not Manager.__sim_exists(user_id):
            Manager.__start_instance(user_id)
        state_cond = Manager.instances[user_id].get_conditions(filter_slug)
        delta_cond = Manager.instances[user_id].get_state().get_conditions(filter_slug)
        return {**state_cond, **delta_cond}

    @staticmethod
    def restart_instance(user_id):
        if not Manager.__sim_exists(user_id):
            Manager.__start_instance(user_id)
        else:
            # Exact same as in __start_instance() except we don't have to boot up a thread running the driver, since
            # it is already running
            state = State()
            delta = Delta(state, 0, 1, 1)
            delta.tick_hour()
            delta.update_state()
            Manager.instances[user_id] = delta

    @staticmethod
    def __operation_wrapper(user_id, manager_operation, *operation_params):
        if Manager.__sim_exists(user_id):
            op_result = Manager.instances[user_id].manager_operation(*operation_params)
            return op_result
        else:
            Manager.__start_instance(user_id)
            op_result = manager_operation(*operation_params)
            return op_result

    @staticmethod
    def __instance_driver(delta):
        while True:
            sleep(delta.get_delta())
            delta.tick_hour()
            delta.update_state()

    @staticmethod
    def __start_instance(user_id):
        state = State()
        delta = Delta(state, 0, 1, 1)
        delta.tick_hour()
        delta.update_state()
        Manager.instances[user_id] = delta
        thread = threading.Thread(target=Manager.__instance_driver, args=(delta,), name=str(user_id))
        thread.start()

    # Checks if the given simulation is running
    @staticmethod
    def __sim_exists(user_id):
        return user_id in Manager.instances

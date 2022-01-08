import threading
from requests import get as request_get
from time import sleep
from typing import Dict

from Simulation.delta import Delta
from Simulation.state import State


class Manager:

    instances: Dict[int, Delta] = {}

    @staticmethod
    def set_delta(auth_token, delta):
        user_id = Manager.__request_get_user_id(auth_token)
        try:
            Manager.instances[user_id].set_delta(delta)
        except KeyError:
            Manager.__start_instance(user_id)
            Manager.instances[user_id].set_delta(delta)

    @staticmethod
    def set_ratios(saving, using, auth_token):
        user_id = Manager.__request_get_user_id(auth_token)
        try:
            Manager.instances[user_id].set_ratios(saving, using)
        except KeyError:
            Manager.__start_instance(user_id)
            Manager.instances[user_id].set_ratios(saving, using)

    @staticmethod
    def get_conditions(filter_slug, auth_token):
        user_id = Manager.__request_get_user_id(auth_token)
        try:
            state_cond = Manager.instances[user_id].get_state().get_conditions(filter_slug)
            delta_cond = Manager.instances[user_id].get_conditions(filter_slug)
            return {**state_cond, **delta_cond}
        except KeyError:
            Manager.__start_instance(user_id)
            state_cond = Manager.instances[user_id].get_state().get_conditions(filter_slug)
            delta_cond = Manager.instances[user_id].get_conditions(filter_slug)
            return {**state_cond, **delta_cond}

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

    @staticmethod
    def __request_get_total_users():
        # TODO: Do not hardcode urls
        url = "http://" + os.environ.get("BACKEND_IP", "127.0.0.1") + ":7999/auth/users/get_total/"
        r = request_get(url)
        return r.json()["number_of_users"]

    @staticmethod
    def __request_get_user_id(token_header):
        # TODO: Do not hardcode urls
        url = "http://" + os.environ.get("BACKEND_IP", "127.0.0.1") + ":7999/auth/users/get_profile/"
        header = {
            "Authorization": token_header
        }
        r = request_get(url, headers=header)
        try:
            return r.json()['id']
        except KeyError:
            return -1

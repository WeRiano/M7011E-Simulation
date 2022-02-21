from requests import get as request_get
import os


def request_get_user_info(token_header):
    url = "http://" + os.environ.get("BACKEND_IP", "127.0.0.1") + ":7999/api/version/1/users/get_profile/"
    header = {
        "Authorization": token_header
    }
    r = request_get(url, headers=header)
    return r.json()


def request_get_all_users(admin_token_header):
    url = "http://" + os.environ.get("BACKEND_IP", "127.0.0.1") + ":7999/api/version/1/admin/get_all_users/"
    header = {
        "Authorization": admin_token_header
    }
    r = request_get(url, headers=header)
    return r.json()

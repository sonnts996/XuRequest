# coding=utf8
import json

import requests

from src.main.python.model.APIResponse import APIResponse


def post(url, api, param):
    r = requests.post(url=url + api, json=param)
    try:
        res = json.loads(r.content.decode("utf-8"))
    except Exception as ex:
        res = r.content.decode("utf-8")
    data = APIResponse()
    data.setHeader(dict(r.headers))
    data.setStatus(r.status_code)
    data.setContent(res)
    data.setURL(r.url)
    return data


def post_param(url, api, param):
    r = requests.post(url=url + api, json=param, params=param)
    try:
        res = json.loads(r.content.decode("utf-8"))
    except Exception as ex:
        print(ex)
        res = r.content.decode("utf-8")
    data = APIResponse()
    data.setHeader(dict(r.headers))
    data.setStatus(r.status_code)
    data.setContent(res)
    data.setURL(r.url)
    return data


def get(url, api, param):
    r = requests.get(url=url + api, params=param)
    try:
        res = json.loads(r.content.decode("utf-8"))
    except Exception as ex:
        res = r.content.decode("utf-8")
    data = APIResponse()
    data.setHeader(dict(r.headers))
    data.setStatus(r.status_code)
    data.setContent(res)
    data.setURL(r.url)
    return data


def print_response(r):
    if r >= 500:
        return "Server error!!!"
    elif r >= 400:
        return "Client error!!!"
    elif r >= 300:
        return "Redirects!!!"
    elif r >= 200:
        return "Success!!!"
    elif r >= 100:
        return "Informational!!!"
    else:
        return "No Response"

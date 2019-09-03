import os
import configparser
from .exceptions import ExoIncompleteAuthorisation


config = configparser.ConfigParser()
current_path = os.path.abspath('')
config.read(current_path+'/.env')

ip_address = config['DEFAULT']['EXO_IP']
port = config['DEFAULT']['EXO_PORT']

EXO_URL = "http://" + ip_address + ":" + port

try:
    LOGS_DIRECTORY = config['DEFAULT']['LOGS']
except KeyError:
    LOGS_DIRECTORY = "logs"

try:
    CACHE_DIRECTORY = config['DEFAULT']['LOGS']
except KeyError:
    CACHE_DIRECTORY = "caching"

try:
    EXO_USERNAME = config['AUTH']['EXO_USERNAME']
except KeyError:
    EXO_USERNAME = os.environ.get('EXO_USERNAME')

try:
    EXO_PASSWORD = config['AUTH']['EXO_PASSWORD']
except KeyError:
    EXO_PASSWORD = os.environ.get('EXO_PASSWORD')

try:
    EXO_API_KEY = config['AUTH']['EXO_API_KEY']
except KeyError:
    EXO_API_KEY = os.environ.get('EXO_API_KEY')

try:
    EXO_TOKEN = config['AUTH']['EXO_TOKEN']
except KeyError:
    EXO_TOKEN = os.environ.get('EXO_TOKEN')

if None in [EXO_USERNAME, EXO_PASSWORD, EXO_API_KEY, EXO_TOKEN]:
    raise ExoIncompleteAuthorisation("Error")

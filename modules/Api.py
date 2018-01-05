import requests
import logging
import time
import json
from collections import namedtuple
from pprint import pprint

class Api(namedtuple('Api', ['url', 'token'])):
  def postReport(self, report):
    pprint(report)
    success = False
    attempts = 0
    while not success and attempts < 5:
      attempts += 1
      try:
        response = requests.post(self.url + 'irwin/report?api_key=' + self.token, json=report)
        if response.status_code == 200:
          success = True
        else:
          logging.warning(str(response.status_code) + ': Failed to post player report')
          logging.warning(json.dumps(report))
          if response.status_code == 413:
            return
          logging.debug('Trying again in 60 sec')
          time.sleep(60)
      except requests.ConnectionError:
        logging.warning("CONNECTION ERROR: Failed to post report.")
        logging.debug("Trying again in 30 sec")
        time.sleep(30)
      except requests.exceptions.SSLError:
        logging.warning("SSL ERROR: Failed to post report.")
        logging.debug("Trying again in 30 sec")
        time.sleep(30)
      except ValueError:
        logging.warning("VALUE ERROR: Failed to post report.")
        logging.debug("Trying again in 30 sec")
        time.sleep(30)

  def getPlayerData(self, userId):
    success = False
    attempts = 0
    while not success and attempts < 5:
      attempts += 1
      try:
        response = requests.get(self.url+'irwin/'+userId+'/assessment?api_key='+self.token)
        success = True
      except requests.ConnectionError:
        logging.warning('CONNECTION ERROR: Failed to pull assessment data')
        logging.debug('Trying again in 30 sec')
        time.sleep(30)
      except requests.exceptions.SSLError:
        logging.warning('SSL ERROR: Failed to pull assessment data')
        logging.debug('Trying again in 30 sec')
        time.sleep(30)
    try:
      return json.loads(response.text)
    except ValueError:
      return {}

  def getNextPlayerId(self):
    success = False
    attempts = 0
    while not success and attempts < 5:
      attempts += 1
      try:
        response = requests.get(self.url+'irwin/request?api_key='+self.token)
        if response.status_code == 200:
          success = True
        else:
          logging.warning(str(response.status_code) + ': Failed get to new player name')
          logging.debug('Trying again in 60 sec')
          time.sleep(60)
      except requests.ConnectionError:
        logging.warning('CONNECTION ERROR: Failed to get new player name')
        logging.debug('Trying again in 30 sec')
        time.sleep(30)
      except requests.exceptions.SSLError:
        logging.warning('SSL ERROR: Failed to get new player name')
        logging.debug('Trying again in 30 sec')
        time.sleep(30)
    try:
      return response.text
    except ValueError:
      return None
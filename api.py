import requests
from future import standard_library
standard_library.install_aliases()
from builtins import object
import sys
import time
from datetime import datetime
from dateutil import tz
import requests
import json
from urllib.parse import quote_plus

from qgis.PyQt import QtWidgets, QtCore

from qgis.utils import iface

from .worker import AbstractWorker, start_worker

from . import log

API_URL = 'http://misland-africa.oss-online.org:1337/api'
TIMEOUT = 20

def get_user_email(warn=True):
    email = QtCore.QSettings().value("MISLANDAFRICA/email", None)
    if warn and email is None:
        QtWidgets.QMessageBox.critical(None,
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Please register with MISLANDAFRICA before using this function."))
        return None
    else:
        return email

def get_access_token(warn=True):
    token = QtCore.QSettings().value("MISLANDAFRICA/token", None)
    if token is None:
        return None
    return token
###############################################################################
# Threading functions for calls to requests

def login(email=None, password=None):
    if (email == None):
        email = get_user_email()
    if (password == None):
        password = QtCore.QSettings().value("MISLANDAFRICA/password", None)
    if not email or not password:
        log('API unable to login - check username/password')
        QtWidgets.QMessageBox.critical(None,
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Unable to login to MISLAND-AFRICA. Check your username and password."))
        return None
    print(password)
    print(email)
    try:
        # resp = call_api('/auth', method='post', payload={"email": email, "password": password})
        resp = requests.post(API_URL+ "/login/", json={"email": email, "password": password})
        
        if resp.status_code == 200:
            print("Access Token:\t{}".format(resp.json().get("token")))
            QtCore.QSettings().setValue("MISLANDAFRICA/email", email)
            QtCore.QSettings().setValue("MISLANDAFRICA/password", password)
            QtCore.QSettings().setValue("MISLANDAFRICA/token", resp.json().get("token"))
            return resp
            
        elif str(resp.status_code).startswith("5"):
            log("Could not connect to the MISLANDAFRICA server due to a server error. Error code: {}".format(resp.status_code))
            QtWidgets.QMessageBox.critical(None,
                                    QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                    QtWidgets.QApplication.translate("MISLANDAFRICA", "Could not connect to the MISLAND-AFRICA server due to a server error. Error code: {}".format(resp.status_code)))
            return None
        elif resp.json().get('non_field_errors') is not None:
            log(resp.json().get('non_field_errors')[0])
            QtWidgets.QMessageBox.critical(None,
                                    QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                    QtWidgets.QApplication.translate("MISLANDAFRICA", resp.json().get('non_field_errors')[0]))
            return None
        else:
            log("Could not login. Error code: {}".format(resp.status_code))
            QtWidgets.QMessageBox.critical(None,
                                    QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                    QtWidgets.QApplication.translate("MISLANDAFRICA", "Could not login. Error code: {}".format(resp.status_code)))
            return None
    
    except requests.exceptions.ConnectionError:
        log('API unable to access server - check internet connection')
        QtWidgets.QMessageBox.critical(None,
                                    QtWidgets.QApplication.translate("MISLAND", "Error"),
                                    QtWidgets.QApplication.translate("MISLAND", u"Unable to login to MISLAND-AFRICA server. Check your internet connection."))
        resp = None
    except requests.exceptions.Timeout:
        log('API unable to login - general error')
        QtWidgets.QMessageBox.critical(None,
                                    QtWidgets.QApplication.translate("MISLAND", "Error"),
                                    QtWidgets.QApplication.translate("MISLAND", u"Unable to connect to the MISLAND-AFRICA server."))
        resp = None
        
        


def fetchRaster(endpoint, payload):
    token = get_access_token()
    resp = requests.post(API_URL+ endpoint, json=payload, headers={'Authorization': 'Bearer {}'.format(token)})
    
    if resp.status_code == 200:
        return resp
        
    elif str(resp.status_code).startswith("5"):
        log("Could not connect to the MISLANDAFRICA server due to a server error. Error code: {}".format(resp.status_code))
        QtWidgets.QMessageBox.critical(None,
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Could not connect to the MISLAND-AFRICA server due to a server error. Error code: {}".format(resp.status_code)))
        return None
    elif resp.json().get('non_field_errors') is not None:
        log(resp.json().get('non_field_errors')[0])
        QtWidgets.QMessageBox.critical(None,
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", resp.json().get('non_field_errors')[0]))
        return None
    else:
        log("Could not login. Error code: {}".format(resp.status_code))
        QtWidgets.QMessageBox.critical(None,
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Error"),
                                   QtWidgets.QApplication.translate("MISLANDAFRICA", "Could not login. Error code: {}".format(resp.status_code)))
        return None
      

    

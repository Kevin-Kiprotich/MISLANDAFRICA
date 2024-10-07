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

from MISLANDAFRICA.worker import AbstractWorker, start_worker

from MISLANDAFRICA import log

API_URL = 'http://misland-africa.oss-online.org/misland_api'
TIMEOUT = 20

def get_user_email(warn=True):
    email = QtCore.QSettings().value("MISLAND/email", None)
    if warn and email is None:
        QtWidgets.QMessageBox.critical(None,
                                   QtWidgets.QApplication.translate("MISLAND", "Error"),
                                   QtWidgets.QApplication.translate("MISLAND", "Please register with MISLAND before using this function."))
        return None
    else:
        return email

###############################################################################
# Threading functions for calls to requests


class RequestWorker(AbstractWorker):
    """worker, implement the work method here and raise exceptions if needed"""

    def __init__(self, url, method, payload, headers):
        AbstractWorker.__init__(self)
        self.url = url
        self.method = method
        self.payload = payload
        self.headers = headers

    def work(self):
        self.toggle_show_progress.emit(False)
        self.toggle_show_cancel.emit(False)
        if self.method == 'get':
            resp = requests.get(self.url, json=self.payload, headers=self.headers, timeout=TIMEOUT)
        elif self.method == 'post':
            resp = requests.post(self.url, json=self.payload, headers=self.headers, timeout=TIMEOUT)
        elif self.method == 'update':
            resp = requests.update(self.url, json=self.payload, headers=self.headers, timeout=TIMEOUT)
        elif self.method == 'delete':
            resp = requests.delete(self.url, json=self.payload, headers=self.headers, timeout=TIMEOUT)
        elif self.method == 'patch':
            resp = requests.patch(self.url, json=self.payload, headers=self.headers, timeout=TIMEOUT)
        elif self.method == 'head':
            resp = requests.head(self.url, json=self.payload, headers=self.headers, timeout=TIMEOUT)
        else:
            raise ValueError("Unrecognized method: {}".format(self.method))
            resp = None
        return resp


class Request(object):
    def __init__(self, url, method='get', payload=None, headers={}, server_name='Land Degradation Monitoring Service'):
        self.resp = None
        self.exception = None

        self.url = url
        self.method = method
        self.payload = payload
        self.headers = headers
        self.server_name = server_name

    def start(self):
        try:
            worker = RequestWorker(self.url, self.method, self.payload, self.headers)
            pause = QtCore.QEventLoop()
            worker.finished.connect(pause.quit)
            worker.successfully_finished.connect(self.save_resp)
            worker.error.connect(self.save_exception)
            start_worker(worker, iface, QtWidgets.QApplication.translate("MISLAND", u'Contacting {} server...'.format(self.server_name)))
            pause.exec_()
            if self.get_exception():
                raise self.get_exception()
        except requests.exceptions.ConnectionError:
            log('API unable to access server - check internet connection')
            QtWidgets.QMessageBox.critical(None,
                                       QtWidgets.QApplication.translate("MISLAND", "Error"),
                                       QtWidgets.QApplication.translate("MISLAND", u"Unable to login to {} server. Check your internet connection.".format(self.server_name)))
            resp = None
        except requests.exceptions.Timeout:
            log('API unable to login - general error')
            QtWidgets.QMessageBox.critical(None,
                                       QtWidgets.QApplication.translate("MISLAND", "Error"),
                                       QtWidgets.QApplication.translate("MISLAND", u"Unable to connect to {} server.".format(self.server_name)))
            resp = None

    def save_resp(self, resp):
        self.resp = resp

    def get_resp(self):
        return self.resp

    def save_exception(self, exception):
        self.exception = exception

    def get_exception(self):
        return self.exception

###############################################################################
# Other helper functions for api calls


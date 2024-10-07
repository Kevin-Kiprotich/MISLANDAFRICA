from qgis.PyQt.QtWidgets import QMessageBox

from MISLANDAFRICA import log
import requests
URL_PATH = "http://41.227.30.136:1337"

"""
    This function retrieves level 0 admin boundaries to be used in the country comboboxes.
"""

def get_Adm0():
    path = "/api/vect0/?include=all"
    #create a response object
    try:
        response = requests.get(URL_PATH + path)
        return response.json()
    except requests.exceptions.ConnectionError:
        log("Unable to access the MISLAND server")
        return []
    except requests.exceptions.Timeout:
        log('API unable to login - general error')
        return []
    


"""
    This function retrieves level 1 admin boundaries to be added region comboboxes.
"""
def get_Adm1(adm0_id):
    path= "/api/vect1/?include=all"
    try:
        response = requests.get(URL_PATH +path)
        all_adm1=response.json()
        adm1=[]
        for item in all_adm1:
            if item['admin_zero_id']==adm0_id:
                adm1.append(item)
        return adm1
    except requests.exceptions.ConnectionError:
        log("Unable to access the MISLAND server")
        return []
    except requests.exceptions.Timeout:
        log('API unable to login - general error')
        return []


"""
    This function retrieves level 2 admin boundaries to be added in the sub-region combo boxes
"""
def get_Adm2(adm1_id):
    path="/api/vect2/"
    try:
        response = requests.get(URL_PATH+path)
        all_adm2=response.json()
        adm2=[]
        for item in all_adm2:
            if item["admin_one_id"]==adm1_id:
                adm2.append(item)
        
        return adm2

    except requests.exceptions.ConnectionError:
        log("Unable to access the MISLAND server")
        return []
    
    except requests.exceptions.Timeout:
        log('API unable to login - general error')
        return []

def show_error_message(message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec_()
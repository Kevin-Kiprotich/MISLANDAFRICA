from .api import login, get_user_email
from .gui.DlgSettings import Ui_DlgSettings
from .gui.DlgSettingsLogin import Ui_DlgSettingsLogin
from .gui.DlgSettingsRegister import Ui_DlgSettingsRegister
from .downloads import get_Adm0, get_Adm1, get_Adm2

from qgis.PyQt.QtCore import QSettings,QUrl
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QDesktopServices
settings = QSettings()

class DlgSettings(QtWidgets.QDialog, Ui_DlgSettings):
    def __init__(self, parent=None):
        super(DlgSettings, self).__init__(parent)

        self.setupUi(self)

        # self.dlg_settings_register = DlgSettingsRegister()
        self.dlg_settings_login = DlgSettingsLogin()
        # self.dlg_settings_edit = DlgSettingsEdit()

        self.pushButton_register.clicked.connect(self.register)
        self.pushButton_login.clicked.connect(self.login)
        self.pushButton_forgot_pwd.clicked.connect(self.forgot_pwd)

        self.buttonBox.rejected.connect(self.close)

    # """
    #     This is modified to connect to the MISLAND platform for unified registration    
    # """
    def register(self):
        url = QUrl('http://misland-africa.oss-online.org/#/register') #This holds the url for registration of new users in the QGIS plugin
        QDesktopServices.openUrl(url)
    #     result = self.dlg_settings_register.exec_()

    def login(self):
        result = self.dlg_settings_login.exec_()
        if result and self.dlg_settings_login.ok:
            self.close()

    # def edit(self):
    #     if not get_user_email():
    #         # Note that the get_user_email will display a message box warning 
    #         # the user to register.
    #         return

    #     self.dlg_settings_edit.exec_()

    def forgot_pwd(self):
        url=QUrl('http://misland-africa.oss-online.org/#/forgot-password')
        QDesktopServices.openUrl(url)
        

class DlgSettingsLogin(QtWidgets.QDialog, Ui_DlgSettingsLogin):
    def __init__(self, parent=None):
        super(DlgSettingsLogin, self).__init__(parent)

        self.setupUi(self)

        self.buttonBox.accepted.connect(self.login)
        self.buttonBox.rejected.connect(self.close)

        self.ok = False

    def showEvent(self, event):
        super(DlgSettingsLogin, self).showEvent(event)

        email = get_user_email(warn=False)
        if email:
            self.email.setText(email)
        password = settings.value("MISLANDAFRICA/password", None)
        if password:
            self.password.setText(password)

    def login(self):
        if not self.email.text():
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Enter your email address."))
            return
        elif not self.password.text():
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Enter your password."))
            return

        resp = login(self.email.text(), self.password.text())
        if resp:
            QtWidgets.QMessageBox.information(None,
                    self.tr("Success"),
                    self.tr(u"""Logged in to the MISLAND-AFRICA server as {}.<html><p>Welcome to MISLAND-AFRICA!<p/></html>""").format(self.email.text()))
            settings.setValue("MISLANDAFRICA/jobs_cache", None)
            self.done(QtWidgets.QDialog.Accepted)
            self.ok = True
    
    
    

        
        
        

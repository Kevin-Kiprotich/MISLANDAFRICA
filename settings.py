from MISLANDAFRICA.gui.DlgSettings import Ui_DlgSettings
from qgis.PyQt import QtWidgets

class DlgSettings(QtWidgets.QDialog, Ui_DlgSettings):
    def __init__(self, parent=None):
        super(DlgSettings, self).__init__(parent)

        self.setupUi(self)

        # self.dlg_settings_register = DlgSettingsRegister()
        # self.dlg_settings_login = DlgSettingsLogin()
        # self.dlg_settings_edit = DlgSettingsEdit()

        # self.pushButton_register.clicked.connect(self.register)
        # self.pushButton_login.clicked.connect(self.login)
        # self.pushButton_edit.clicked.connect(self.edit)
        # self.pushButton_forgot_pwd.clicked.connect(self.forgot_pwd)

        # self.buttonBox.rejected.connect(self.close)

    # """
    #     This is modified to connect to the MISLAND platform for unified registration    
    # """
    # def register(self):
    #     # url = QUrl('http://misland-africa.oss-online.org/#/register') #This holds the url for registration of new users in the QGIS plugin
    #     # QDesktopServices.openUrl(url)
    #     result = self.dlg_settings_register.exec_()

    # def login(self):
    #     result = self.dlg_settings_login.exec_()
    #     if result and self.dlg_settings_login.ok:
    #         self.close()

    # def edit(self):
    #     if not get_user_email():
    #         # Note that the get_user_email will display a message box warning 
    #         # the user to register.
    #         return

    #     self.dlg_settings_edit.exec_()

    # def forgot_pwd(self):
    #     # url=QUrl('http://misland-africa.oss-online.org/#/forgot-password')
    #     # QDesktopServices.openUrl(url)
    #     dlg_settings_edit_forgot_password = DlgSettingsEditForgotPassword()
    #     ret = dlg_settings_edit_forgot_password.exec_()
    #     if ret and dlg_settings_edit_forgot_password.ok:
    #         self.done(QtWidgets.QDialog.Accepted)

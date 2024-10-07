from .gui.DlgCalculate import Ui_DlgCalculate
from .gui.DlgSDG import Ui_DlgSDG
from .gui.DlgForests import Ui_DlgForests
from .gui.DlgSoilErosion import Ui_DlgSoilErosional
from qgis.PyQt import QtWidgets


class DlgCalculate(QtWidgets.QDialog, Ui_DlgCalculate):
    def __init__(self, parent=None):
        super(DlgCalculate, self).__init__(parent)

        self.setupUi(self)

    #     self.dlg_calculate_ld = DlgCalculateLD()
    #     self.dlg_calculate_tc = DlgCalculateTC()
    #     self.dlg_calculate_rest_biomass = DlgCalculateRestBiomass()
    #     # self.dlg_calculate_urban = DlgCalculateUrban()
    #     self.dlg_calculate_forest = DlgCalculateForest()
    #     self.dlg_calculate_medalus = DlgCalculateMedalus()

    #     # add the calculate cvi sequence
    #     self.dlg_calculate_ce = DlgCalculateCE()

    #     # add the soil erosion sequence
    #     self.dlg_calculate_se = DlgCalculateSE() 

    #     from MISLAND.timeseries import DlgTimeseries
    #     self.dlg_timeseries = DlgTimeseries()
        
    #     self.pushButton_ld.clicked.connect(self.btn_ld_clicked)
    #     self.pushButton_timeseries.clicked.connect(self.btn_timeseries_clicked)
    #     # self.pushButton_tc.clicked.connect(self.btn_tc_clicked)
    #     # self.pushButton_rest_biomass.clicked.connect(self.btn_rest_biomass_clicked)
    #     # self.pushButton_urban.clicked.connect(self.btn_urban_clicked)
    #     self.pushButton_forest.clicked.connect(self.btn_forest_clicked)
    #     self.pushButton_medalus.clicked.connect(self.btn_medalus_clicked)
    #     self.pushbutton_CE.clicked.connect(self.btn_ce_clicked)
    #     self.pushButton_SE.clicked.connect(self.btn_se_clicked)
    
    # def btn_ld_clicked(self):
    #     self.close()
    #     result = self.dlg_calculate_ld.exec_()

    # def btn_tc_clicked(self):
    #     self.close()
    #     result = self.dlg_calculate_tc.exec_()

    # def btn_rest_biomass_clicked(self):
    #     self.close()
    #     result = self.dlg_calculate_rest_biomass.exec_()

    # def btn_forest_clicked(self):
    #     self.close()
    #     result = self.dlg_calculate_forest.exec_()
    #     # self.close()
    #     # result = self.dlg_calculate_forest.exec_()
    #     # QtWidgets.QMessageBox.information(None, self.tr("Coming soon!"),
    #     #                         self.tr("Forest coming soon!"))

    # def btn_medalus_clicked(self):
    #     self.close()
    #     result = self.dlg_calculate_medalus.exec_()
    #     # QtWidgets.QMessageBox.information(None, self.tr("Coming soon!"),
    #     #                         self.tr("MEDALUS coming soon!"))

    # def btn_timeseries_clicked(self):
    #     self.close()
    #     result = self.dlg_timeseries.exec_()
    #     # QtWidgets.QMessageBox.information(None, self.tr("Coming soon!"),
    #     #                         self.tr("MEDALUS coming soon!"))
    
    # #This listens for when the coastal erosion button is clicked
    # def btn_ce_clicked(self):
    #     self.close()
    #     result=self.dlg_calculate_ce.exec_()

    # def btn_se_clicked(self):
    #     self.close()
    #     result = self.dlg_calculate_se.exec_() 
    # # def btn_urban_clicked(self):
    # #     self.close()
    # #     result = self.dlg_calculate_urban.exec_()
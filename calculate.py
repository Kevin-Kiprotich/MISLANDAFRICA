from .gui.DlgCalculate import Ui_DlgCalculate
from .gui.DlgSDG import Ui_DlgSDG
from .gui.DlgForests import Ui_DlgForests
from .gui.DlgSoilErosion import Ui_DlgSoilErosion
from .SDG import *
from .vegetation import DlgVegetation
from .medalus import DlgMedalus
from .CVI import DlgCoastalVulnerabilityIndex
from .water_erosion import DlgWaterErosion
from .wind_erosion import DlgWindErosion
from .forests import DlgForestLoss, DlgForestCarbonEmission, DlgForestFireRisk, DlgForestFireAssessment
from qgis.PyQt import QtWidgets


class DlgCalculate(QtWidgets.QDialog, Ui_DlgCalculate):
    def __init__(self, parent=None):
        super(DlgCalculate, self).__init__(parent)

        self.setupUi(self)

        self.dlgSDG = DlgSDG()
        self.dlgForests = DlgForests()
        self.dlgSoilErosion = DlgSoilErosion()
        self.dlgVegetation = DlgVegetation()
        self.dlgMedalus = DlgMedalus()
        self.dlgCVI = DlgCoastalVulnerabilityIndex()
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
        
        self.pushButton_ld.clicked.connect(self.btn_ld_clicked)
        self.pushButton_forest.clicked.connect(self.btn_forest_clicked)
        self.pushButton_SE.clicked.connect(self.btn_SE_clicked)
        self.pushButton_vegetation.clicked.connect(self.btn_vegetation_clicked)
        self.pushButton_medalus.clicked.connect(self.btn_medalus_clicked)
        self.pushbutton_CE.clicked.connect(self.btn_CE_clicked)
    
    def btn_ld_clicked(self):
        self.close()
        result = self.dlgSDG.exec_()

    def btn_forest_clicked(self):
        self.close()
        result=self.dlgForests.exec_()
    
    def btn_SE_clicked(self):
        self.close()
        result = self.dlgSoilErosion.exec_()
    
    def btn_vegetation_clicked(self):
        self.close()
        result = self.dlgVegetation.exec_()
    
    def btn_medalus_clicked(self):
        self.close()
        result = self.dlgMedalus.exec_()
        
    def btn_CE_clicked(self):
        self.close()
        result = self.dlgCVI.exec_()
        
    
    
class DlgSDG(QtWidgets.QDialog, Ui_DlgSDG):
    def __init__(self, parent=None):
        super(DlgSDG, self).__init__(parent)

        self.setupUi(self)
        
        self.pushButton_lp.clicked.connect(self.btn_lp_clicked)
        self.pushButton_lc.clicked.connect(self.btn_lc_clicked)
        self.pushButton_cs.clicked.connect(self.btn_cs_clicked)
        self.pushButton_sdg.clicked.connect(self.btn_sdg_clicked)
        
    def btn_lp_clicked(self):
        self.close()
        result = DlgLandProductivity().exec_()
        
    def btn_lc_clicked(self):
        self.close()
        result = DlgLandCover().exec_()
    
    def btn_sdg_clicked(self):
        self.close()
        result = DlgSDGIndicator().exec_()
        
    def btn_cs_clicked(self):
        self.close()
        result=DlgCarbonStock().exec_()
        
        
class DlgForests(QtWidgets.QDialog, Ui_DlgForests):
    def __init__(self, parent=None):
        super(DlgForests, self).__init__(parent)

        self.setupUi(self)
        
        self.pushButton_fl.clicked.connect(self.openForestLoss)
        self.pushButton_fc.clicked.connect(self.openForestCarbonEmission)
        self.pushButton_ffr.clicked.connect(self.openForestFireRisk)
        self.pushButton_ffa.clicked.connect(self.openForestFireAssessment)
        
    def openForestLoss(self):
        self.close()
        result = DlgForestLoss().exec_()
    
    def openForestCarbonEmission(self):
        self.close()
        result = DlgForestCarbonEmission().exec_()
    
    def openForestFireRisk(self):
        self.close()
        result = DlgForestFireRisk().exec_()
    
    def openForestFireAssessment(self):
        self.close()
        result = DlgForestFireAssessment().exec_()


class DlgSoilErosion(QtWidgets.QDialog, Ui_DlgSoilErosion):
    def __init__(self, parent=None):
        super(DlgSoilErosion, self).__init__(parent)

        self.setupUi(self)
        
        self.WaterPushButton.clicked.connect(self.openWaterErosion)
        self.WindPushButton.clicked.connect(self.openWindErosion)
        
    def openWaterErosion(self):
        self.close()
        result = DlgWaterErosion().exec_()
        
    def openWindErosion(self):
        self.close()
        result = DlgWindErosion().exec_()
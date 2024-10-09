from .gui.DlgMedalus import Ui_DlgMedalus
from concurrent.futures import ThreadPoolExecutor
from .downloads import *
from .Styles import *
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtWidgets
from qgis.utils import iface

class DlgMedalus(QtWidgets.QDialog, Ui_DlgMedalus):
    def __init__(self, parent=None):
        super(DlgMedalus, self).__init__(parent)

        self.setupUi(self)
        self.qualityIndices = ["Climate","Vegetation","Soil","Management","Environmental Sensitive Areas"]
        self.computation = "Climate Quality Index"
        self.IndexComboBox.addItems(self.qualityIndices)
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.computationYears = fetchComputationYears(self.computation)
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.CountryComboBox.setCurrentIndex(-1)
        self.OutputLineEdit.setReadOnly(True)
        
        #Map functions to buttons and combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.IndexComboBox.currentTextChanged.connect(self.evaluateComputation)
        
    def evaluateComputation(self):
        if self.IndexComboBox.currentText() == "Climate":
            self.computation = "Climate Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Vegetation":
            self.computation = "Vegetation Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Soil":
            self.computation = "Soil Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Management":
            self.computation = "Management Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Environmental Sensitive Areas":
            self.computation = "Soil Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
            
    def fillOutputDestination(self):
        resetLineEditHighlight(self.OutputLineEdit)
        filepath = getOutputDestination(self)
        self.OutputLineEdit.setText(filepath)
        
    def getRegions(self):
        resetComboBoxHighlight(self.CountryComboBox)
        self.RegionComboBox.clear()
        self.regions, self.country_id = populate_region(self.CountryComboBox.currentText())
        self.RegionComboBox.addItems(self.regions if self.regions is not None else [])
        self.RegionComboBox.setCurrentIndex(-1)
    
    def getSubRegions(self):
        self.SubRegionComboBox.clear()
        self.subregions, self.region_id = populate_sub_region(self.RegionComboBox.currentText(),self.country_id)
        self.SubRegionComboBox.addItems(self.subregions if self.subregions is not None else [])
        self.SubRegionComboBox.setCurrentIndex(-1)
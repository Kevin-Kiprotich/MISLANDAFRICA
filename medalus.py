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
        self.api = '/climatequality/'
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
        self.SubmitPushButton.clicked.connect(self.compute)
        
    def evaluateComputation(self):
        if self.IndexComboBox.currentText() == "Climate":
            self.computation = "Climate Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.api = '/climatequality/'
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Vegetation":
            self.computation = "Vegetation Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.api = '/vegetationquality/'
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Soil":
            self.computation = "Soil Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.api = '/soilquality/'
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Management":
            self.computation = "Management Quality Index"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.api = '/managementquality/'
            self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        elif self.IndexComboBox.currentText() == "Environmental Sensitive Areas":
            self.computation = "ESAI"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearComboBox.clear()
            self.api = '/esai/'
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
    
    def compute(self):
        progress_dialog = QtWidgets.QProgressDialog("Processing...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Fetching Land Productivity Raster")
        progress_dialog.setWindowModality(Qt.WindowModal)

        progress_bar = QtWidgets.QProgressBar(progress_dialog)
        progress_dialog.setBar(progress_bar)

        progress_dialog.show()
        QtWidgets.QApplication.processEvents()
        path = self.api
        
        if not self.CountryComboBox.currentText():
            highlightComboBox(self.CountryComboBox)
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Please select a country"))
            return
        
        if not self.OutputLineEdit.text():
            highlightLineEdit(self.OutputLineEdit)
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Please provide an output file path"))
            return
        
        
        
        filePath = self.OutputLineEdit.text()
        payload = {
            "admin_0": self.country_id,
            "computation_type":self.computation,
            "raster_type":1,
            "end_year":int(self.YearComboBox.currentText()),
            "cached":self.CacheCheckBox.isChecked(),
            "start_year":int(self.YearComboBox.currentText()),
        }
        country = self.CountryComboBox.currentText()
        region = self.RegionComboBox.currentText()
        subregion = self.SubRegionComboBox.currentText()
        if country and not region and not subregion:
            #get the country id
            for item in countries:
                if country == item['name_0']:
                    countryID = item["id"]
                    break
            payload["vector"] = countryID
            payload["admin_level"] = 0
            
        elif country and region and not subregion:
            for item in regions:
                if region == item['name_1']:
                    regionID = item["id"]
                    break
            
            payload["vector"] = regionID
            payload["admin_level"] = 1

        elif country and region and subregion:
            for item in subregions:
                if subregion == item['name_2']:
                    subRegionID = item["id"]
                    break
            
            payload["vector"] = subRegionID
            payload["admin_level"] = 2
        
        # task = threading.Thread(target=fetchRaster, args = (path, payload, filePath, progress_dialog, progress_bar))
        # task.start()
        # with ThreadPoolExecutor(max_workers=1) as executor:
        #     future = executor.submit(fetchRaster, path, payload, filePath, progress_dialog, progress_bar)
        #     result = future.result()
        #     print(result)
        #     if result is not None:
        #         self.close()
        result = fetchRaster(path, payload, filePath, progress_dialog, progress_bar,self.computation)
        if result is not None:
            self.close()
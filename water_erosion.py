from .gui.DlgWaterErosion import Ui_DlgWaterErosion
from .algorithms import dissolvePolygons
from qgis.core import QgsVectorLayer
from .downloads import *
from .Styles import *
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtWidgets
from qgis.utils import iface

class DlgWaterErosion(QtWidgets.QDialog, Ui_DlgWaterErosion):
    def __init__(self, parent=None):
        super(DlgWaterErosion, self).__init__(parent)

        self.setupUi(self)
        
        self.indices = ["Rainfall Erosivity","Soil Erodibility","Slope Steepness","Cover Management","Conservation Practice","Soil Loss"]
        self.computation = "RUSLE"
        self.api = "/rusle/"
        self.computationYears = fetchComputationYears(self.computation)
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.FactorComboBox.addItems(self.indices)
        self.CountryComboBox.setCurrentIndex(-1)
        self.OutputLineEdit.setReadOnly(True)
        
        #Map functions to buttons and combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.SubmitPushButton.clicked.connect(self.compute)
        #Custom Shapefile
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.CustomPushButton.clicked.connect(self.fetchShapefile)
    
    def fetchShapefile(self):
        path = getShapefile(self, self.CustomGroupBox.isChecked())
        if path is not None:
            self.CustomComboBox.setCurrentText(path)
        
    def evaluateComputation(self):
        if self.FactorComboBox.currentText() == "Soil Loss":
            return "Rusle"
        else:
            return self.FactorComboBox.currentText()
             
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
        progress_dialog.setWindowTitle("Fetching Water Erosion Raster")
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
            "computation_type":self.evaluateComputation(),
            "raster_type":1,
            "end_year":int(self.YearComboBox.currentText()),
            "cached":self.CacheCheckBox.isChecked(),
            "start_year":int(self.YearComboBox.currentText()),
        }
        
        if self.CustomGroupBox.isChecked():
            file = self.CustomComboBox.currentText()
            if not file:
                show_error_message("Custom Area not provided")
                return
            if os.path.isfile(file):
                # Load the vector layer using QGIS's QgsVectorLayer class
                layer = QgsVectorLayer(file, "layer_name", "ogr")
                
                if not layer.isValid():
                    show_error_message(f"Failed to load the file: {file}")
                    return None

                # Use the updated QGIS dissolvePolygons function for QGIS layers
                customCoords = dissolvePolygons(layer,filePath) # Using the new QGIS-based dissolvePolygons function
                if customCoords is None:
                    return None
                
                payload["custom_coords"] = customCoords
            else:
                # Handle QGIS layer input
                layer = QgsProject.instance().mapLayersByName(file)[0]
                if layer:
                    # Use the updated QGIS dissolvePolygons function for QGIS layers
                    customCoords = dissolvePolygons(layer,filePath)  # Using the new QGIS-based dissolvePolygons function
                    if customCoords is None:
                        return None
                    
                    payload["custom_coords"] = customCoords
                else:
                    show_error_message(f"Layer '{file}' not found in QGIS.")
                    return None
        
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
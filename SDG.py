from .gui.DlgSDGIndicator import Ui_DlgSDGIndicator
from .gui.DlgCarbonStock import Ui_DlgCarbonStock
from .gui.DlgLandCover import Ui_DlgLandCover
from .gui.DlgLandProductivity import Ui_DlgLandProductivity
from concurrent.futures import ThreadPoolExecutor
from .algorithms import dissolvePolygons
import geopandas as gpd
from .downloads import *
from .Styles import *
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.core import QgsVectorLayer
mb = iface.messageBar()


class DlgSDGIndicator(QtWidgets.QDialog, Ui_DlgSDGIndicator):
    def __init__(self, parent=None):
        super(DlgSDGIndicator, self).__init__(parent)

        self.setupUi(self)
        
        self.dataSources = ['Modis', 'Landsat']
        self.vegetationIndex = ['NDVI']
        self.EcoDataSources = ['2000','2001','2002']
        self.SOCReferences = ['2000','2001','2002']
        self.computation = "Land Degradation"
        self.computationYears = fetchComputationYears(self.computation)
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.SourceComboBox.addItems(self.dataSources)
        self.EcoSourceComboBox.addItems(self.EcoDataSources)
        self.RefComboBox.addItems(self.SOCReferences)
        self.IndexComboBox.addItems(self.vegetationIndex)
        self.CountryComboBox.setCurrentIndex(-1)

        #map functions to buttons and combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.SourceComboBox.currentTextChanged.connect(self.evaluateIndex)
        self.SubmitPushButton.clicked.connect(self.compute)
        self.OutputLineEdit.setReadOnly(True)
        
        #Custom Shapefile
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.CustomPushButton.clicked.connect(self.fetchShapefile)
    
    def fetchShapefile(self):
        path = getShapefile(self, self.CustomGroupBox.isChecked())
        if path is not None:
            self.CustomComboBox.setCurrentText(path)
        
    def evaluateIndex(self):
        if self.SourceComboBox.currentText() == "Modis":
            self.IndexComboBox.setCurrentIndex(0)
            self.IndexComboBox.setDisabled(True)
        if self.SourceComboBox.currentText() == "Landsat":
            self.IndexComboBox.setDisabled(False)
    
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
        path = "/degradation/"
        
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
            "raster_source": self.SourceComboBox.currentText() if self.SourceComboBox.currentText() == "Modis" else "Landsat 7" if self.SourceComboBox.currentText() == "Landsat" else "",
            "raster_type":1,
            "reference_eco_units":49,
            "reference_raster":12,
            "end_year":int(self.YearComboBox.currentText()),
            "cached":self.CacheCheckBox.isChecked(),
            "start_year":2001,
            "show_change":True,
            "veg_index":self.IndexComboBox.currentText(),
            "transform":"area",
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
        
        
class DlgCarbonStock(QtWidgets.QDialog, Ui_DlgCarbonStock):
    def __init__(self, parent=None):
        super(DlgCarbonStock,self).__init__(parent)
        
        self.setupUi(self)
        
        self.dataSources = ["ESA CCI-LC"]
        self.SOCReferences = ["2000","2001","2002"]
        self.computation = "SOC"
        self.computationYears = fetchComputationYears(self.computation)
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.SourceComboBox.addItems(self.dataSources)
        self.RefComboBox.addItems(self.SOCReferences)
        self.CountryComboBox.setCurrentIndex(-1)
        
        #map functions to buttons and combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.SubmitPushButton.clicked.connect(self.compute)
        self.OutputLineEdit.setReadOnly(True)
        
        #Custom Shapefile
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.CustomPushButton.clicked.connect(self.fetchShapefile)
    
    def fetchShapefile(self):
        path = getShapefile(self, self.CustomGroupBox.isChecked())
        if path is not None:
            self.CustomComboBox.setCurrentText(path)
    
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
        progress_dialog.setWindowTitle("Fetching Carbon Stock Raster")
        progress_dialog.setWindowModality(Qt.WindowModal)

        progress_bar = QtWidgets.QProgressBar(progress_dialog)
        progress_dialog.setBar(progress_bar)

        progress_dialog.show()
        QtWidgets.QApplication.processEvents()
        path = "/soc/"
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
            "cached":self.CacheCheckBox.isChecked(),
            "raster_type":1,
            "reference_raster":12,
            "reference_soc": 12,
            "show_change":True,
            "start_year":2000,
            "end_year":int(self.YearComboBox.currentText())
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
            
        result = fetchRaster(path, payload, filePath, progress_dialog, progress_bar,self.computation)
        if result is not None:
            self.close()
    
        
        
        
class DlgLandCover(QtWidgets.QDialog, Ui_DlgLandCover):
    def __init__(self, parent=None):
        super(DlgLandCover,self).__init__(parent)
        
        self.setupUi(self)
        self.analysisOptions = ['Land Cover', 'Land Cover Change']
        self.dataSources = ["ESA CCI-LC"]
        self.computation = "LULC"
        self.computationYears = fetchComputationYears(self.computation)
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.StartYearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.EndYearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.OptionComboBox.addItems(self.analysisOptions)
        self.SourceComboBox.addItems(self.dataSources)
        self.YearsWidget.setVisible(False)
        self.CountryComboBox.setCurrentIndex(-1)
        self.YearComboBox.setCurrentIndex(-1)
        self.StartYearComboBox.setCurrentIndex(-1)
        self.EndYearComboBox.setCurrentIndex(-1)
        
        #map functions to buttons and combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.OptionComboBox.currentTextChanged.connect(self.resetComputationYears)
        self.SubmitPushButton.clicked.connect(self.compute)
        self.OutputLineEdit.setReadOnly(True)
        
        #Custom Shapefile
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.CustomPushButton.clicked.connect(self.fetchShapefile)
    
    def fetchShapefile(self):
        path = getShapefile(self, self.CustomGroupBox.isChecked())
        if path is not None:
            self.CustomComboBox.setCurrentText(path)
            
    def fillOutputDestination(self):
        resetLineEditHighlight(self.OutputLineEdit)
        filepath = getOutputDestination(self)
        self.OutputLineEdit.setText(filepath)
    
    def resetComputationYears(self):
        if self.OptionComboBox.currentText() == "Land Cover":
            self.computation = "LULC"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearsWidget.setVisible(False)
            self.PeriodWidget.setVisible(True)
            self.StartYearComboBox.setCurrentIndex(-1)
            self.EndYearComboBox.setCurrentIndex(-1)
        else:
            self.computation = "LULC Change"
            self.computationYears = fetchComputationYears(self.computation)
            self.YearsWidget.setVisible(True)
            self.PeriodWidget.setVisible(False)
            self.YearComboBox.setCurrentIndex(-1)
            
       
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
        progress_dialog.setWindowTitle("Fetching Land Cover Raster")
        progress_dialog.setWindowModality(Qt.WindowModal)

        progress_bar = QtWidgets.QProgressBar(progress_dialog)
        progress_dialog.setBar(progress_bar)

        progress_dialog.show()
        QtWidgets.QApplication.processEvents()
        path = "/lulc/"
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
            "cached":self.CacheCheckBox.isChecked(),
            "raster_type":1,
        }
        
        if self.computation == "LULC":
            payload["end_year"] = ""
            payload["show_change"] = 0
            payload["start_year"] = str(self.YearComboBox.currentText())
        elif self.computation == "LULC Change":
            payload["end_year"] = self.EndYearComboBox.currentText()
            payload["show_change"] = 1
            payload["start_year"] = self.StartYearComboBox.currentText()
            
            
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
            
        result = fetchRaster(path, payload, filePath, progress_dialog, progress_bar,self.computation)
        if result is not None:
            self.close()

      
class DlgLandProductivity(QtWidgets.QDialog, Ui_DlgLandProductivity):
    def __init__(self, parent=None):
        super(DlgLandProductivity,self).__init__(parent)
        
        self.setupUi(self)
        
        self.productivityIndicators = ['State','Trajectory','Performance','Land Productivity']
        self.indices = ["NDVI", "MSAVI", "SAVI"]
        self.dataSources = ['Modis', 'Landsat']
        self.computation = "Productivity State"
        self.countries = []
        for country in get_Adm0():
            self.countries.append(country['name_0'])
        self.computationYears = fetchComputationYears(self.computation)
        if self.computationYears is None:
            self.close()
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.IndicatorComboBox.addItems(self.productivityIndicators)
        self.IndexComboBox.addItems(self.indices)
        self.SourceComboBox.addItems(self.dataSources)
        self.mGroupBox.setVisible(False)
        self.CountryComboBox.setCurrentIndex(-1)
        
        #map functions to buttons and the combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.IndicatorComboBox.currentTextChanged.connect(self.resetComputationYears)
        self.SourceComboBox.currentTextChanged.connect(self.evaluateIndex)
        self.SubmitPushButton.clicked.connect(self.compute)
        self.CustomPushButton.clicked.connect(self.fetchShapefile)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.OutputLineEdit.setReadOnly(True)
    
    def fetchShapefile(self):
        path = getShapefile(self, self.CustomGroupBox.isChecked())
        if path is not None:
            self.CustomComboBox.setCurrentText(path)
              
    def evaluateIndex(self):
        if self.SourceComboBox.currentText() == "Modis":
            self.IndexComboBox.setCurrentIndex(0)
            self.mGroupBox.setVisible(False)
        if self.SourceComboBox.currentText() == "Landsat":
            self.mGroupBox.setVisible(True)
        
    
    def resetComputationYears(self):
        if self.IndicatorComboBox.currentText() == "Land Productivity":
            self.computation = "Productivity"
            self.computationYears = fetchComputationYears(self.computation)
        else:
            self.computation = "Productivity {}".format(self.IndicatorComboBox.currentText())
            self.computationYears = fetchComputationYears(self.computation)
            
            
    
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
        path = "/{}/".format(self.IndicatorComboBox.currentText().lower())
        
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
            "raster_source": self.SourceComboBox.currentText() if self.SourceComboBox.currentText() == "Modis" else "Landsat 7" if self.SourceComboBox.currentText() == "Landsat" else "",
            "raster_type":3,
            "reference_eco_units":49,
            "reference_raster":12,
            "end_year":int(self.YearComboBox.currentText()),
            "cached":self.CacheCheckBox.isChecked(),
            "start_year":2000,
            "show_change":1,
            "veg_index":self.IndexComboBox.currentText(),
            "transform":"area",
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
        log(json.dumps(payload)) 
        result = fetchRaster(path, payload, filePath, progress_dialog, progress_bar,self.computation)
        if result is not None:
            self.close()    
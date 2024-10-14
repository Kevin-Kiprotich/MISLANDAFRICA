from .gui.DlgForestLoss import Ui_DlgForestLoss
from .gui.DlgForestCarbonEmission import Ui_DlgForestCarbonEmission
from .gui.DlgForestFireRisk import Ui_DlgForestFireRisk
from .gui.DlgForestFireAssessment import Ui_DlgForestFireAssessment
from .algorithms import dissolvePolygons
from qgis.core import QgsVectorLayer
from .downloads import *
from .Styles import *
from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt import QtWidgets
from qgis.utils import iface

class DlgForestLoss(QtWidgets.QDialog, Ui_DlgForestLoss):
    def __init__(self, parent=None):
        super(DlgForestLoss, self).__init__(parent)

        self.setupUi(self)
        
        self.dataSources = ["Hansen"]
        self.computation = "Forest Change"
        self.api = "/forestchange/"
        self.computationYears = fetchComputationYears(self.computation)
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.SourceComboBox.addItems(self.dataSources)
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
        progress_dialog.setWindowTitle("Fetching Forest Loss Raster")
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
            "raster_source":self.SourceComboBox.currentText(),
            "raster_type":6,
            "end_year":int(self.YearComboBox.currentText()),
            "cached":self.CacheCheckBox.isChecked(),
            "start_year":2000,
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
            

class DlgForestCarbonEmission(QtWidgets.QDialog, Ui_DlgForestCarbonEmission):
    def __init__(self, parent=None):
        super(DlgForestCarbonEmission, self).__init__(parent)

        self.setupUi(self)
        
        self.dataSources = ["Global Forest Change Maps"]
        self.computation = "Forest Carbon Emission"
        self.api = "/carbonemission/"
        self.computationYears = fetchComputationYears(self.computation)
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.YearComboBox.addItems(self.computationYears if self.computationYears is not None else [])
        self.SourceComboBox.addItems(self.dataSources)
        self.UnitSpinBox.setValue(3)
        self.ThresholdSpinBox.setValue(30)
        self.StockDoubleSpinBox.setValue(0.2522)
        self.ProportionSpinBox.setValue(30)
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
        progress_dialog.setWindowTitle("Fetching Forest Carbon Emission Raster")
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
            "raster_source":self.SourceComboBox.currentText(),
            "raster_type":6,
            "end_year":int(self.YearComboBox.currentText()),
            "cached":self.CacheCheckBox.isChecked(),
            "start_year":int(self.YearComboBox.currentText()),
            "muf": int(self.UnitSpinBox.value()),
            "mfu_forest_threshold": int(self.ThresholdSpinBox.value()),
            "degradation_emission_proportion": int(self.ProportionSpinBox.value()),
            "carbon_stock": float(self.StockDoubleSpinBox.value()),
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
            
            
class DlgForestFireRisk(QtWidgets.QDialog, Ui_DlgForestFireRisk):
    def __init__(self, parent=None):
        super(DlgForestFireRisk, self).__init__(parent)

        self.setupUi(self)
        
        self.computation = "Forest Fire Risk"
        self.api = "/forestfirerisk/"
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.StartDateEdit.setDate(QDate.currentDate())
        self.EndDateEdit.setDate(QDate.currentDate())
        self.CountryComboBox.setCurrentIndex(-1)
        self.OutputLineEdit.setReadOnly(True)
        
        #Map functions to buttons and combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.StartDateEdit.dateChanged.connect(self.updateDates)
        self.SubmitPushButton.clicked.connect(self.compute)
        
        #Custom Shapefile
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.CustomPushButton.clicked.connect(self.fetchShapefile)
    
    def fetchShapefile(self):
        path = getShapefile(self, self.CustomGroupBox.isChecked())
        if path is not None:
            self.CustomComboBox.setCurrentText(path)

    def updateDates(self):
        self.EndDateEdit.setDate(self.StartDateEdit.date())
        self.EndDateEdit.setMinimumDate(self.StartDateEdit.date())
    
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
        progress_dialog.setWindowTitle("Fetching Forest Fire Risk Raster")
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
            "end_date":self.EndDateEdit.date().toString("yyyy-MM-dd"),
            "cached":self.CacheCheckBox.isChecked(),
            "start_date":self.StartDateEdit.date().toString("yyyy-MM-dd"),
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
            
class DlgForestFireAssessment(QtWidgets.QDialog, Ui_DlgForestFireAssessment):
    def __init__(self, parent=None):
        super(DlgForestFireAssessment, self).__init__(parent)

        self.setupUi(self)
        
        self.dataSources = ["Sentinel 2", "Landsat"]
        self.computation = "Forest Fire"
        self.api = "/forestfire/"
        self.countries = [country['name_0'] for country in get_Adm0() if get_Adm0() is not None]
        self.CountryComboBox.addItems(self.countries if self.countries is not None else [])
        self.SourceComboBox.addItems(self.dataSources)
        self.PreStartDateEdit.setDate(QDate.currentDate())
        self.PreEndDateEdit.setDate(QDate.currentDate())
        self.PostStartDateEdit.setDate(QDate.currentDate())
        self.PostEndDateEdit.setDate(QDate.currentDate())
        self.CountryComboBox.setCurrentIndex(-1)
        self.OutputLineEdit.setReadOnly(True)
        
        #Map functions to buttons and combo boxes
        self.CountryComboBox.currentTextChanged.connect(self.getRegions)
        self.RegionComboBox.currentTextChanged.connect(self.getSubRegions)
        self.OutputPushButton.clicked.connect(self.fillOutputDestination)
        self.PreStartDateEdit.dateChanged.connect(self.updatePreEndDates)
        self.PreEndDateEdit.dateChanged.connect(self.updatePostStartDates)
        self.PostStartDateEdit.dateChanged.connect(self.updatePostEndDates)
        self.SubmitPushButton.clicked.connect(self.compute)
        
        #Custom Shapefile
        self.CustomComboBox.addItems(getLayers() if getLayers() is not None else [])
        self.CustomPushButton.clicked.connect(self.fetchShapefile)
    
    def fetchShapefile(self):
        path = getShapefile(self, self.CustomGroupBox.isChecked())
        if path is not None:
            self.CustomComboBox.setCurrentText(path)

    def updatePreEndDates(self):
        self.PreEndDateEdit.setDate(self.PreStartDateEdit.date())
        self.PreEndDateEdit.setMinimumDate(self.PreStartDateEdit.date())
    
    def updatePostStartDates(self):
        self.PostStartDateEdit.setDate(self.PreEndDateEdit.date())
        self.PostStartDateEdit.setMinimumDate(self.PreEndDateEdit.date())
    
    def updatePostEndDates(self):
        self.PostEndDateEdit.setDate(self.PostStartDateEdit.date())
        self.PostEndDateEdit.setMinimumDate(self.PostStartDateEdit.date())
    
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
        progress_dialog.setWindowTitle("Fetching Forest Fire Assessment Raster")
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
            "cached":self.CacheCheckBox.isChecked(),
            "postfire_end": self.PostEndDateEdit.date().toString("yyyy-MM-dd"),
            "postfire_start": self.PostStartDateEdit.date().toString("yyyy-MM-dd"),
            "prefire_end": self.PreEndDateEdit.date().toString("yyyy-MM-dd"),
            "prefire_start": self.PreStartDateEdit.date().toString("yyyy-MM-dd"),
            "raster_source": self.SourceComboBox.currentText() if self.SourceComboBox.currentText() == "Sentinel 2" else "Landsat 8" if self.SourceComboBox.currentText() == "Landsat" else "",
            "raster_type": 1,
            "show_change": 1,
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

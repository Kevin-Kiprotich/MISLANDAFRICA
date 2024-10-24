from qgis.PyQt.QtWidgets import QMessageBox, QApplication, QFileDialog
from qgis.core import QgsRasterLayer, QgsProject, QgsMapLayerType, QgsRasterBandStats
from qgis.utils import iface
from .data.admin_bounds import countries, regions, subregions
from .data.computation_years import computationYears
import json
from . import log
from .api import get_access_token
import requests
import os

API_URL = 'http://misland-africa.oss-online.org:1337/api'
pluginDir = os.path.dirname(os.path.abspath(__file__))


def get_Adm0():
    """
        This function retrieves level 0 admin boundaries to be used in the country comboboxes.
        Returns:
            list: A list of the all countries
    """
    return countries
    
def get_Adm1(adm0_id: int):
    """
        This function retrieves level 1 admin boundaries to be added region comboboxes.
        Args:
            adm0_id (int): The id of the country
        Returns:
            list: A list of the regions in the country
    """
    all_adm1=regions
    adm1=[]
    for item in all_adm1:
        if item['admin_zero_id']==adm0_id:
            adm1.append(item)
    return adm1
    
def get_Adm2(adm1_id: int):
    """
        This function retrieves level 2 admin boundaries to be added in the sub-region combo boxes.
        Args:
            adm1_id (int): The id of the region
        Returns:
            list: A list of the subregions in the region
    """
    all_adm2=subregions
    adm2=[]
    for item in all_adm2:
        if item["admin_one_id"]==adm1_id:
            adm2.append(item)
    
    return adm2

def show_error_message(message):
        """
            Shows an error message if an error occurs.
            Args:
                message (str): Error message to be displayed.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec_()
        
def show_info_message(message):
    """
    Shows an information message.
    Args:
        message (str): Information message to be displayed.
    """
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)  # Change to Information icon
    msg_box.setWindowTitle("Information")  # Update window title
    msg_box.setText(message)
    msg_box.exec_()
        
def populate_region(country: str):
    """
        Populates region names only.
        Args:
            country (str): The name of the country for regions are to be returned.
        Returns:
            list: A sorted list of all regions and the country id
    """ 
    regions = []
    id = 0
    for item in get_Adm0():
        if country == item['name_0']:
            id = item['id']
            for region in get_Adm1(id):
                regions.append(region['name_1'])
            break
    return sorted(regions), id

def populate_sub_region(region:str, countryID:int):
    """
        Populates region names only.
        Args:
            region (str): The name of the country for sub-regions are to be returned.
            countryID (int): The id of the country for which the region belongs.
        Returns:
            list: A sorted list of all sub-regions and the region id.
    """
    sub_regions=[]
    regionID = 0
    for item in get_Adm1(countryID):
        if region == item['name_1']:
            regionID = item['id']
            for subregion in get_Adm2(regionID):
                sub_regions.append(subregion['name_2'])
            break
    return sorted(sub_regions), regionID

def fetchComputationYears(computation_type: str):
    """
        Populates region names only.
        Args:
            computation_type (str): Computation type.
        Returns:
            list: A sorted list of computation years associated with the given computation type.
    """
    computations=computationYears
    for item in computations:
        if computation_type == item['computation_type']:
            years = item["published_years"]
            return sorted(list(map(str, years)))
    
def getOutputDestination(parent=None):
        """
        Open a file dialog to allow the user to select where to save the output GeoTIFF file.

        Returns:
            str: The file path selected by the user to save the GeoTIFF file, or an empty string if canceled.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(parent, "Select Output Destination", "", "GeoTIFF Files (*.tif);;All Files (*)", options=options)
        
        if file_name:
            return file_name
        else:
            return ""
        
def fetchRaster(path, payload, filePath, progressDialog, progressBar, computation):
    token = get_access_token()
    log(json.dumps(payload))
    try:
        progressDialog.setLabelText("Fetching Data ...")
        progressBar.setValue(0)
        resp = requests.post(API_URL+path, json = payload, headers = {"Authorization": "Bearer " + token})
        
        if resp.status_code == 200:
            progressBar.setValue(30)
            raster_data = resp.json()
            progressDialog.setLabelText("Fetching Raster File ...")
            if "error" in raster_data.keys():
                show_error_message(raster_data['error'])
                progressDialog.close()
                return None
            if "success" in raster_data.keys() and "message" in raster_data.keys():
                if raster_data['success'] == "false":
                    show_error_message(raster_data['message'])
                    progressDialog.close()
                    return None
                else:
                    show_info_message(raster_data['message'])
                    progressDialog.close()
                    return None
            raster_response = requests.get(raster_data["rasterfile"])
            progressBar.setValue(50)
            if raster_response.status_code == 200:
                progressDialog.setLabelText("Writing Raster File ...")
                progressBar.setValue(60)
                with open(filePath , "wb") as file:
                    file.write(raster_response.content)
                
                qml_path = os.path.join(pluginDir, "data/sld/{}.qml".format(computation))
                # Step 1: Load the GeoTIFF into QGIS
                progressDialog.setLabelText("Loading raster to QGIS...")
                progressBar.setValue(70)
                project = QgsProject.instance()
                filename = filePath.split("/")[-1][0:-4]
                raster_layer = QgsRasterLayer(filePath, filename, 'gdal')
                if not raster_layer.isValid():
                    progressDialog.close()
                    show_error_message("Invalid GeoTiff")
                    return None
                else:
                    progressBar.setValue(80)
                    log("GeoTIFF loaded successfully!")
                    
                    # Step 2: Apply the SLD style from the URL (or from a local file)
                    progressDialog.setLabelText("Loading Style Layer...")
                    progressBar.setValue(90)
                    log(computation)
                    result = raster_layer.loadNamedStyle(qml_path)
                    if result[1]:
                        raster_layer.triggerRepaint()
                        project.instance().addMapLayer(raster_layer)
                        log(f"Current style: {raster_layer.styleManager().currentStyle()}")
                        
                        iface.mapCanvas().refresh()
                        if computation == "Forest Fire":
                            # Set min/max values for the raster renderer if the default range does not match
                            provider = raster_layer.dataProvider()
                            stats = provider.bandStatistics(1, QgsRasterBandStats.All)
                            log(str(stats.minimumValue))
                            log(str(stats.maximumValue))
                            renderer = raster_layer.renderer()
                            renderer.setClassificationMin(stats.minimumValue)
                            renderer.setClassificationMax(stats.maximumValue)

                            # Refresh the layer again to apply the new min/max
                            raster_layer.triggerRepaint()
                            iface.layerTreeView().refreshLayerSymbology(raster_layer.id())
                            iface.mapCanvas().refresh()
                        progressDialog.setLabelText("Done...")
                        progressBar.setValue(100)
                        progressDialog.close()
                        log("SLD applied successfully!")
                        
                    else:
                        log("Failed to apply the SLD style.")
                        progressDialog.close()
                        show_error_message(f"Failed to apply the SLD style.\n {result[0]}")
                        return None
                    return True
            else:
                show_error_message("Error fetching raster. Error code: {}".format(raster_response.status_code))
                return None
        elif str(resp.status_code).startswith("5"):
            log("Could not connect to the MISLANDAFRICA server due to a server error. Error code: {}".format(resp.status_code))
            QMessageBox.critical(None,
                                    QApplication.translate("MISLANDAFRICA", "Error"),
                                    QApplication.translate("MISLANDAFRICA", "Could not connect to the MISLAND-AFRICA server due to a server error. Error code: {}".format(resp.status_code)))
            return None
        
    except requests.exceptions.ConnectionError:
        log('API unable to access server - check internet connection')
        QMessageBox.critical(None,
                                QApplication.translate("MISLAND", "Error"),
                                QApplication.translate("MISLAND", u"Unable to login to MISLAND-AFRICA server. Check your internet connection."))
        resp = None
    except requests.exceptions.Timeout:
        log('API unable to login - general error')
        QMessageBox.critical(None,
                                QApplication.translate("MISLAND", "Error"),
                                QApplication.translate("MISLAND", u"Unable to connect to the MISLAND-AFRICA server."))
        resp = None
    # except Exception as e:
    #     show_error_message(str(e))
    #     return None
    


def getLayers():
    layers = QgsProject.instance().mapLayers().values()
    vector_layers=[layer for layer in layers if layer.type() == QgsMapLayerType.VectorLayer and layer.dataProvider().name()=='ogr']
    vector_names = [layer.name() for layer in vector_layers]
    return vector_names

def getShapefile(parent=None,isActive=False):
    if isActive:
        # Open a file dialog to select a shapefile or GeoJSON
        file_path, _ = QFileDialog.getOpenFileName(
            parent, 'Open Layer File', '', 'Shapefiles (*.shp);;GeoJSON (*.geojson *.json)'
        )
        if file_path:
            return file_path
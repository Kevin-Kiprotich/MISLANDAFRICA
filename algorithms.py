from qgis.core import QgsProcessingFeatureSourceDefinition, QgsApplication, QgsVectorLayer,QgsWkbTypes,QgsProcessing,QgsProject
from qgis.analysis import QgsNativeAlgorithms
from .downloads import show_error_message, show_info_message
from . import log
import shutil
import processing
import json
import os

def dissolvePolygons(layer,path):
    try:
        folder_path = os.path.dirname(path)
        temp_folder = os.path.join(folder_path,'temp')
        
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        # Ensure the input is a valid vector layer containing polygons
        if not isinstance(layer, QgsVectorLayer) or layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            show_error_message("The layer must contain only polygons.")
            return None
        
        # Run the dissolve algorithm
        result = processing.run(
            "native:dissolve",
            {
                'INPUT': layer.source().split('|')[0],
                'FIELD':[''],
                'SEPARATE_DISJOINT': True,
                'OUTPUT': temp_folder+ '/dissolved.geojson' # Output will be in memory
            }
        )

        # Get the dissolved output layer
        dissolved_layer = result['OUTPUT']
        
        # Read the GeoJSON file and convert it to a dictionary
        with open(dissolved_layer, 'r', encoding='utf-8') as file:
            geojson_dict = json.load(file)
            
        # Extract the features list
        features = geojson_dict.get('features', [])
        
        if not features:
            show_error_message("Error dissolving features: Could not read features from dissolve geojson")
            return
        
        # Extract the geometry type (ensure it's a polygon and not multipolygon)
        geometry = features[0]['geometry']

        # If the geometry is a MultiPolygon, convert it to Polygon
        if geometry['type'] == 'MultiPolygon':
            log("Converting MultiPolygon to Polygon.")
            # You can choose to return the first polygon in the MultiPolygon
            # or merge polygons into a single Polygon based on your needs.
            first_polygon = geometry['coordinates'][0]  # Get the first polygon
            geometry = {
                'type': 'Polygon',
                'coordinates': first_polygon
            }
        # Convert the dictionary to a JSON string
        geometry_str = json.dumps(geometry)
        log(geometry_str)
    
    except Exception as e:
        show_error_message(f"Error dissolving the polygons: {str(e)}")
        return None
    shutil.rmtree(temp_folder)
    return geometry_str
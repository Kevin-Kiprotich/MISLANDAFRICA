from .gui.DlgSDGIndicator import Ui_DlgSDGIndicator
from .gui.DlgCarbonStock import Ui_DlgCarbonStock
from .gui.DlgLandCover import Ui_DlgLandCover
from .gui.DlgLandProductivity import Ui_DlgLandProductivity
from qgis.PyQt import QtWidgets


class DlgSDGIndicator(QtWidgets.QDialog, Ui_DlgSDGIndicator):
    def __init__(self, parent=None):
        super(DlgSDGIndicator, self).__init__(parent)

        self.setupUi(self)
        
class DlgCarbonStock(QtWidgets.QDialog, Ui_DlgCarbonStock):
    def __init__(self, parent=None):
        super(DlgCarbonStock,self).__init__(parent)
        
        self.setupUi(self)
        
class DlgLandCover(QtWidgets.QDialog, Ui_DlgLandCover):
    def __init__(self, parent=None):
        super(DlgLandCover,self).__init__(parent)
        
        self.setupUi(self)
        
class DlgLandProductivity(QtWidgets.QDialog, Ui_DlgLandProductivity):
    def __init__(self, parent=None):
        super(DlgLandProductivity,self).__init__(parent)
        
        self.setupUi(self)
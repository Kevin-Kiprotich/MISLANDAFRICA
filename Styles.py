def highlightComboBox(combo_box):
        """
        Highlight the QComboBox by changing its border color.
        """
        combo_box.setStyleSheet("QComboBox { border: 1.5px solid red; }")
        
def resetComboBoxHighlight(combo_box):
    """
    Reset the QComboBox border color to default.
    """
    combo_box.setStyleSheet("")  # Reset to default style

def highlightLineEdit(line_edit):
    """
    Highlight the QLineEdit by changing its border color.
    """
    line_edit.setStyleSheet("QLineEdit { border: 1.5px solid red; }")
    
def resetLineEditHighlight(line_edit):
    """
    Reset the QLineEdit border color to default.
    """
    line_edit.setStyleSheet("")
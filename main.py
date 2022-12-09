
import sys
from PyQt5.QtWidgets import QApplication
from window_login import UiLoginDialog
from window_arduino import UiArduinoDialog
from window_main import UiMainWindow
from window_manage_animal import UiManageAnimalDialog
from window_manage_program import UiManageProgramDialog
from window_new_animal import UiNewAnimalDialog
from window_new_program import UiNewProgramDialog


# This is where the program starts
if __name__ == "__main__":
    app = QApplication(sys.argv)
#    ui = UiLoginDialog()
#    ui = UiArduinoDialog()
#    ui = UiManageAnimalDialog()
#    ui = UiNewAnimalDialog()
#    ui = UiManageProgramDialog()
#    ui = UiNewProgramDialog()
    ui = UiMainWindow()
    ui.show()
    sys.exit(app.exec_())

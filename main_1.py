
from xmcd_gui import Ui_MainWindow
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets

from xmcd_gui_logic_2 import GuiProgram, MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    
    program = GuiProgram(win)
    cwd_style = os.getcwd()
    style_path = cwd_style + "\\Toolery.qss"
    File = open(style_path,'r')

    with File:
        qss = File.read()
        app.setStyleSheet(qss)
    win.setFocus()
    win.show()
    sys.exit(app.exec_())
import main_1
import sys
import os

def main():
    app = main_1.QtWidgets.QApplication(sys.argv)
    win = main_1.MainWindow()

    program = main_1.GuiProgram(win)
    cwd_style = os.getcwd()
    style_path = cwd_style + "\\Toolery.qss"
    File = open(style_path, 'r')

    with File:
        qss = File.read()
        app.setStyleSheet(qss)
    win.setFocus()
    win.show()
    sys.exit(app.exec_())

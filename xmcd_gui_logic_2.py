from multiprocessing.sharedctypes import Value

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavBar
)
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from xmcd_gui import Ui_MainWindow
import os
import time
import pandas as pd
import numpy as np
from skimage.registration import phase_cross_correlation
from scipy.ndimage import fourier_shift
from matplotlib.image import imread

import matplotlib
matplotlib.use("Qt5Agg")


class InfoDialog(QtWidgets.QDialog):
    def __init__(self, path):
        super().__init__()
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
        self.path = path

        info_text = ""
        with open(self.path, "r") as f:
            for row in f:
                info_text += row

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QTextBrowser()
        message.append(info_text)
        self.layout.addWidget(message)
        self.setLayout(self.layout)


class GuiProgram(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, MainWindow):
        super().__init__()
        Ui_MainWindow.__init__(self) 
                    # Initialize Window
        self.setupUi(MainWindow)                  # Set up the UI
        # Initialize the figure in our window
        
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("SoftiMAX XMCD viewer") 
        figure_cp = Figure()
        figure_cm = Figure()
        figure_xmcd = Figure()
        axis_cp = figure_cp.add_subplot(111)
        axis_cm = figure_cm.add_subplot(111)
        axis_xmcd = figure_xmcd.add_subplot(121)
        axis_xmcd_2 = figure_xmcd.add_subplot(122)
        self.add_combo_elems()

        self.fig_xmcd = figure_xmcd
        self.ax_xmcd = axis_xmcd
        self.ax_xmcd_2 = axis_xmcd_2

        '''ax1 = plt.subplot(1, 2, 1)
        ax2 = plt.subplot(1, 2, 2, sharex=ax1, sharey=ax1)'''

        self.browse_cp.clicked.connect(self.browse_files_cp)
        self.browse_cm.clicked.connect(self.browse_files_cm)

        # Prep empty plot
        self.initialize_figure_cp(figure_cp, axis_cp)  # Initialize!
        self.initialize_figure_cm(figure_cm, axis_cm)
        self.initialize_figure_xmcd(figure_xmcd)

        # Connect our button with plotting function
        
        self.cp_button.clicked.connect(
            lambda: self.change_plot_cp(figure_cp, axis_cp))       
          
        self.cm_button.clicked.connect(
            lambda: self.change_plot_cm(figure_cm, axis_cm))
        self.xmcd_button.clicked.connect(
            lambda: self.change_plot_xmcd(figure_xmcd, axis_xmcd, axis_xmcd_2))
        self.button_reset.clicked.connect(
            lambda: self.change_plot_xmcd(figure_xmcd, axis_xmcd, axis_xmcd_2))
        


        self.menu_action_tips = QtWidgets.QAction("Tips", self)
        self.menu_action_info = QtWidgets.QAction("Info", self)
        self.menu_action_tips.triggered.connect(self.show_tips)
        self.menu_action_info.triggered.connect(self.show_info)
        self.menuInfo.addAction(self.menu_action_tips)
        self.menuInfo.addAction(self.menu_action_info)

        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.setExclusive(True)
        self.btn_grp.addButton(self.button_right)
        self.btn_grp.addButton(self.button_left)
        self.btn_grp.addButton(self.button_up)
        self.btn_grp.addButton(self.button_down)
        self.shift = [0, 0]

        self.btn_grp.buttonClicked.connect(self.one_clicked)
        self.btn_grp.buttonClicked.connect(lambda: self.change_plot_xmcd_manual(figure_xmcd, axis_xmcd, axis_xmcd_2))     


    def one_clicked(self, value):  
        val = value.text()
        if self.lineEdit_shift.text() == "" or self.lineEdit_shift.text() == '0' or len(self.lineEdit_shift.text()):
            shift_val = 0.5
        if "," in self.lineEdit_shift.text() or " " in self.lineEdit_shift.text() and len(self.lineEdit_shift.text()) != 0:
            
            str_nou = ""
            for i in range(len(self.lineEdit_shift.text())):                
                
                if self.lineEdit_shift.text()[i] == ',':
                    str_nou+="."
                elif self.lineEdit_shift.text()[i] == " ":
                    str_nou += ""
                else:
                    str_nou+=self.lineEdit_shift.text()[i]
            
            shift_val = float(str_nou)

        if val == "Up":
            self.shift[0] += shift_val
            #print(self.shift)
        elif val == "Down":
            self.shift[0] -= shift_val
            #print(self.shift)
        elif val == "Left":
            self.shift[1] -= shift_val
            #print(self.shift)
        elif val == "Right":
            self.shift[1] += shift_val
            #print(self.shift)


                
        
        
        
        #change_xmcd_plot_manual(fig, ax, ax2, shift)

    # @QtCore.pyqtSlot(QtWidgets.QAction)
    def show_info(self):
        path = os.getcwd() + "\\info.txt"
        dlg = InfoDialog(path)
        dlg.setWindowTitle("Info")
        dlg.exec()

    def show_tips(self):
        path = os.getcwd() + "\\tips.txt"
        dlg = InfoDialog(path)
        dlg.setWindowTitle("Tips")
        dlg.setMinimumWidth(550)
        dlg.exec()

    def get_image(self, path):
        if os.path.exists(path):
            try:
                image = np.array(pd.read_csv(path, sep='\t'))
                image[np.isnan(image)] = 0
                return image
            except FileNotFoundError as e:
                self.label_output.setText("No no")
        else:
            print("Not found path")


        
        # Remove Nans from the arrays and set them to 0
        

    def change_plot_cp(self, fig, ax):
        ''' Plots something new in the figure. '''
        # Clear whatever was in the plot before
        self.fig = fig
        self.ax = ax
        color = self.comboBox_cmap.currentText()
        
        path_cp = self.lineEdit_cp.text()
        

        if path_cp == "":
            self.label_output.setText("OBS: Please select a C+ image file!")

        elif not os.path.exists(path_cp):
            self.label_output.setText("OBS: Please select a valid path to a C+ image!")
        else:
            
            self.ax.clear()
            # Plot data, add labels, change colors, ...
            
            self.label_output.setText("")
            plot_image = self.get_image(path_cp)
            try:
                self.ax.set_xlabel('X ($\mu$m)')
                self.ax.set_ylabel('Y ($\mu$m)')
                min_max_dim = self.get_dimensions(path_cp)
                self.ax.imshow(plot_image, cmap=color, extent=min_max_dim)
            except:
                self.ax.set_xlabel('X (px)')
                self.ax.set_ylabel('Y (px)')
                self.ax.imshow(plot_image, cmap=color)
                self.label_output.setText(
                    "OBS: It seems you're missing a header (.hdr) file.")
                 
            
            
            # Make sure everything fits inside the canvas
            #self.fig.tight_layout()
            # Show the new figure in the interface
            self.canvas_cp.draw()
             
        '''
        variable_test = self.test_method()
        print(f"Test return var: {variable_test}")'''

    def change_plot_cm(self, fig, ax):
        self.label_output.setText("")
        ''' Plots something new in the figure. '''
        # Clear whatever was in the plot before
        self.fig = fig
        self.ax = ax
        color = self.comboBox_cmap.currentText()
        path_cm = self.lineEdit_cm.text()

        if path_cm == "":
            self.label_output.setText("OBS: Please select a C- image file!")
        elif not os.path.exists(path_cm):
            self.label_output.setText("OBS: Please select a valid path to a C- image!")
        else:
            self.ax.clear()
            # Plot data, add labels, change colors, ...
            
            self.label_output.setText("")
            
            plot_image = self.get_image(path_cm)
            try:
                self.ax.set_xlabel('X ($\mu$m)')
                self.ax.set_ylabel('Y ($\mu$m)')
                min_max_dim = self.get_dimensions(path_cm)
                self.ax.imshow(plot_image, cmap=color, extent=min_max_dim)
            except:
                self.ax.set_xlabel('X (px)')
                self.ax.set_ylabel('Y (px)')
                self.ax.imshow(plot_image, cmap=color)
                self.label_output.setText("OBS: It seems you're missing a header (.hdr) file.")
            
            #self.fig.tight_layout()
            # Show the new figure in the interface
            self.canvas_cm.draw()

    def change_plot_xmcd(self, fig, ax, ax2):
        ''' Plots something new in the figure. '''
        # Clear whatever was in the plot before
        self.shift = [0, 0]
        self.fig = fig
        self.ax = ax
        self.ax2 = ax2
        path_cm = self.lineEdit_cm.text()
        path_cp = self.lineEdit_cp.text()
        color = self.comboBox_cmap.currentText()
        if path_cm == "" or path_cp == "":
            self.label_output.setText(
                "OBS: Please select both C+ and C- files!")
        elif not os.path.exists(path_cp) or not os.path.exists(path_cm):
            self.label_output.setText("OBS: Please select valid paths!!!")
        else:
            self.ax.clear()
            self.label_output.setText("")
            # Plot data, add labels, change colors, ...
            img_cm = self.get_image(path_cm)
            img_cp = self.get_image(path_cp)
            
            
            try:
                shift, error, diffphase = phase_cross_correlation(
                    img_cp, img_cm, upsample_factor=100)
                self.label_output.setText(f"The C- image was automatically shifted by: [{shift[0]:.2f},{shift[1]:.2f}]")
                offset_img_cm = fourier_shift(np.fft.fftn(img_cm), shift)
                offset_img_cm = np.real(np.fft.ifftn(offset_img_cm))

                xmcd_im = (img_cp - offset_img_cm)/(img_cp + offset_img_cm)

                norm_img_cm = self.norm_images(img_cp, offset_img_cm)
                xmcd_im_norm = (img_cp - norm_img_cm)/(img_cp + norm_img_cm)
                self.ax2.yaxis.set_label_position("right")
                self.ax2.yaxis.tick_right()
                try:
                    min_max_dim = self.get_dimensions(path_cp)
                    extra = self.get_dimensions(path_cm)
                    self.ax.set_xlabel('X ($\mu$m)')
                    self.ax.set_ylabel('Y ($\mu$m)')
                    self.ax2.set_xlabel('X ($\mu$m)')
                    self.ax2.set_ylabel('Y ($\mu$m)')
                    self.ax.imshow(xmcd_im, cmap=color, extent = min_max_dim)
                    self.ax2.imshow(xmcd_im_norm, cmap=color, extent = min_max_dim)
                except:
                    self.ax.set_xlabel('X (px)')
                    self.ax.set_ylabel('Y (px)')
                    self.ax2.set_xlabel('X (px)')
                    self.ax2.set_ylabel('Y (px)')
                    self.ax.imshow(xmcd_im, cmap=color)
                    self.ax2.imshow(xmcd_im_norm, cmap=color)
                    self.label_output.setText(
                        f"OBS: You're either missing a header file (.hdr) or the two images are very different (not of the same thing).\nThe C- image was shifted by: [{shift[0]:.2f},{shift[1]:.2f}]")

                self.ax.set_title("Without normalization")
                self.ax2.set_title("With normalization")
                # Make sure everything fits inside the canvas
                #self.fig.tight_layout()
                # Show the new figure in the interface
                self.canvas_xmcd.draw()
            except ValueError as ve:
                self.label_output.setText(f"Error: {ve}")

            

    def change_plot_xmcd_manual(self, fig, ax, ax2):
        ''' Plots something new in the figure. '''
        # Clear whatever was in the plot before
        
        self.fig = fig
        
        self.ax = ax
        self.ax2 = ax2
        path_cm = self.lineEdit_cm.text()
        path_cp = self.lineEdit_cp.text()
        color = self.comboBox_cmap.currentText()
        if path_cm == "" or path_cp == "":
            self.label_output.setText(
                "OBS: Please select both C+ and C- files!")
        elif not os.path.exists(path_cp) or not os.path.exists(path_cm):
            self.label_output.setText("OBS: Please select valid paths!!!")
        else:
            try:
                self.ax.clear()
                self.label_output.setText("")
                # Plot data, add labels, change colors, ...
                img_cm = self.get_image(path_cm)
                img_cp = self.get_image(path_cp)

                self.label_output.setText(f"The C- image was shifted by: [{self.shift[0]:.2f},{self.shift[1]:.2f}]")
                offset_img_cm = fourier_shift(np.fft.fftn(img_cm), self.shift)
                offset_img_cm = np.real(np.fft.ifftn(offset_img_cm))

                xmcd_im = (img_cp - offset_img_cm)/(img_cp + offset_img_cm)

                norm_img_cm = self.norm_images(img_cp, offset_img_cm)
                xmcd_im_norm = (img_cp - norm_img_cm)/(img_cp + norm_img_cm)
                self.ax2.yaxis.set_label_position("right")
                self.ax2.yaxis.tick_right()
                try:
                    min_max_dim = self.get_dimensions(path_cp)
                    extra = self.get_dimensions(path_cm)
                    self.ax.set_xlabel('X ($\mu$m)')
                    self.ax.set_ylabel('Y ($\mu$m)')
                    self.ax2.set_xlabel('X ($\mu$m)')
                    self.ax2.set_ylabel('Y ($\mu$m)')
                    self.ax.imshow(xmcd_im, cmap=color, extent=min_max_dim)
                    self.ax2.imshow(xmcd_im_norm, cmap=color,
                                    extent=min_max_dim)
                except:
                    self.ax.set_xlabel('X (px)')
                    self.ax.set_ylabel('Y (px)')
                    self.ax2.set_xlabel('X (px)')
                    self.ax2.set_ylabel('Y (px)')
                    self.ax.imshow(xmcd_im, cmap=color)
                    self.ax2.imshow(xmcd_im_norm, cmap=color)
                    self.label_output.setText(f"OBS: You're either missing a header file (.hdr) or the two images are very different (not of the same thing).\nThe C- image was shifted by: [{self.shift[0]:.2f},{self.shift[1]:.2f}]")
                
                self.ax.set_title("Without normalization")
                self.ax2.set_title("With normalization")
                # Make sure everything fits inside the canvas
                #self.fig.tight_layout()
                # Show the new figure in the interface
                self.canvas_xmcd.draw()
            except ValueError as ve:
                self.label_output.setText(f"Error: {ve}")

    def initialize_figure_cp(self, fig, ax):

        # Figure creation (self.fig and self.ax)
        self.fig = fig
        self.ax = ax
        # Canvas creation
        self.canvas_cp = FigureCanvas(fig)
        self.plotLayout_cp.addWidget(self.canvas_cp)
        self.canvas_cp.draw()
        # Toolbar creation
        self.toolbar_cp = NavBar(self.canvas_cp, self.plotWindow_cp,
                                 coordinates=True)
        self.plotLayout_cp.addWidget(self.toolbar_cp)

    def initialize_figure_cm(self, fig, ax):
        
        # Figure creation (self.fig and self.ax)
        self.fig = fig
        self.ax = ax
        # Canvas creation
        self.canvas_cm = FigureCanvas(fig)
        self.plotLayout_cm.addWidget(self.canvas_cm)
        self.canvas_cm.draw()
        # Toolbar creation
        self.toolbar_cm = NavBar(self.canvas_cm, self.plotWindow_2,
                                 coordinates=True)
        self.plotLayout_cm.addWidget(self.toolbar_cm)

    def initialize_figure_xmcd(self, fig):

        # Figure creation (self.fig and self.ax)
        self.fig = fig
        
        # Canvas creation
        self.canvas_xmcd = FigureCanvas(fig)
        self.plotLayout_xmcd.addWidget(self.canvas_xmcd)
        self.canvas_xmcd.draw()
        # Toolbar creation
        self.toolbar_xmcd = NavBar(self.canvas_xmcd, self.plotWindow_3,
                                   coordinates=True)
        self.plotLayout_xmcd.addWidget(self.toolbar_xmcd)

    def browse_files_cp(self):
        # browse buttons

        fname_cp = QtWidgets.QFileDialog.getOpenFileName(filter="*.xim")
        self.lineEdit_cp.setText(fname_cp[0])

    def browse_files_cm(self):
        # browse buttons

        fname_cm = QtWidgets.QFileDialog.getOpenFileName(filter="*.xim")
        self.lineEdit_cm.setText(fname_cm[0])

    def norm_images(self, img1, img2):
        I1 = np.median(img1)
        I2 = np.median(img2)
        norm_img2 = img2*I1/I2
        return norm_img2

    def get_dimensions(self, path2):
        
        path2_splt = path2.split("/")
        last_elem = path2_splt[-1].split("_a")
        new_path2 = "\\".join(path2_splt[:-1]) + "\\" + last_elem[0] + ".hdr"
        path = new_path2

        row_tst_x = []
        row_tst_y = []

        with open(path, 'r') as f_dim:
            for idx, row in enumerate(f_dim):
                if idx == 4:
                    row_tst_x = row
                if idx == 8:
                    row_tst_y = row
        f_dim.close()

        res_x = [s for s in row_tst_x.split("; ")]
        min_x = [s for s in res_x[2].split(" ")]
        max_x = [s for s in res_x[3].split(" ")]
        res_y = [s for s in row_tst_y.split("; ")]
        min_y = [s for s in res_y[2].split(" ")]
        max_y = [s for s in res_y[3].split(" ")]


        min_x = float(min_x[2])
        max_x = float(max_x[2])
        min_y = float(min_y[2])
        max_y = float(max_y[2])

        lst_return = [min_x, max_x, min_y, max_y]
        return lst_return
    

    def add_combo_elems(self):
        lst_of_cmaps = ['gray', 'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r',
                        'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd',
                        'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2',
                        'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples',
                        'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds',
                        'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn',
                        'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r',
                        'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm',
                        'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r',
                        'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r',
                        'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma',
                        'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r',
                        'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r',
                        'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r']

        for elem in lst_of_cmaps:
            self.comboBox_cmap.addItem(elem)

    def move_xmcd(self, shift):        
        print("It works apparently", shift)
        print("self in Gui is: ", self)
        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("SoftiMAX XMCD viewer")
         
        
    
    

    

    
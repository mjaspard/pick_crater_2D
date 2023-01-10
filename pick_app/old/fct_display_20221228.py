from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import numpy as np
import os, math, re, time
import datetime as datetime
from osgeo import gdal
from PyQt5 import QtCore


# import numpy as np
# import os as os
# from netCDF4 import Dataset
# from mpl_toolkits import mplot3d
# from mpl_toolkits.mplot3d import axes3d
# from matplotlib import patches
# import matplotlib.pyplot as plt






# def displayTest(self):

#     figure = Figure()
#     axes = figure.gca()
#     axes.set_title("My Plot")
#     x = np.linspace(1, 10)
#     y = np.linspace(1, 10)
#     y1 = np.linspace(11, 20)
#     axes.plot(x, y, "-k", label="first one")
#     axes.plot(x, y1, "-b", label="second one")
#     axes.legend()
#     axes.grid(True)
#     # Canvas creation
#     canvas = FigureCanvas(figure)

#     return canvas

#===============================================================================================================
#====================    AMPLITUDE IMAGE     ===================================================================
#===============================================================================================================


def getSARFig(self):
    """ Function to draw SAR image in canvas """

    # File name
    i = self.index_live
    dataset = self.dataset

    img_dir = dataset['folder'][i]
    img_name = dataset['img_name'][i]
    filepath = os.path.join(img_dir, img_name)
    filepath_filter = filepath.replace(".r4", "_Filtre.r4")
    satname = img_dir.split('/')[-2]

    # Acquisition time
    img_date_string = dataset['day'][i]
    img_date = datetime.datetime.strptime(str(img_date_string), "%Y%m%d")

    # Pixel size and incidence angle
    azimuth_pixel_size = dataset['azimuth_pixel_size'][i]
    range_pixel_size = dataset['range_pixel_size'][i]
    incidence_angle_deg = dataset['incidence_angle_deg'][i]
    incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360

    # Caldera ellipse
    caldera_edgeN_x = dataset['caldera_edgeN_x'][i]
    caldera_edgeN_y = dataset['caldera_edgeN_y'][i]
    caldera_edgeS_x = dataset['caldera_edgeS_x'][i]
    caldera_edgeS_y = dataset['caldera_edgeS_y'][i]

    # Crater outer ellipse
    crater_outer_edgeN_x = dataset['crater_outer_edgeN_x'][i]
    crater_outer_edgeN_y = dataset['crater_outer_edgeN_y'][i]
    crater_outer_edgeS_x = dataset['crater_outer_edgeS_x'][i]
    crater_outer_edgeS_y = dataset['crater_outer_edgeS_y'][i]

    # Crater inner ellipse
    crater_inner_edgeN_x = dataset['crater_inner_edgeN_x'][i]
    crater_inner_edgeN_y = dataset['crater_inner_edgeN_y'][i]
    crater_inner_edgeS_x = dataset['crater_inner_edgeS_x'][i]
    crater_inner_edgeS_y = dataset['crater_inner_edgeS_y'][i]

    # Crater outer ellipse
    crater_topCone_edgeN_x = dataset['crater_topCone_edgeN_x'][i]
    crater_topCone_edgeN_y = dataset['crater_topCone_edgeN_y'][i]
    crater_topCone_edgeS_x = dataset['crater_topCone_edgeS_x'][i]
    crater_topCone_edgeS_y = dataset['crater_topCone_edgeS_y'][i]

    # Crater outer ellipse
    crater_bottom_edgeN_x = dataset['crater_bottom_edgeN_x'][i]
    crater_bottom_edgeN_y = dataset['crater_bottom_edgeN_y'][i]
    crater_bottom_edgeS_x = dataset['crater_bottom_edgeS_x'][i]
    crater_bottom_edgeS_y = dataset['crater_bottom_edgeS_y'][i]


    expo_greyscale = dataset['expo_greyscale'][i] 

    
    # print("!!! Coordinate caldera_N = ", dataset['crater_outer_edgeN_x'][i])
    # print("index i = ", i)


    # Open the file:
    if self.pushButton_filtered_SAR.isChecked():
        file_to_open = filepath_filter
    else:
        file_to_open = filepath
    Raster = gdal.Open(file_to_open)

    # print("file_to_open = ",file_to_open)
    # Extract data from envi file
    Band   = Raster.GetRasterBand(1) # 1 based, for this example only the first
    NoData = Band.GetNoDataValue()  # this might be important later
    nBands = Raster.RasterCount      # how many bands, to help you loop
    nRows  = Raster.RasterYSize      # how many rows
    nCols  = Raster.RasterXSize      # how many columns
    dType  = Band.DataType          # the datatype for this band

    # Extract band
    inputArray = (np.array(Band.ReadAsArray()**expo_greyscale))


    # Cleanup
    del Raster, Band


   
    #--------------------- Calculate ellipse + profile ccordinate -----------------#

    if self.pushButton_ellipse.isChecked():
        # Parameter for curvilinear coordinates of ellipse
        t = np.linspace(0, 2*np.pi, 100)
        # Ellipses
        [caldera_ellipse_x, caldera_ellipse_y] = ellipse_equation_2p(caldera_edgeN_x, caldera_edgeN_y, caldera_edgeS_x, caldera_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_outer_ellipse_x, crater_outer_ellipse_y] = ellipse_equation_2p(crater_outer_edgeN_x, crater_outer_edgeN_y, crater_outer_edgeS_x, crater_outer_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_inner_ellipse_x, crater_inner_ellipse_y] = ellipse_equation_2p(crater_inner_edgeN_x, crater_inner_edgeN_y, crater_inner_edgeS_x, crater_inner_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_topCone_ellipse_x, crater_topCone_ellipse_y] = ellipse_equation_2p(crater_topCone_edgeN_x, crater_topCone_edgeN_y, crater_topCone_edgeS_x, crater_topCone_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)
        [crater_bottom_ellipse_x, crater_bottom_ellipse_y] = ellipse_equation_2p(crater_bottom_edgeN_x, crater_bottom_edgeN_y, crater_bottom_edgeS_x, crater_bottom_edgeS_y, azimuth_pixel_size, range_pixel_size, incidence_angle_deg, t)




    #========================== DRAW FIGURE ================================#


    # matplotlib.style.use('seaborn-talk')

    self.figure = Figure()
    self.ax = self.figure.gca()
    self.ax.set_title("{}:{}".format(satname, img_date_string))

    if self.pushButton_filtered_SAR.isChecked():    # Need to rescale mi/max between 0 and 1
        vmin = float((self.SAR_clip_min.value()/255))
        vmax = float((self.SAR_clip_max.value()/255))
    else:
        vmin = int(self.SAR_clip_min.value())
        vmax = int(self.SAR_clip_max.value())
    # print("greyscale, vmin, vmax =", expo_greyscale, vmin, vmax)
    if vmin < vmax:
        self.ax.imshow(inputArray, cmap='Greys_r', vmin=vmin, vmax=vmax)
    else:
        print("Value not coherent to display this image : please check clip value!")


    if self.pushButton_ellipse.isChecked():
        self.ax.plot(caldera_ellipse_x, caldera_ellipse_y, color='blue', alpha=0.8)
        self.ax.plot(crater_outer_ellipse_x, crater_outer_ellipse_y, color='skyblue', alpha=0.8)
        self.ax.plot(crater_inner_ellipse_x, crater_inner_ellipse_y, color='red', alpha=0.8)
        self.ax.plot(crater_topCone_ellipse_x, crater_topCone_ellipse_y, color='orange', alpha=0.8)
        self.ax.plot(crater_bottom_ellipse_x, crater_bottom_ellipse_y, color='magenta', alpha=0.8)
        self.ax.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

        self.ax.plot(caldera_edgeN_x,caldera_edgeN_y,marker="o", markeredgecolor="blue", markerfacecolor="blue")
        self.ax.plot(caldera_edgeS_x,caldera_edgeS_y,marker="o", markeredgecolor="blue", markerfacecolor="blue")
        self.ax.plot(crater_outer_edgeN_x,crater_outer_edgeN_y,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
        self.ax.plot(crater_outer_edgeS_x,crater_outer_edgeS_y,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
        self.ax.plot(crater_inner_edgeN_x,crater_inner_edgeN_y,marker="o", markeredgecolor="red", markerfacecolor="red")
        self.ax.plot(crater_inner_edgeS_x,crater_inner_edgeS_y,marker="o", markeredgecolor="red", markerfacecolor="red")
        self.ax.plot(crater_topCone_edgeN_x,crater_topCone_edgeN_y,marker="o", markeredgecolor="orange", markerfacecolor="orange")
        self.ax.plot(crater_topCone_edgeN_x,crater_topCone_edgeS_y,marker="o", markeredgecolor="orange", markerfacecolor="orange")
        self.ax.plot(crater_bottom_edgeN_x,crater_bottom_edgeN_y,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
        self.ax.plot(crater_bottom_edgeS_x,crater_bottom_edgeS_y,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
    
    # restore previous zoom value
    print("self.SAR_zoom = ", self.SAR_zoom)
    if self.SAR_zoom:
        print("set zoom value :", self.lim_x, self.lim_y)
        self.ax.set_xlim(self.lim_x)
        self.ax.set_ylim(self.lim_y)




    # self.canvas.mpl_connect('key_press_event', lambda event: on_key(event, self)) 
    self.figure.canvas.mpl_connect('button_press_event', lambda event: onclick(event, self))
    self.figure.canvas.mpl_connect('key_press_event', lambda event: on_key(event, self))   # Do not work !!! Why ???


    self.ax.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

    # Canvas creation
    self.canvas = FigureCanvas(self.figure)
    self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    self.canvas.setFocus()




    return self.canvas



#===============================================================================================================
#====================    PROFILE      ==========================================================================
#===============================================================================================================

from input_shape import *

def getProfileFig(self):
    """ Function to draw SAR image in canvas """

    # File name
    i = self.index_live
    dataset = self.dataset


    # Pixel size and incidence angle
    azimuth_pixel_size = dataset['azimuth_pixel_size'][i]
    range_pixel_size = dataset['range_pixel_size'][i]
    incidence_angle_deg = dataset['incidence_angle_deg'][i]
    incidence_angle_rad = (incidence_angle_deg * 2 * math.pi)/360

    # Caldera ellipse
    caldera_edgeN_x = dataset['caldera_edgeN_x'][i]
    caldera_edgeN_y = dataset['caldera_edgeN_y'][i]
    caldera_edgeS_x = dataset['caldera_edgeS_x'][i]
    caldera_edgeS_y = dataset['caldera_edgeS_y'][i]

    # Crater outer ellipse
    crater_outer_edgeN_x = dataset['crater_outer_edgeN_x'][i]
    crater_outer_edgeN_y = dataset['crater_outer_edgeN_y'][i]
    crater_outer_edgeS_x = dataset['crater_outer_edgeS_x'][i]
    crater_outer_edgeS_y = dataset['crater_outer_edgeS_y'][i]

    # Crater inner ellipse
    crater_inner_edgeN_x = dataset['crater_inner_edgeN_x'][i]
    crater_inner_edgeN_y = dataset['crater_inner_edgeN_y'][i]
    crater_inner_edgeS_x = dataset['crater_inner_edgeS_x'][i]
    crater_inner_edgeS_y = dataset['crater_inner_edgeS_y'][i]

    # Crater outer ellipse
    crater_topCone_edgeN_x = dataset['crater_topCone_edgeN_x'][i]
    crater_topCone_edgeN_y = dataset['crater_topCone_edgeN_y'][i]
    crater_topCone_edgeS_x = dataset['crater_topCone_edgeS_x'][i]
    crater_topCone_edgeS_y = dataset['crater_topCone_edgeS_y'][i]

    # Crater outer ellipse
    crater_bottom_edgeN_x = dataset['crater_bottom_edgeN_x'][i]
    crater_bottom_edgeN_y = dataset['crater_bottom_edgeN_y'][i]
    crater_bottom_edgeS_x = dataset['crater_bottom_edgeS_x'][i]
    crater_bottom_edgeS_y = dataset['crater_bottom_edgeS_y'][i]


####### Draw picked topography ###########

    # >=P2
    Ix = -((caldera_edgeS_y - caldera_edgeN_y)/2)*azimuth_pixel_size
    Iy = Zvolc

    Jx = ((caldera_edgeS_y - caldera_edgeN_y)/2)*azimuth_pixel_size
    Jy = Zvolc

    Kx = -((crater_outer_edgeS_y - crater_outer_edgeN_y)/2)*azimuth_pixel_size
    a1 = abs(crater_outer_edgeN_x - caldera_edgeN_x)*range_pixel_size
    h1 = int(a1 / np.cos(incidence_angle_rad))
    Ky = Iy - h1

    Lx = -Kx
    Ly = Ky


    # P2
    a2 = (crater_outer_edgeN_x - crater_inner_edgeN_x)*range_pixel_size
    delta_x = (a2)/(np.sin(incidence_angle_rad))
    Cx = delta_x - (((crater_inner_edgeS_y - crater_inner_edgeN_y)/2)*azimuth_pixel_size)
    Cy = Ky

    Dx = delta_x + (((crater_inner_edgeS_y - crater_inner_edgeN_y)/2)*azimuth_pixel_size)
    Dy = Ky

    # <P2
    Ux = Cx
    a3 = abs(crater_topCone_edgeN_x - crater_inner_edgeN_x)*range_pixel_size
    h2 = a3/np.cos(incidence_angle_rad)
    Uy = Cy - h2

    Vx = Dx
    Vy = Uy

    # Cone
    Ex = delta_x - (((crater_bottom_edgeN_y - crater_topCone_edgeN_y)/2)*azimuth_pixel_size)
    a4 = abs(crater_bottom_edgeN_x - crater_topCone_edgeN_x)*range_pixel_size
    h3 = a3/np.cos(incidence_angle_rad)
    Ey = Uy - h3

    Fx = delta_x + (((crater_bottom_edgeN_y - crater_topCone_edgeN_y)/2)*azimuth_pixel_size)
    Fy = Ey



    # Create array to draw profile


    X_profile_1 = [-2500, Ix, Kx]   # flanc caldera
    Y_profile_1 = [2500, Iy, Ky]

    X_profile_2 = [Kx, Cx]  # P2
    Y_profile_2 = [Ky, Cy]

    X_profile_3 = [Cx, Dx]  # crater top
    Y_profile_3 = [Cy, Dy]

    X_profile_4 = [Cx, Ux]  # flanc cratere vertical
    Y_profile_4 = [Cy, Uy]  

    X_profile_5 = [Ux, Vx]  # middle 
    Y_profile_5 = [Uy, Vy]  

    X_profile_6 = [Ux, Ex]  # flanc crater conique
    Y_profile_6 = [Uy, Ey]  

    X_profile_7 = [Fx, Ex]  # bottom
    Y_profile_7 = [Fy, Ey]  

    X_profile_66 = [Fx, Vx]
    Y_profile_66 = [Fy, Vy] 

    X_profile_44 = [Dx, Vx]
    Y_profile_44 = [Dy, Vy]

    X_profile_22 = [Dx, Lx]
    Y_profile_22 = [Dy, Ly]

    X_profile_11 = [Lx, Jx, 2500]
    Y_profile_11 = [Ly, Jy, 2500]


    
   
    #========================== DRAW FIGURE ================================#


    # matplotlib.style.use('seaborn-talk')

    self.figure_profile = Figure()
    self.ax1 = self.figure_profile.gca()
    # self.ax1.set_title("{}:{}".format(satname, img_date_string))

  

    self.ax1.set_title("profile from picking points")
    # Caldera
    self.ax1.plot(Ix,Iy,marker="o", markeredgecolor="blue", markerfacecolor="blue")
    self.ax1.plot(X_profile_1, Y_profile_1, color='black')
    self.ax1.plot(Jx,Jy,marker="o", markeredgecolor="blue", markerfacecolor="blue")
    self.ax1.plot(X_profile_11, Y_profile_11, color='black')

    # Crater outer = P2
    self.ax1.plot(Lx,Ly,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
    self.ax1.plot(X_profile_2, Y_profile_2, color='skyblue')
    self.ax1.plot(Kx,Ky,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
    self.ax1.plot(X_profile_22, Y_profile_22, color='skyblue')

    # Crater at top position (level P2)
    self.ax1.plot(Cx,Cy,marker="o", markeredgecolor="red", markerfacecolor="red")
    self.ax1.plot(Dx,Dy,marker="o", markeredgecolor="red", markerfacecolor="red")
    self.ax1.plot(X_profile_3, Y_profile_3, color='red',linestyle='dashed', linewidth=1)


    self.ax1.plot(X_profile_4, Y_profile_4, color='black')
    self.ax1.plot(X_profile_44, Y_profile_44, color='black')

    # Crater at middle position (Between bottom and top)
    self.ax1.plot(Ux,Uy,marker="o", markeredgecolor="orange", markerfacecolor="orange")
    self.ax1.plot(Vx,Vy,marker="o", markeredgecolor="orange", markerfacecolor="orange")
    self.ax1.plot(X_profile_5, Y_profile_5, color='orange',linestyle='dashed', linewidth=1)


    self.ax1.plot(X_profile_6, Y_profile_6, color='black')
    self.ax1.plot(X_profile_66, Y_profile_66, color='black')

    # Crater at bottom
    self.ax1.plot(Ex,Ey,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
    self.ax1.plot(Fx,Fy,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
    self.ax1.plot(X_profile_7, Y_profile_7, color='magenta',linestyle='dashed', linewidth=1)


    self.ax1.set_xlim(-1000, 1000)
    self.ax1.set_ylim(2200, 3600)
    self.ax1.set_xlabel('[m]')
    self.ax1.set_ylabel('[m]')
    self.ax1.text(0, 3500, "P2 from top = {}m".format(h1))
    self.ax1.text(0, 3450, "Caldera Radius= {}m".format(Jx))
    self.ax1.text(0, 3400, "P2 radius = {}m".format(Lx))
    self.ax1.text(0, 3550, "delta X = {}m".format(delta_x))
  

    # Create event when mouse clicking on profile
    self.figure_profile.canvas.mpl_connect('button_press_event', lambda event: onclick_profile(event, self))

    self.ax1.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

    # Canvas creation
    self.canvas_profile = FigureCanvas(self.figure_profile)
    # self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
    # self.canvas.setFocus()




    return self.canvas_profile



#===============================================================================================================
#====================    FUNCTION     ==========================================================================
#===============================================================================================================



# Ellipse stuff
def ellipse_equation_2p(top_x, top_y, bot_x, bot_y, az_pix_size, ra_pix_size, theta,t):
    u = top_x
    v = int((int(bot_y) - int(top_y))/2 + top_y)
    a = int((int(bot_y) - int(top_y))/2)
    theta_rad = (theta * (2*math.pi))/360
    b = a*((az_pix_size*np.sin(theta_rad))/ra_pix_size)
    # print("theta = {}, theta_rad = {}, a = {}, b = {}".format(theta, theta_rad, a, b))
    return np.array([u+b*np.cos(t) , v+a*np.sin(t)])

def ellipse_equation(u, v, a, b, t):
    return np.array([u+a*np.cos(t) , v+b*np.sin(t)])

def ellipse_tilt_equation(u, v, a_x,a_y, b_x,b_y, t,theta):
    a = np.sqrt((a_x-u)**2 + (a_y-v)**2)
    b = np.sqrt((b_x-u)**2 + (b_y-v)**2)
    return np.array([u+a*np.cos(t)*np.cos(theta) - b*np.sin(t)*np.sin(theta) , v+a*np.cos(t)*np.sin(theta)+b*np.sin(t)*np.cos(theta)])

def ellipse_area(a,b):
    return np.pi*a*b


#================== Picking Amplitude Image (SAR) function =========================#

def pick_point(self, info_str, x, y):
    """Function that will write in the dictionary "inages_data" new coordinate of clicked point"""
    x_str = "{}_x".format(info_str)
    y_str = "{}_y".format(info_str)
    # print("{} = [{}:{}]".format(info_str, x, y))
    self.dataset[x_str][self.index_live] = round(x)
    self.dataset[y_str][self.index_live] = round(y)


def getPointNameFromIndex(index):
    switcher = {
    0: 'caldera_edgeN',
    1: 'caldera_edgeS',
    2: 'crater_outer_edgeN',
    3: 'crater_outer_edgeS',
    4: 'crater_inner_edgeN',
    5: 'crater_inner_edgeS',
    6: 'crater_topCone_edgeN',
    7: 'crater_topCone_edgeS',
    8: 'crater_bottom_edgeN',
    9: 'crater_bottom_edgeS',
    }
    return switcher.get(index, "nothing")


# Events
def on_key(event, self):
    """ Function that will call the pickSARManagement function when clicking on the amplitude image"""


#     # Re-initialise zoom if escape pressed
    if event.key == 'escape':
        print("Reinitialise zoom")
        self.lim_x = self.lim_x_or
        self.lim_y = self.lim_y_or
        print("roriginal zoom value :", self.lim_x_or, self.lim_y_or)
        print("record zoom value :", self.lim_x, self.lim_y)
        self.updateSARPlot()

              

def onclick(event, self):
    """ Function that will call the pickSARManagement function when clicking on the amplitude image"""
    print("Mouse button is clicked: ", event.button)
    # Check if right clic
    if re.search('MouseButton.RIGHT', str(event.button)):
        # Picking options mest be activated
        if self.pushButton_pick_SAR.isChecked():
            # Mouse must be in a place where coordinate are available
            if event.xdata != None and event.ydata != None:

                # record zoom value if anything pressed
                print("coordinate mouse : ", event.xdata, event.ydata)
                self.lim_x = self.ax.get_xlim()
                self.lim_y = self.ax.get_ylim()
                print("roriginal zoom value :", self.lim_x_or, self.lim_y_or)
                print("record zoom value :", self.lim_x, self.lim_y)
                self.SAR_zoom = True


                # Get points to pick fron inex value
                point_str = getPointNameFromIndex(self.pick_SAR_index)
                pick_point(self, point_str, event.xdata, event.ydata)
                # Update figure
                self.updateSARPlot()
                # update index
                self.pick_SAR_index += 1
                self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 9)
                # Display new point to pick in information label
                self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
                # Make Save button checkable
                self.pushButton_pickSAR_save.setChecked(True)


def onclick_profile(event, self):
    """ Function that will call the pickSARManagement function when clicking on the amplitude image"""
    print("Profile figure is clicked: ", event.button)




            # pickSARManagement(self)



# def pickSARManagement(self):
#     """ Function that will manage each click on the amplitude image if Picking Action activated"""
#     if self.pushButton_pick_SAR.isChecked():
#         print("key tapped , index = ", self.pick_SAR_index)
#         # Display the next points to pick in the label of picking frame panel
#         self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))












            
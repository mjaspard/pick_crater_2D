from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import numpy as np
import os, math, re, time
import datetime as datetime
from osgeo import gdal

def displayTest(self):

    figure = Figure()
    axes = figure.gca()
    axes.set_title("My Plot")
    x = np.linspace(1, 10)
    y = np.linspace(1, 10)
    y1 = np.linspace(11, 20)
    axes.plot(x, y, "-k", label="first one")
    axes.plot(x, y1, "-b", label="second one")
    axes.legend()
    axes.grid(True)
    # Canvas creation
    canvas = FigureCanvas(figure)

    return canvas




def getSARFig(self, dataset, i):
    """ Function to draw SAR image in canvas """

    # File name
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

    



    # Open the file:
    if self.pushButton_filtered_SAR.isChecked():
        file_to_open = filepath_filter
    else:
        file_to_open = filepath
    Raster = gdal.Open(file_to_open)

    print("file_to_open = ",file_to_open)
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

    figure = Figure()
    ax = figure.gca()
    ax.set_title("{}:{}".format(satname, img_date_string))

    if self.pushButton_filtered_SAR.isChecked():    # Need to rescale mi/max between 0 and 1
        vmin = float((self.SAR_clip_min.value()/255))
        vmax = float((self.SAR_clip_max.value()/255))
    else:
        vmin = int(self.SAR_clip_min.value())
        vmax = int(self.SAR_clip_max.value())
    # print("greyscale, vmin, vmax =", expo_greyscale, vmin, vmax)
    if vmin < vmax:
        ax.imshow(inputArray, cmap='Greys_r', vmin=vmin, vmax=vmax)
    else:
        print("Value not coherent to display this image : please check clip value!")


    if self.pushButton_ellipse.isChecked():
        ax.plot(caldera_ellipse_x, caldera_ellipse_y, color='blue', alpha=0.8)
        ax.plot(crater_outer_ellipse_x, crater_outer_ellipse_y, color='skyblue', alpha=0.8)
        ax.plot(crater_inner_ellipse_x, crater_inner_ellipse_y, color='red', alpha=0.8)
        ax.plot(crater_topCone_ellipse_x, crater_topCone_ellipse_y, color='orange', alpha=0.8)
        ax.plot(crater_bottom_ellipse_x, crater_bottom_ellipse_y, color='magenta', alpha=0.8)
        ax.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

        ax.plot(caldera_edgeN_x,caldera_edgeN_y,marker="o", markeredgecolor="blue", markerfacecolor="blue")
        ax.plot(caldera_edgeS_x,caldera_edgeS_y,marker="o", markeredgecolor="blue", markerfacecolor="blue")
        ax.plot(crater_outer_edgeN_x,crater_outer_edgeN_y,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
        ax.plot(crater_outer_edgeS_x,crater_outer_edgeS_y,marker="o", markeredgecolor="skyblue", markerfacecolor="skyblue")
        ax.plot(crater_inner_edgeN_x,crater_inner_edgeN_y,marker="o", markeredgecolor="red", markerfacecolor="red")
        ax.plot(crater_inner_edgeS_x,crater_inner_edgeS_y,marker="o", markeredgecolor="red", markerfacecolor="red")
        ax.plot(crater_topCone_edgeN_x,crater_topCone_edgeN_y,marker="o", markeredgecolor="orange", markerfacecolor="orange")
        ax.plot(crater_topCone_edgeN_x,crater_topCone_edgeS_y,marker="o", markeredgecolor="orange", markerfacecolor="orange")
        ax.plot(crater_bottom_edgeN_x,crater_bottom_edgeN_y,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
        ax.plot(crater_bottom_edgeS_x,crater_bottom_edgeS_y,marker="o", markeredgecolor="magenta", markerfacecolor="magenta")
    


    # self.cid = figure.canvas.mpl_connect('button_press_event', onclick(self))
    figure.canvas.mpl_connect('button_press_event', lambda event: onclick(event, self))

    ax.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

    # Canvas creation
    canvas = FigureCanvas(figure)

    return canvas




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
    print("{} = [{}:{}]".format(info_str, x, y))
    self.images_data[x_str][self.pick_SAR_index] = round(x)
    self.images_data[y_str][self.pick_SAR_index] = round(y)


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
def onclick(event, self):
    """ Function that will call the pickSARManagement function when clicking on the amplitude image"""


    # Picking options mest be activated
    if self.pushButton_pick_SAR.isChecked():
        # Mouse must be in a place where coordinate are available
        if event.xdata != None and event.ydata != None:
            # Get points to pick fron inex value
            point_str = getPointNameFromIndex(self.pick_SAR_index)
            pick_point(self, point_str, event.xdata, event.ydata)
            # update index
            self.pick_SAR_index += 1
            self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 9)
            # Display new point to pick in information label
            self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
            # Make Save button checkable
            self.pushButton_pickSAR_save.setChecked(True)




            # pickSARManagement(self)



# def pickSARManagement(self):
#     """ Function that will manage each click on the amplitude image if Picking Action activated"""
#     if self.pushButton_pick_SAR.isChecked():
#         print("key tapped , index = ", self.pick_SAR_index)
#         # Display the next points to pick in the label of picking frame panel
#         self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))












            
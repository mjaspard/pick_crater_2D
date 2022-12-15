#!/usr/bin/python3
#
#	/usr/bin/python3
# This script is used to display multiples pairs of SAR image (original + filter) sequentially,
#  with the possibility to pick points and record them in a csv file
# 
#	Mandatory:
#		- the name of file must start by 8 digit in date format %Y%m%d
#		- the name of the file must finish by "Crop.r4" 
#		- a filter file must be present with identique name of original ending by "Crop_Filtre.r4"
#
#	1. The script will loop in the image folder and check if each image in the folder is well recorded in csv file
# 			- It will add the image in csv file with empty data
#
#	2. The image will be display on screen:
# 			- Check terminal to know which point to pick
#			- Pick on the map to record coordinate (Follow the terminal)
# 			- press 'p' if you want to skip this point
# 			- press 'n' to go to the next image
#			- press 'q' to quit the script.
#
#	3. New datas are written in the csv file
#-------------------------------------------------------------





import numpy as np
import os as os
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import time
import pandas as pd
import datetime as datetime
import matplotlib.pyplot as plt
import matplotlib as matplotlib
from matplotlib import cm
from matplotlib.patches import Ellipse
from osgeo import gdal
import re
import csv
import sys
import argparse
import datetime
import math

## Manage argument

parser = argparse.ArgumentParser(description='Picker options')

parser.add_argument("csv_file", help="path to csv file", type=str)
parser.add_argument('-C', "--caldera_only", action='store_true', default=False)
parser.add_argument('-c', "--crater_only", action='store_true', default=False)
parser.add_argument('-s', "--shadow_only", action='store_true', default=False)
parser.add_argument('-d', "--date", type=datetime.date.fromisoformat)

args = parser.parse_args()


csv_file = args.csv_file
crater_only = args.crater_only
caldera_only = args.caldera_only
shadow_only = args.shadow_only
target_date = args.date



lim_x_or = ()		# Limite original
lim_y_or = ()
lim_x = ()		# Limite modified
lim_y = ()
reset_zoom = False
reset_zoom_original = False

crater_cone = False
crater_flat = False
crater_tilt = False

global clic_cnt
images_data = {}





#------- Function definition ---------------#
def pick_point(info_str, x, y):
	global i
	global images_data
	x_str = "{}_x".format(info_str)
	y_str = "{}_y".format(info_str)
	print("			{} = [{}:{}]".format(info_str, x, y))
	images_data[x_str][i] = round(x)
	images_data[y_str][i] = round(y)


def pick_semiaxis(info_str, x, y):
	global i
	global images_data
	x_str = "{}_x".format(info_str)
	y_str = "{}_y".format(info_str)
	print("			{} = [{}:{}]".format(info_str, x, y))
	center_x = re.sub(r"semiaxis_.$", "center_x", info_str)
	center_y = re.sub(r"semiaxis_.$", "center_y", info_str)
	if info_str[-1] == 'x':	
		images_data[info_str][i] = abs(int(round(x)) - images_data[center_x][i])
	elif info_str[-1] == 'y':
		images_data[info_str][i] = abs(round(y) - images_data[center_y][i])
	print("			{} = {}".format(info_str, images_data[info_str][i]))
		
	
def on_key(event):
	global clic_cnt
	global check_valid
	global images_data
	global images_data_mem
	global reset_zoom
	global i
	global clic_cnt
	global lim_x
	global lim_y
	global lim_x_or
	global lim_y_or
	global images_number
	global crater_cone
	global crater_flat
	global crater_tilt
	
	global restart_image
	lim_x = ax1.get_xlim()
	lim_y = ax1.get_ylim()	
	if event.key == 'j':
#		print(clic_cnt)
		if clic_cnt == 0:
			clic_cnt += 1	
			print("		Pick caldera_semiaxis_x")
		elif clic_cnt == 1:
			clic_cnt += 1	
			print("		Pick caldera_semiaxis_y")
		elif clic_cnt == 2 and not caldera_only:
			clic_cnt += 1
			print("		Pick crater_center")	
		elif clic_cnt == 3:
			clic_cnt += 1
			print("		Pick crater_semiaxis_x")	
		elif clic_cnt == 4:
			clic_cnt += 1
			print("		Pick crater_semiaxis_y")		
		elif clic_cnt == 5:
			clic_cnt += 1
			print("		Select crater shape: Cone or Flat or Tilt [c/d/t]")	
		elif clic_cnt == 7 and crater_cone:
			clic_cnt += 1
			print("		Pick crater_layover_bottom")	
		elif clic_cnt == 9 and crater_flat:
			clic_cnt += 1
			print("		Pick bottom_crater_semiaxis_x")	
		elif clic_cnt == 10 and crater_flat:
			clic_cnt += 1
			print("		Pick bottom_crater_semiaxis_y")	
		elif clic_cnt == 12 and crater_tilt:
			clic_cnt += 1
			print("		Pick tilt_crater_semiaxis_a")		
		elif clic_cnt == 13 and crater_tilt:
			clic_cnt += 1
			print("		Pick tilt_crater_semiaxis_b")		
		elif (clic_cnt == 14) or ((clic_cnt == 11) and (crater_flat == True)) or ((clic_cnt == 8) and (crater_cone == True)) or ((clic_cnt == 2) and (caldera_only == True)):	
			print("		Thank you!")
			i += -1
			check_valid = True
			plt.close()


	elif event.key == 'y':					# Save change and go to next image
		if check_valid == True:
			df = pd.DataFrame.from_dict(images_data)
			df.to_csv(csv_file, index=False)
			print("		New values has been saved to csv")
			plt.close()
	elif event.key == 'n':					# Do not save change and go to next image
		if check_valid == True:
			images_data = images_data_mem
			print("		Keep old values")
			plt.close()
		else:
			print("{} - {}".format(i, images_number))		
			if i < (images_number - 1):		# go to next image
				plt.close()
	elif event.key == 'm':					# go to 10th next image
		if i < (images_number - 10):
			i += 9
			plt.close()
	elif event.key == 'b':					# go to previous image
		if  i > 0:
			i += -2
			plt.close()
	elif event.key == 'v':					# go to 10th previous image
		print("i = {}".format(i))
		if  i >= 10:
			i += -11
			plt.close()
	elif event.key == 'r':					# Pick again same image
		if check_valid == True:
			i += -1
			restart_image = True
			plt.close()
	elif event.key == 'escape':				# return to original zoom 
		ax1.set_xlim(lim_x_or)
		ax1.set_ylim(lim_y_or)
		ax2.set_xlim(lim_x_or)
		ax2.set_ylim(lim_y_or)
		reset_zoom = True
		i += -1
		plt.close()
	elif event.key == 'c':					# Validation crater shape = cone
		if clic_cnt == 6:
			images_data['bottom_crater_center_x'][i] = 0
			images_data['bottom_crater_center_y'][i] = 0
			images_data['bottom_crater_semiaxis_x'][i] = 0
			images_data['bottom_crater_semiaxis_y'][i]= 0
			images_data['tilt_crater_center_x'][i] = 0
			images_data['tilt_crater_center_y'][i] = 0
			images_data['tilt_crater_semiaxis_a_x'][i] = 0
			images_data['tilt_crater_semiaxis_a_y'][i] = 0
			images_data['tilt_crater_semiaxis_b_x'][i] = 0
			images_data['tilt_crater_semiaxis_b_y'][i] = 0
			clic_cnt += 1
			crater_cone = True
			print("		Pick crater_layover_edge")
	elif event.key == 'd':					# Validation crater shape = flat
		if clic_cnt == 6:
			images_data['tilt_crater_center_x'][i] = 0
			images_data['tilt_crater_center_y'][i] = 0
			images_data['tilt_crater_semiaxis_a_x'][i] = 0
			images_data['tilt_crater_semiaxis_a_y'][i] = 0
			images_data['tilt_crater_semiaxis_b_x'][i] = 0
			images_data['tilt_crater_semiaxis_b_y'][i] = 0
			clic_cnt += 3
			crater_flat = True
			print("		Pick bottom_crater_center")	
	elif event.key == 't':					# Validation crater shape = tilt
		if clic_cnt == 6:                                                            # A AJUSTER ET DEFINIR CFR 133-165
			images_data['bottom_crater_center_x'][i] = 0
			images_data['bottom_crater_center_y'][i] = 0
			images_data['bottom_crater_semiaxis_x'][i] = 0
			images_data['bottom_crater_semiaxis_y'][i]= 0
			images_data['crater_layover_edge_x'][i] = ''
			images_data['crater_layover_edge_y'][i] = ''
			images_data['crater_layover_bottom_x'][i] = ''
			images_data['crater_layover_bottom_y'][i] = ''
			clic_cnt += 6
			crater_tilt = True
			print("		Pick tilt_crater_center")



	elif event.key == 'x':					# Pick points 	
# 		print("x pressed start: i = {}: clic_cnt = {}".format(i, clic_cnt))
		if event.xdata != None and event.ydata != None:
#			print(clic_cnt)
			if clic_cnt == 0:
				pick_point('caldera_center', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick caldera_semiaxis_x")
			elif clic_cnt == 1:
				pick_semiaxis('caldera_semiaxis_x', event.xdata, event.ydata)	
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick caldera_semiaxis_y")
			elif clic_cnt == 2 and not caldera_only:
				pick_semiaxis('caldera_semiaxis_y', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick crater_center")	
			elif clic_cnt == 2 and caldera_only:
				pick_semiaxis('caldera_semiaxis_y', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				check_valid = True	
			elif clic_cnt == 3:
				pick_point('crater_center', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick crater_semiaxis_x")	
			elif clic_cnt == 4:
				pick_semiaxis('crater_semiaxis_x', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick crater_semiaxis_y")		
			elif clic_cnt == 5:
				pick_semiaxis('crater_semiaxis_y', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Select crater shape: Cone or Flat or Tilt [c/d/t]")
			elif (clic_cnt == 7) and crater_cone:
				pick_point('crater_layover_edge', event.xdata, event.ydata)	
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick crater_layover_bottom")		
			elif clic_cnt == 8 and crater_cone:
				pick_point('crater_layover_bottom', event.xdata, event.ydata)	
				i += -1
				check_valid = True
				clic_cnt += 1
				plt.close()	
			elif clic_cnt == 9 and crater_flat:
				pick_point('bottom_crater_center', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick bottom_crater_semiaxis_x")	
			elif clic_cnt == 10 and crater_flat:
				pick_semiaxis('bottom_crater_semiaxis_x', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick bottom_crater_semiaxis_y")		
			elif clic_cnt == 11 and crater_flat:
				pick_semiaxis('bottom_crater_semiaxis_y', event.xdata, event.ydata)
				i += -1
				check_valid = True
				plt.close()
				clic_cnt += 1			
			elif clic_cnt == 12 and crater_tilt:
				pick_point('tilt_crater_center', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick tilt_crater_semiaxis_a")	
			elif clic_cnt == 13 and crater_tilt:
				pick_point('tilt_crater_semiaxis_a', event.xdata, event.ydata)
				i += -1
				plt.close()
				clic_cnt += 1
				print("		Pick tilt_crater_semiaxis_b")		
			elif clic_cnt == 14 and crater_tilt:
				pick_point('tilt_crater_semiaxis_b', event.xdata, event.ydata)
				i += -1
				check_valid = True
				plt.close()
				clic_cnt += 1
# 			else:
# 				i += -1
# 			print("x pressed end: i = {}: clic_cnt = {}".format(i, clic_cnt))
# 		else:
# 			i += -1
# 			print("else i = {}: clic_cnt = {}".format(i, clic_cnt))

	elif event.key == 'q':				# quit
		sys.exit()



def nested_dict_pairs_iterator(dict_obj):
    ''' This function accepts a nested dictionary as argument
        and iterate over all values of nested dictionaries
    '''
    # Iterate over all key-value pairs of dict argument
    for key, value in dict_obj.items():
        # Check if value is of dict type
        if isinstance(value, dict):
            # If value is dict then iterate over all its values
            for pair in  nested_dict_pairs_iterator(value):
                yield (key, *pair)
        else:
            # If value is not dict type then yield the value
            yield (key, value)
 
            
#------------ Original code -------------------------------#

## Choose between displaying figures or saving them to file

# Set to True for display in the notebook
displayFigures = True
# Set to False for plotting in files
#displayFigures = False

#if displayFigures is True:
    ## Display the plots within the notebook
    #matplotlib inline
#else:
#    plt.ioff()

matplotlib.style.use('seaborn-talk')
#matplotlib.style.available


# A priori crater slope
slope_crater = 50.0

# Parameter for curvilinear coordinates of ellipse
t = np.linspace(0, 2*np.pi, 100)

# Ellipse stuff
def ellipse_equation(u, v, a, b, t):
    return np.array([u+a*np.cos(t) , v+b*np.sin(t)])

def ellipse_tilt_equation(u, v, a_x,a_y, b_x,b_y, t,theta):
    a = np.sqrt((a_x-u)**2 + (a_y-v)**2)
    b = np.sqrt((b_x-u)**2 + (b_y-v)**2)
    return np.array([u+a*np.cos(t)*np.cos(theta) - b*np.sin(t)*np.sin(theta) , v+a*np.cos(t)*np.sin(theta)+b*np.sin(t)*np.cos(theta)])

def ellipse_area(a,b):
    return np.pi*a*b



# A priori crater slope
slope_crater = 50.0
#--------------------------------------------------------------#
#---------------- START MAIN ----------------------------------#
#--------------------------------------------------------------#




## Write csv input file data into dictionary 'images_data'



with open(csv_file, 'r') as f:
	images_data = pd.read_csv(f).to_dict()

# print(images_data['folder'])
print("\n------ Let's go ------\n")



print("""Keyboard shortcut on images:\n 
			'j' 	pass this pick point 
			'n' 	next image (without saving current image) 
			'm' 	jump 10 images forward (without saving current image)
			'b' 	previous image (without saving current image) 
			'v' 	jump 10 images backward (without saving current image)
			'esc'	return to original zoom
			'q' 	quit script (without saving current image)


	Matplotlib shortcut: 
				'o'		Zoom-to-rest
				's'		Save
				'p'		Pan/Zoom	
			""")
if caldera_only:
	print("Pick Caldera only")
elif crater_only:
	print("Pick Crater only")


## Loop through dictionary per image and display both image (Crop + filter).
## 		- Select on the images point one by one (information are written in the console)
i = 0
mem_i = -1



check_valid = False
images_data_mem = images_data
images_number = len(images_data['folder'])
once_image_run = False
restart_image = False



## Manage date target and image indice ('i')

if target_date:
	print("\n\nCheck file for image closest to {} as requested".format(target_date))
	all_dates = {}
	choose_dates = []
	while i < images_number:
		date_x = images_data['day'][i]
		date_x = datetime.datetime.strptime(str(date_x), "%Y%m%d")
		if date_x.date() >= target_date:
			delta_x = date_x.date() - target_date
		else:
			delta_x = target_date - date_x.date() 
	# 	delta_x = int(date_x.strftime("%d"))
		all_dates[i] = (delta_x)
		i += 1

	result = sorted(all_dates.items(), key=lambda x: x[1])
	result = result[:5]
	for x in result:
		choose_dates.append(x)


	for j in range(len(choose_dates)):
		k = choose_dates[j][0]
		folder = os.path.basename(images_data['folder'][k])
		print(" {} --> {} ({})".format(j, images_data['day'][k], folder))
		
	user_sel = input("\nPress [0-4] and enter...")
	i = choose_dates[int(user_sel)][0]
else:
	i = 0



#---------------- START LOOP IMAGE DISPLAY ----------------------------------#


while i < images_number:

	# Code for new image display
	if i != mem_i or restart_image:
		print("\nWork on {}/{}".format(images_data['folder'][i], images_data['img_name'][i]))
		if crater_only:
			clic_cnt = 3
			print("		Pick crater_center")
		else:
			clic_cnt = 0	
			print("		Pick caldera_center")
		images_data_mem = images_data
		check_valid = False
		reset_zoom_original = True
		once_image_run = True
		crater_cone = False
		crater_flat = False
		crater_tilt = False
		restart_image = False
	mem_i = i

	# Manage validation
	if check_valid == True:
		print("\n		Do you want to keep these new value or ? [y/n]  or press 'r' to pick again this image")

	#     print("before plot: i = {}: clic_cnt = {}".format(i, clic_cnt))

	# File name
	img_dir = images_data['folder'][i]
	img_name = images_data['img_name'][i]
	filepath = os.path.join(img_dir, img_name)
	filepath_filter = filepath.replace(".r4", "_Filtre.r4")

	# Acquisition time
	img_date_string = images_data['day'][i]
	img_date = datetime.datetime.strptime(str(img_date_string), "%Y%m%d")

	# Pixel size and incidence angle
	azimuth_pixel_size = images_data['azimuth_pixel_size'][i]
	range_pixel_size = images_data['range_pixel_size'][i]
	incidence_angle_deg = images_data['incidence_angle_deg'][i]

	# Caldera ellipse
	caldera_center_x = images_data['caldera_center_x'][i]
	caldera_center_y = images_data['caldera_center_y'][i]
	caldera_semiaxis_x = images_data['caldera_semiaxis_x'][i]
	caldera_semiaxis_y = images_data['caldera_semiaxis_y'][i]

	# Crater ellipse
	crater_center_x = images_data['crater_center_x'][i]
	crater_center_y = images_data['crater_center_y'][i]
	crater_semiaxis_x = images_data['crater_semiaxis_x'][i]
	crater_semiaxis_y = images_data['crater_semiaxis_y'][i]

	# Bottom_Crater ellipse
	bottom_crater_center_x = images_data['bottom_crater_center_x'][i]
	bottom_crater_center_y = images_data['bottom_crater_center_y'][i]
	bottom_crater_semiaxis_x = images_data['bottom_crater_semiaxis_x'][i]
	bottom_crater_semiaxis_y = images_data['bottom_crater_semiaxis_y'][i]

	# Crater layover
	crater_layover_edge_x = images_data['crater_layover_edge_x'][i]
	crater_layover_edge_y = images_data['crater_layover_edge_y'][i]
	crater_layover_bottom_x = images_data['crater_layover_bottom_x'][i]
	crater_layover_bottom_y = images_data['crater_layover_bottom_y'][i]
	
	# Crater tilt
	tilt_crater_center_x = images_data['tilt_crater_center_x'][i]
	tilt_crater_center_y = images_data['tilt_crater_center_y'][i]
	tilt_crater_semiaxis_a_x = images_data['tilt_crater_semiaxis_a_x'][i]
	tilt_crater_semiaxis_a_y = images_data['tilt_crater_semiaxis_a_y'][i]
	tilt_crater_semiaxis_b_x = images_data['tilt_crater_semiaxis_b_x'][i]
	tilt_crater_semiaxis_b_y = images_data['tilt_crater_semiaxis_b_y'][i]
	# Grayscale exponent
	expo_greyscale = images_data['expo_greyscale'][i] 
	# Open the file:
	Raster = gdal.Open(filepath)
	#expo_greyscale = 0.3

	Band   = Raster.GetRasterBand(1) # 1 based, for this example only the first
	NoData = Band.GetNoDataValue()  # this might be important later

	nBands = Raster.RasterCount      # how many bands, to help you loop
	nRows  = Raster.RasterYSize      # how many rows
	nCols  = Raster.RasterXSize      # how many columns
	dType  = Band.DataType          # the datatype for this band


	# Check type of the variable 'raster'
	#print(type(Raster))

	# Extract band
	inputArray = (np.array(Band.ReadAsArray()**expo_greyscale))


	# Cleanup
	del Raster, Band

	# Open the filter file:
	Raster_f = gdal.Open(filepath_filter)
	expo_greyscale = 0.3

	Band_f = Raster_f.GetRasterBand(1) # 1 based, for this example only the first
	NoData = Band_f.GetNoDataValue()  # this might be important later

	nBands = Raster_f.RasterCount      # how many bands, to help you loop
	nRows  = Raster_f.RasterYSize      # how many rows
	nCols  = Raster_f.RasterXSize      # how many columns
	dType  = Band_f.DataType 

	inputArray_f = (np.array(Band_f.ReadAsArray()**expo_greyscale))

	 # Cleanup
	del Raster_f, Band_f
	
	
	# Angle
	
	theta_deg = 360 - math.atan2(tilt_crater_semiaxis_a_y - tilt_crater_center_y  , tilt_crater_semiaxis_a_x -tilt_crater_center_x ) * 180 / math.pi 
	theta = math.atan2(tilt_crater_semiaxis_a_y - tilt_crater_center_y  , tilt_crater_semiaxis_a_x -tilt_crater_center_x )

	# Ellipses
	[caldera_ellipse_x, caldera_ellipse_y] = ellipse_equation(caldera_center_x, caldera_center_y, caldera_semiaxis_x, caldera_semiaxis_y, t)
	[crater_ellipse_x, crater_ellipse_y] = ellipse_equation(crater_center_x, crater_center_y, crater_semiaxis_x, crater_semiaxis_y, t)
	[bottom_crater_ellipse_x, bottom_crater_ellipse_y] = ellipse_equation(bottom_crater_center_x, bottom_crater_center_y, bottom_crater_semiaxis_x, bottom_crater_semiaxis_y, t)
	[tilt_crater_ellipse_x, tilt_crater_ellipse_y] = ellipse_tilt_equation(tilt_crater_center_x, tilt_crater_center_y, tilt_crater_semiaxis_a_x, tilt_crater_semiaxis_a_y, tilt_crater_semiaxis_b_x, tilt_crater_semiaxis_b_y, t,theta)


	# Estimate of crater size
	caldera_area = ellipse_area(caldera_semiaxis_x, caldera_semiaxis_y)
	crater_area = ellipse_area(crater_semiaxis_x, crater_semiaxis_y)
	crater_relative_area = crater_area/caldera_area
	crater_relative_elongation_y = crater_semiaxis_y / caldera_semiaxis_y
	#     print(" 	Caldera area = %f" % caldera_area)
	#     print(" 	Crater area = %f" % crater_area)
	#     print(" 	Caldera relative area = %f" % crater_relative_area)
	#     print(" 	Caldera relative elongation in azimuth = %f" % crater_relative_elongation_y)

	# Estimate of crater depth (method 1 : crater center)
# 	if crater_cone == True:
# 		crater_delta_range_pix = np.abs(crater_layover_bottom_x - crater_center_x)
# 		crater_delta_range_meters = crater_delta_range_pix * range_pixel_size
# 		crater_delta_vertical_meters = crater_delta_range_meters * np.cos(np.deg2rad(incidence_angle_deg))
	#     	print(" 	Crater slant-range depth from cent# er of crater = %f m" % crater_delta_range_meters)
	#     	print(" 	Crater vertical depth from center of crater = %f m" % crater_delta_vertical_meters)

	# Estimate of crater depth (method 2 : crater edge)
# 		crater_delta_range_pix = np.abs(crater_layover_bottom_x-crater_layover_edge_x)
# 		crater_delta_range_meters = crater_delta_range_pix * range_pixel_size
# 		crater_delta_vertical_meters = crater_delta_range_meters * np.cos(np.deg2rad(incidence_angle_deg))
	#     	print(" 	Crater slant-range depth from edge of crater = %f m" % crater_delta_range_meters)
	#     	print(" 	Crater vertical depth from edge of crater = %f m" % crater_delta_vertical_meters)

	#     	print(img_date_string, crater_relative_elongation_y) 
   
	# Show everything together
	fig, [ax1, ax2] = plt.subplots(1,2, sharex=True, sharey=True, figsize=(20,9))

	ax1.set_title(filepath)
	implot = ax1.imshow(inputArray, cmap='Greys_r')
	ax1.plot(caldera_ellipse_x, caldera_ellipse_y, color='blue', alpha=0.1)
	ax1.plot(caldera_center_x, caldera_center_y, 'o', markerfacecolor='blue', alpha=0.3)
	ax1.plot(crater_ellipse_x, crater_ellipse_y, color='red', alpha=0.1)
	ax1.plot(crater_center_x, crater_center_y, 'o', markerfacecolor='red', alpha=0.3)
	ax1.plot(crater_layover_edge_x, crater_layover_edge_y, 'o', markerfacecolor='orange', alpha=0.3)
	ax1.plot(crater_layover_bottom_x, crater_layover_bottom_y, 'o', markerfacecolor='green', alpha=0.3)
	ax1.plot(bottom_crater_ellipse_x, bottom_crater_ellipse_y, color='magenta', alpha=0.1)
	ax1.plot(bottom_crater_center_x, bottom_crater_center_y, 'o', markerfacecolor='magenta', alpha=0.3)
	ax1.plot(tilt_crater_ellipse_x, tilt_crater_ellipse_y, color='cyan', alpha=0.1)
	ax1.plot(tilt_crater_center_x, tilt_crater_center_y, 'o', markerfacecolor='cyan', alpha=0.3)
	ax1.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)

	ax2.set_title("{} - Filtered".format(img_date_string))
	ax2.imshow(inputArray_f, cmap='Greys_r')
	ax2.plot(caldera_ellipse_x, caldera_ellipse_y, color='blue', alpha=0.5)
	ax2.plot(caldera_center_x, caldera_center_y, 'o', markerfacecolor='blue', alpha=0.8)
	ax2.plot(crater_ellipse_x, crater_ellipse_y, color='red', alpha=0.5)
	ax2.plot(crater_center_x, crater_center_y, 'o', markerfacecolor='red', alpha=0.8)
	ax2.plot(crater_layover_edge_x, crater_layover_edge_y, 'o', markerfacecolor='orange', alpha=0.8)
	ax2.plot(crater_layover_bottom_x, crater_layover_bottom_y, 'o', markerfacecolor='green', alpha=0.8)
	ax2.plot(bottom_crater_ellipse_x, bottom_crater_ellipse_y, color='magenta', alpha=0.8)
	ax2.plot(bottom_crater_center_x, bottom_crater_center_y, 'o', markerfacecolor='magenta', alpha=0.5)
	ax2.plot(tilt_crater_ellipse_x, tilt_crater_ellipse_y, color='cyan', alpha=0.5)
	ax2.plot(tilt_crater_center_x, tilt_crater_center_y, 'o', markerfacecolor='cyan', alpha=0.8)
	ax2.set_aspect(abs(np.sin(np.deg2rad(incidence_angle_deg))) * azimuth_pixel_size/range_pixel_size)
	# Manage click on image


	#     cid = fig.canvas.mpl_connect('button_press_event', onclick)
	cid = fig.canvas.mpl_connect('key_press_event', on_key)


	# Keep zoom memorisation on image
	if not once_image_run and not reset_zoom:
		ax1.set_xlim(lim_x)
		ax1.set_ylim(lim_y)
		ax2.set_xlim(lim_x)
		ax2.set_ylim(lim_y)

	# Reset zoom om image
	if reset_zoom:
		ax1.set_xlim(lim_x_or)
		ax1.set_ylim(lim_y_or)
		ax2.set_xlim(lim_x_or)
		ax2.set_ylim(lim_y_or)
		reset_zoom = False

	# record otriginal zoom (juste once per image)
	if reset_zoom_original == True:
		lim_x_or = ax1.get_xlim()
		lim_y_or = ax1.get_ylim()
		reset_zoom_original = False


	once_image_run = False


	#     print("lim_x_or = {}".format(lim_x))
	#     print("lim_y_or = {}".format(lim_y))   
	#     print("lim_x = {}".format(lim_x))
	#     print("lim_y = {}".format(lim_y))
	#     print("current_x = {} ".format(ax1.get_xlim()))
	#     print("current_y = {} ".format(ax1.get_ylim()))
	
	#     if reset_zoom:
	#     	reset_zoom = False

	plt.show()
	i += 1
	#     plt.clf() 

## Write the dictionary with all new data to csv output file


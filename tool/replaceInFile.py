#!/usr/bin/python3
#
#
#-------------------------------------------------------------




import sys
import re
import csv

## Manage argument


csv_file = sys.argv[1]

print(csv_file)






update_file = csv_file.replace(".csv", "_updated.csv")


new_lines = []
with open(csv_file, 'r') as infile:
	for line in infile:
		line = line.replace('/home/delphine/Documents/Nyir2021/CraterDepth/Process/', '/Users/maxime/Project/Pick_Crater/pick_crater_3/DATA_SAR_AMPLI_NYIR21_FOR_PICKING/Data/')
		x = line.split(',')
		y = ','.join(x[0:28])
		new_lines.append(y)


with open(update_file, 'w') as outfile:
    for line in new_lines:
        outfile.write("{}\n".format(line))
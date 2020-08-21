#!/usr/bin/env python3

# THIS CAN BE USED TO ANALYZE AND GRAPH PLANT INFORMATION (LIKE AREA) OVER A SINGLE DAY

import plantcv as pcv
import json
import matplotlib.pyplot as plt
import csv
import numpy as np
import os
import argparse

def options():
    parser = argparse.ArgumentParser(description='Graph plant information over a single day')
    parser.add_argument('-d', '--directory', help='Path to source directory', required=True)
    parser.add_argument('-o', '--outFile', help='Output file', default='areaVsTime.png', required=False)
    parser.add_argument('-t', '--date', help='Date data was collected', required=True)
    args = parser.parse_args()
    return args

def main():
    # Get arguments
    args = options()
    folder = args.directory

    areas = np.array([])
    times = np.array([])

    # Loop through result files in given folder
    for file in sorted(os.listdir(folder)):
        if file != '.ipynb_checkpoints' and file != '.DS_Store':
            text_data = open('{a}/{b}'.format(a=folder,b=file))
            data_dict = json.load(text_data)
            area = data_dict['observations']['area']['value']
            areas = np.append(areas, area)
            fileTime = file.split('_')
            fileTime = fileTime[2]
            filetime = fileTime.split(':')
            filetime = '{h}.{m}'.format(h=filetime[0],m=int(filetime[1])*100//60)
            filetime = float(filetime)
            times = np.append(times, filetime)

    # plot the areas vs time
    x = times
    y = areas
    plt.title('Area VS Time of Day ' + args.date)
    plt.scatter(x,areas,color='blue')
    plt.xlabel('Hour of Day')
    plt.ylabel('Area of plant [Pixels]')
    plt.savefig(args.outFile)

# THE FOLLOWING IS AN OPTIONAL WAY TO FILTER OUTLIER DATA THAT STRAYS A CERTAIN AMOUNT FROM THE MEAN OF THE DAY:

def removeOutliers(areas,times):
    mean = np.mean(areas)
    print(mean)
    for i in range(len(areas)-1,0,-1):
        if (areas[i]/mean > 1.2) or (areas[i]/mean < 0.8):
            areasFiltered = np.delete(areas, i)
            timesFiltered = np.delete(times, i)
            print(i, times[i])
            areas = areasFiltered
            times = timesFiltered
    return areas, times
    areasFiltered, timesFiltered = removeOutliers(areas, times)

    # plot the areas vs time
    x = timesFiltered
    y = areasFiltered

    plt.title('Area (Filtered) VS Time of Day ' + args.date)
    plt.scatter(x,y,color='green')
    plt.xlabel('Hour of Day')
    plt.ylabel('Area of plant [Pixels]')
    plt.savefig(args.outFile + '_filtered')

if __name__ == '__main__':
    main()

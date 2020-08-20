#!/usr/bin/env python3

# THIS CAN BE USED TO ANALYZE & GRAPH MANY DIFFERENT FACTORS SUCH AS AREA OF PLANT AND CSV SENSOR DATA

import plantcv as pcv
import json
import matplotlib.pyplot as plt
import csv
import numpy as np
import os
import argparse

def options():
    parser = argparse.ArgumentParser(description='Analyze and graph data')
    parser.add_argument('-d', '--directory', help='Path to input directory', required=True)
    parser.add_argument('-c', '--csvFile', help='Temperature and humidity CSV file', required=True)
    parser.add_argument('-t', '--date', help='Date data was taken (YYYY-MM-DD)', required=True)
    parser.add_argument('-o', '--outFile', help='File to output results to', default='Temp&Height.png', required=False)
    args = parser.parse_args()
    return args

def main():
    # Get arguments
    args = options()

    areas, heights, widths, times = readData(args.directory)
    temps, hum, times2 = tempHumData(args.csvFile, args.date)
    plotData(times, times2, areas, heights, widths, temps, args.outFile, args.date)

def readData(folder):
    areas = np.array([])
    heights = np.array([])
    widths = np.array([])
    times = np.array([])

    for file in sorted(os.listdir(folder)):
        if file != '.ipynb_checkpoints' and file != '.DS_Store':
            text_data = open('{a}/{b}'.format(a=folder,b=file))
            data_dict = json.load(text_data)
            area = data_dict['observations']['area']['value']
            height = data_dict['observations']['height']['value']
            width = data_dict['observations']['width']['value']
            fileTime = file.split('_')
            fileTime = fileTime[2]
            filetime = fileTime.split(':')
            ############################################## CHANGE THE FOLLOWING BEFORE RUNNING:
            if (5>int(filetime[0])>=0) or (24>=int(filetime[0])>=22):
                filetimeB = filetime
                ############################################## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                filetimeB = '{h}.{m}'.format(h=int(filetimeB[0]),m=int(filetimeB[1])*100//60)
                filetimeB = float(filetimeB)
                if filetimeB > 6:
                    filetimeB = filetimeB -22
                else:
                    filetimeB = filetimeB + 2
                times = np.append(times, filetimeB)
                areas = np.append(areas, area)
                heights = np.append(heights, height)
                widths = np.append(widths, width)
    return areas, heights, widths, times

def tempHumData(csvfile, date):
    temps = np.array([])
    hum = np.array([])
    times2 = np.array([])
    count = 0
    with open(csvfile, 'r') as fd:
        for row in fd:
            row = row.split(',')
            count +=1   
            timesplit = row[3].split(':')
            # CHANGE THE FOLLOWING:
            if (row[2]==date and 5>int(timesplit[0])>=0) or (row[2]=='2020-07-31' and 24>=int(timesplit[0])>=22):
            # ^^^^^^^^^^^^^^^^^^^^
                temps = np.append(temps, float(row[0]))
                hum = np.append(hum, float(row[1]))
                timedata = row[3][0:8]
                timedata = timedata.split(':')
                timedata = float('{h}.{m}'.format(h=int(timedata[0]), m=int(timedata[1])*100//60))
#               timedata = timedata/100
                if timedata > 6:
                    timedata = timedata -22
                else:
                    timedata = timedata + 2
                times2 = np.append(times2, timedata)
    return temps, hum, times2

def plotData(times, times2, areas, heights, widths, temps, outFile, date):
    # plot the areas vs time
    x = times
    x2 = times2
    y = areas
    z = heights
    w = widths
    q = temps

    # make a graph with the first y axis
    fig1, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('Hours Past 22:00 (' + date + ')')
    ax1.set_ylabel('Temperature (C)', color=color)
    ax1.scatter(x2, q, color=color, s=20)   # the s paramter determines marker size
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_title(' Height vs Time')
    ax1.locator_params(axis='x', nbins=5)

    # Add the 2nd y axis
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Height (Pixels)', color=color)
    ax2.scatter(x, z, color=color, s=20)
    ax2.tick_params(axis='y', labelcolor=color)
    #ax2.set_ylim(0,300)
    plt.show()
    fig1.savefig(outFile) 

if __name__ == '__main__':
    main()

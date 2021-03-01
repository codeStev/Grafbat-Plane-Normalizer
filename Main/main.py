# -*- coding: UTF-8 -*-
# Python program to create
# a file explorer in Tkinter
# import all components
# from the tkinter library
import functools
import os
from datetime import datetime
from tkinter import *
# import filedialog module
from tkinter import filedialog

# Function for opening the
# file explorer window
umlaute = {"ö": 148}
file = None
priolist = ['5296', '510', '511', '251', '481', '484', '1209', '253']


def browseFiles():
    global file
    filename = None
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Datei auswaehlen",
                                          filetypes=(("Dateien",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))

    # Change label contents
    if filename is not None:
        file = open(filename, encoding='cp1252')
        label_file_explorer.configure(text="Datei: " + filename)
    else:
        label_file_explorer.configure(text="Keine Datei ausgewaehlt")


def processFile():
    startTime = datetime.now()
    print(startTime)
    if file is not None:
        others = [""]
        lines = []
        pointLines = []
        texts = []
        othercounter = 0
        for line in file:
            if line.startswith('LI', 0, 2):

                lines.append(line)
            elif line.startswith('PK', 0, 2):
                pointLines.append(line)
            elif line.startswith('TE', 0, 2):
                if len(texts) == 0:
                    othercounter += 1
                texts.append(line)
            elif line.startswith('TX', 2, 4):
                texts[len(texts) - 1] += line
            elif line.startswith('TR', 2, 4):
                texts[len(texts) - 1] += line
            elif line.startswith('TT', 2, 4):
                texts[len(texts) - 1] += line
            else:
                # print(othercounter)
                if len(others) - 1 < othercounter:
                    others.append(line)
                else:
                    others[othercounter] += line
        lines = sorted(lines, key=functools.cmp_to_key(line_cmp_prio), reverse=True)
        seenPoints = []
        pointDict = {}
        textPointDic = {}
        textLineDic = {}
        for pointLine in pointLines:
            # print(get_PointId_from_PointLine(point))
            pointId = get_Id_from_line(pointLine)
            pointDict[pointId] = pointLine
        for textLine in texts:
            pointKey = get_PointId_from_TextLine(textLine)
            pointLine = get_PointId_from_TextLine(textLine)
            if pointKey is not None:
                textPointDic[pointKey] = textLine
            elif pointLine is not None:
                textLineDic[pointLine] = textLine
        for line in lines:
            lineId = get_Id_from_line(line)
            plane = get_plane(line)
            # print(line+ "....."+plane)
            if textLineDic.get(lineId) is not None:
                textLineDic[lineId] = set_plane(textLineDic.get(lineId, plane))
            pointList = get_points(line)
            for point in pointList:

                if point not in seenPoints:
                    pointDict[point] = set_plane(pointDict.get(point), plane)
                    if textPointDic.get(point) is not None:
                        textPointDic[point] = set_plane(textPointDic.get(point), plane)
                    seenPoints.append(point)

        # merge changes
        # sorted(lines, key=functools.cmp_to_key(line_cmp), reverse=True)
        stringPoints = sorted({str(value) for key, value in pointDict.items()}, key=functools.cmp_to_key(line_cmp_id))
        stringPoints = ''.join(stringPoints)
        lines = ''.join(sorted(lines, key=functools.cmp_to_key(line_cmp_id)))
        stringTextPoints = sorted({str(value) for key, value in textPointDic.items()},
                                  key=functools.cmp_to_key(line_cmp_id))
        stringTextPoints = ''.join(stringTextPoints)
        stringTextLines = sorted({str(value) for key, value in textLineDic.items()},
                                 key=functools.cmp_to_key(line_cmp_id))
        stringTextLines = ''.join(stringTextLines)

        newFileText = others[0] + stringPoints + lines + stringTextPoints + stringTextLines + others[1]
        print(len(others))
        # print(newFileText)
        f = open(os.path.basename(file.name).split('.')[0] + "_new.out", 'w', encoding='cp1252')
        f.write(newFileText)
        endTime = datetime.now()
        print(endTime)
        print(endTime - startTime)
        # for key,value in pointDict.items():
        #    print(value)
        # for key,value in textLineDic.items():
        #     print(value)
        # for key,value in textPointDic.items():
        #     print(value)
    #  print(len(others))
    #  print(others)
    # for line in lines:
    #  print(line)
    # print(points)
    # for text in texts:
    #  print(text)


def line_cmp_prio(a, b):
    global priolist
    a_cut = get_prio(a)
    b_cut = get_prio(b)
    if priolist.index(a_cut) < priolist.index(b_cut):
        return 1
    else:
        return -1


def line_cmp_id(a, b):
    a = int(get_Id_from_line(a))
    b = int(get_Id_from_line(b))
    if a > b:
        return 1

    else:
        return -1


def get_points(line):
    points = []
    temp = line.split(':')
    temp = temp[1].split(',')
    points.append(temp[0].split('=')[1])
    points.append(temp[1].split('=')[1])
    return points


# Create the root window
window = Tk()


def get_prio(line):
    return line.split(',')[2].split('.')[1]


def get_plane(line):
    return line.split(',')[2].split('.')[0]


def get_Id_from_line(line):
    temp = line.split(':')[0]
    pointId = temp[2:]
    # print(pointId)
    return pointId


def get_PointId_from_TextLine(line):
    temp = re.findall("PK=[0-9]+", line)
    if len(temp) < 1:
        return None
    return re.sub('PK=', '', temp[0])


def get_LineId_from_TextLine(line):
    temp = re.findall("LI=[0-9]+", line)
    if len(temp) < 1:
        return None
    return re.sub('LI=', '', temp[0])


def set_plane(line, plane):
    # temp = line.split(':')[1].split(',')[1].split('.')
    # temp[0]= plane
    # temp2 = line.split(',')
    # temp2[1]= temp[0]+'.'+temp[1]
    # temp2 = ','.join(temp)
    # print(temp)
    # return temp2
    return re.sub(',[0-9]+', ',' + plane, line, 1)


# Set window title
window.title('Umsetzer')

# Set window size
window.geometry("500x500")

# Set window background color
window.config(background="white")

# Create a File Explorer label
label_file_explorer = Label(window,
                            text="Dateiauswahl",
                            width=100, height=4,
                            fg="blue")

button_explore = Button(window,
                        text="Durchsuchen",
                        command=browseFiles)
button_format = Button(window,
                       text="umsetzen",
                       command=processFile)

# Grid method is chosen for placing
# the widgets at respective positions
# in a table like structure by
# specifying rows and columns
label_file_explorer.grid(column=1, row=1)

button_explore.grid(column=1, row=2)
button_format.grid(column=1, row=3)

# Let the window wait for any events
window.mainloop()

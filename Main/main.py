# -*- coding: UTF-8 -*-
import functools
import os
from datetime import datetime
from tkinter import *
from tkinter import filedialog


# Function for opening the
# file explorer window
def readPrioConfig():
    global priolist
    prioFile = open("prioKonfiguration.txt")
    if prioFile is None:
        label_file_explorer.configure(text="Keine Datei ausgewaehlt")
        raise FileNotFoundError("Die Datei prioKonfiguration.txt konnte nicht gefunden werden.")
    for line in prioFile:
        if line.strip():
            priolist.append(line.strip())


file = None
priolist = []
readPrioConfig()
print(priolist)


def browseFiles():
    global file
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
        pointBonus = {}
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
            elif line.strip().startswith('TX', 0, 2):
                texts[len(texts) - 1] += line
            elif line.strip().startswith('TR', 0, 2):
                texts[len(texts) - 1] += line
            elif line.strip().startswith('TT', 0, 2):
                texts[len(texts) - 1] += line
            elif line.strip().startswith('F', 0, 1):
                pointId = get_Id_from_line(pointLines[len(pointLines) - 1])
                if pointBonus.get(pointId) is not None:
                    pointBonus[pointId] = pointBonus[pointId] + line
                else:
                    pointBonus[pointId] = line
            else:
                if len(others) - 1 < othercounter:
                    others.append(line)
                else:
                    others[othercounter] += line
        lines = sorted(lines, key=functools.cmp_to_key(line_cmp_prio), reverse=True)
        seenPoints = []
        pointDict = {}
        textPointDic = {}
        textBonusDic = {}
        textLineDic = {}
        textFloatDic = []
        for pointLine in pointLines:
            pointId = get_Id_from_line(pointLine)
            pointDict[pointId] = pointLine
        for textLine in texts:
            pointKey = get_PointId_from_TextLine(textLine)
            pointLine = get_PointId_from_TextLine(textLine)
            if pointKey is not None:
                textPointDic[pointKey] = textLine
            elif pointLine is not None:
                textLineDic[pointLine] = textLine
            else:
                textFloatDic.append(textLine)
        for line in lines:
            lineId = get_Id_from_line(line)
            plane = get_plane(line)
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
        stringPoints = sorted({str(value) for key, value in pointDict.items()}, key=functools.cmp_to_key(line_cmp_id))
        for i in range(0, len(stringPoints) - 1):
            if pointBonus.get(get_Id_from_line(stringPoints[i])) is not None:
                stringPoints[i] = stringPoints[i] + pointBonus.get(get_Id_from_line(stringPoints[i]))
        stringPoints = ''.join(stringPoints)
        lines = ''.join(sorted(lines, key=functools.cmp_to_key(line_cmp_id)))
        listTexts = sorted(
            {str(value) for value in (list(textLineDic.values()) + list(textPointDic.values()) + list(textFloatDic))},
            key=functools.cmp_to_key(line_cmp_id))

        stringTexts = ''.join(listTexts)
        newFileText = others[0] + stringPoints + lines + stringTexts + others[1]
        print(len(others))
        f = open(os.path.basename(file.name).split('.')[0] + "_new.out", 'w', encoding='cp1252')
        f.write(newFileText)
        endTime = datetime.now()
        print(endTime)
        print(endTime - startTime)
        label_file_explorer.configure(text="Fertig")


def line_cmp_prio(a, b):
    global priolist
    a_cut = get_prio(a)
    b_cut = get_prio(b)
    if a_cut not in priolist or b_cut not in priolist:
        return 1
    elif priolist.index(a_cut) < priolist.index(b_cut):
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


def appendLine(toAppend):
    return lambda f: f + toAppend


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

label_file_explorer.grid(column=1, row=1)
button_explore.grid(column=1, row=2)
button_format.grid(column=1, row=3)

# Let the window wait for any events
window.mainloop()

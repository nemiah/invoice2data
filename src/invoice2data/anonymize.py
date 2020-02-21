# -*- coding: utf-8 -*-
#import cv2
from xml.dom import minidom
import subprocess
from distutils import spawn
import json

def anonymize(path, dictionary):
    if not spawn.find_executable("qpdf"):
        raise EnvironmentError("qpdf not installed.")
        
    dictionary = json.loads(dictionary);
    
    #qpdf --stream-data=uncompress your.pdf compressed.pdf
    qpdf = [
        "qpdf",
        "--stream-data=uncompress",
        path,
        "-"
    ]

    p0 = subprocess.Popen(qpdf, stdout=subprocess.PIPE)
    out, err = p0.communicate()
    #print(phrases)

    if "zip" in dictionary and "city" in dictionary and dictionary["zip"] and dictionary["city"]:
        phrase = dictionary["zip"]+" "+dictionary["city"]
        out = out.replace(phrase.encode('ISO-8859-1') , "-".ljust(len(phrase), "-"))
        
    if "company" in dictionary and dictionary["company"]:
        phrase = "Firma "+dictionary["company"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
        phrase = dictionary["company"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
    if "firstname" in dictionary and "lastname" in dictionary and dictionary["firstname"] and dictionary["lastname"]:
        phrase = "Frau "+dictionary["firstname"]+" "+dictionary["lastname"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
        phrase = "Herr "+dictionary["firstname"]+" "+dictionary["lastname"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
        phrase = dictionary["firstname"]+" "+dictionary["lastname"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
    if "lastname" in dictionary and dictionary["lastname"]:
        phrase = "Herr "+dictionary["lastname"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
        phrase = "Frau "+dictionary["lastname"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
    if "street" in dictionary and "number" in dictionary and dictionary["street"] and dictionary["number"]:
        phrase = dictionary["street"]+" "+dictionary["number"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        
        phrase = dictionary["street"].replace(u"straße", u"str.")+" "+dictionary["number"]
        out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))

    if "additional" in dictionary and dictionary["additional"]:
        if isinstance(dictionary["additional"], list):
            for phrase in dictionary["additional"]:
                out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))
        else:
            phrase = dictionary["additional"]
            out = out.replace(phrase.encode('ISO-8859-1'), "-".ljust(len(phrase), "-"))

            
    """
    for phrase in phrases:
        out = out.replace(phrase, " ".ljust(len(phrase)));
        
        try:
            out = out.replace(phrase.decode("utf8").encode('ISO-8859-15'), " ".ljust(len(phrase)));
        except UnicodeDecodeError as (strerror):
            print(strerror)
            print("Error: {} can't be decoded".format(phrase))
    """
    
    with open(path, "w") as text_file:
        text_file.write(out)

        
"""
xmldoc = minidom.parse('/home/nemiah/NetBeansProjects/test/hocr/Lechner.hocr')
image = cv2.imread('/home/nemiah/NetBeansProjects/test/hocr/SCN1507122258199.png')

anonymize = [

]

body = xmldoc.getElementsByTagName('body')
for item in body[0].childNodes[1].childNodes:
    if item.nodeName != "div":
        continue

    for ps in item.childNodes:
        if ps.nodeName != "p":
            continue

        
        for spans in ps.childNodes:
            if spans.nodeName != "span":
                continue
                
            #coord = spans.attributes["title"].value.replace(";", "").split(" ")
            #cv2.rectangle(image, (int(coord[1]), int(coord[2])), (int(coord[3]), int(coord[4])), (255, 0, 0), 1)

            redactLineCells = []
            redactLine = None
            for subspans in spans.childNodes:
                if subspans.nodeName != "span":
                    continue
                    
                #for text in subspans.childNodes[0]:
                text = subspans.childNodes[0].nodeValue

                redact = False
                if redactLine == None:
                    for line in anonymize:
                        sesso = line.split(" ");
                        if text == sesso[0]:
                            redact = True
                            redactLine = sesso;
                            redactLine.pop(0)

                else:
                    if len(redactLine):
                        redact = True
                        word = redactLine.pop(0)
				    
                    else:
                        redactLine = None
			    
                if redact:
                    coord = subspans.attributes["title"].value.replace(";", "").split(" ")
                    redactLineCells.append([int(coord[1]), int(coord[2]), int(coord[3]), int(coord[4])])
                    

            if len(redactLineCells):
                minY1 = redactLineCells[0][1]
                maxY2 = redactLineCells[0][3]
                for cell in redactLineCells:
                    #print(cell)
                    if cell[1] < minY1:
                        minY1 = cell[1]
                        
                    if cell[3] > maxY2:
                        maxY2 = cell[3]
                        
                for cell in redactLineCells:
                    cv2.rectangle(image, (cell[0], minY1), (cell[2], maxY2), (0, 0, 0), -1)
                    #for cell in line:
                    #    print(cell)
                    
cv2.imwrite("output.png", image)
"""









# -*- coding: utf-8 -*-
import re

def to_text(path, language):
    """Wraps Tesseract OCR.

    Parameters
    ----------
    path : str
        path of electronic invoice in JPG or PNG format

    Returns
    -------
    extracted_str : str
        returns extracted text from image in JPG or PNG format

    """
    import subprocess
    from distutils import spawn
    
    # Check for dependencies. Needs Tesseract and Imagemagick installed.
    if not spawn.find_executable("tesseract"):
        raise EnvironmentError("tesseract not installed.")
    if not spawn.find_executable("convert"):
        raise EnvironmentError("imagemagick not installed.")
    if not spawn.find_executable("pdfinfo"):
        raise EnvironmentError("pdfinfo not installed.")

    pdfinfo = [
        "pdfinfo",
        path
    ]

    p0 = subprocess.Popen(pdfinfo, stdout=subprocess.PIPE)
    out, err = p0.communicate()
    
    """
    Producer:       iText® 5.3.5 ©2000-2012 1T3XT BVBA (Canon Inc.; licensed version)
    CreationDate:   Mon Dec  3 10:21:55 2018 CET
    ModDate:        Mon Dec  3 10:21:55 2018 CET
    Tagged:         no
    UserProperties: no
    Suspects:       no
    Form:           none
    JavaScript:     no
    Pages:          2
    Encrypted:      no
    Page size:      595 x 842 pts (A4)
    Page rot:       0
    File size:      1926343 bytes
    Optimized:      no
    PDF version:    1.4
    """
    
    result = re.findall(r"Pages:\s+(\d+)", out)
    pages = int(result[0])
   
    extracted_str = ""
    for page in range(0, pages):
        convert = [
            "convert",
            "-density",
            "350",
            path+"["+str(page)+"]",
            "-colorspace",
            "Gray",
            "-contrast-stretch",
            "0",
            "-sharpen",
            "0x1",
            "-depth",
            "8",
            "-background",
            "white",
            "-flatten",
            "-type",
            "grayscale",
            "-alpha",
            "off",
            "png:-",
        ]
        p1 = subprocess.Popen(convert, stdout=subprocess.PIPE)

        tess = ["tesseract", "stdin", "stdout", "-l", language, "--dpi", "350"]
        p2 = subprocess.Popen(tess, stdin=p1.stdout, stdout=subprocess.PIPE)

        out, err = p2.communicate()

        extracted_str += out

    return extracted_str

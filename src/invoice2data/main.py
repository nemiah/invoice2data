#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shutil
import os
from os.path import join
import logging

from input import pdftotext
from input import pdfminer_wrapper
from input import tesseract
from input import tesseract4
from input import gvision

from extract.loader import read_templates

from output import to_csv
from output import to_json
from output import to_xml
from output import to_xml


logger = logging.getLogger(__name__)

input_mapping = {
    "pdftotext": pdftotext,
    "tesseract": tesseract,
    "tesseract4": tesseract4,
    "pdfminer": pdfminer_wrapper,
    "gvision": gvision,
}

output_mapping = {"csv": to_csv, "json": to_json, "xml": to_xml, "none": None}

input_lang = {"deu": "deu", "eng": "eng"}


def extract_data(invoicefile, templates=None, input_module_lang="deu"):
    """Extracts structured data from PDF/image invoices.

    This function uses the text extracted from a PDF file or image and
    pre-defined regex templates to find structured data.

    Reads template if no template assigned
    Required fields are matches from templates

    Parameters
    ----------
    invoicefile : str
        path of electronic invoice file in PDF,JPEG,PNG (example: "/home/duskybomb/pdf/invoice.pdf")
    templates : list of instances of class `InvoiceTemplate`, optional
        Templates are loaded using `read_template` function in `loader.py`
    input_module : {'pdftotext', 'pdfminer', 'tesseract'}, optional
        library to be used to extract text from given `invoicefile`,

    Returns
    -------
    dict or False
        extracted and matched fields or False if no template matches

    Notes
    -----
    Import required `input_module` when using invoice2data as a library

    See Also
    --------
    read_template : Function where templates are loaded
    InvoiceTemplate : Class representing single template files that live as .yml files on the disk

    Examples
    --------
    When using `invoice2data` as an library

    >>> from invoice2data.input import pdftotext
    >>> extract_data("invoice2data/test/pdfs/oyo.pdf", None, pdftotext)
    {'issuer': 'OYO', 'amount': 1939.0, 'date': datetime.datetime(2017, 12, 31, 0, 0), 'invoice_number': 'IBZY2087',
     'currency': 'INR', 'desc': 'Invoice IBZY2087 from OYO'}

    """
    if templates is None:
        templates = read_templates()

    tesseracted = False
    extracted_str = pdftotext.to_text(invoicefile, input_module_lang).decode("utf-8")
    if extracted_str.strip() == "":
        logger.debug("No extractable text, running OCR...")
        extracted_str = tesseract.to_text(invoicefile, input_module_lang).decode("utf-8")
        tesseracted = True
    
    logger.debug("START text result ===========================")
    logger.debug(extracted_str)
    logger.debug("END text result =============================")

    logger.debug("Testing {} template files".format(len(templates)))
    
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)
       
        if t.matches_input(optimized_str):
            return t.extract(optimized_str)

    if tesseracted:
        logger.error("No template for %s", invoicefile)
        return False
        

    logger.debug("No template match! Re-reading...")
    extracted_str = tesseract.to_text(invoicefile, input_module_lang).decode("utf-8")
        
    logger.debug("START tesseract result ===========================")
    logger.debug(extracted_str)
    logger.debug("END tesseract result =============================")

    logger.debug("Testing {} template files".format(len(templates)))
    
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)
       
        if t.matches_input(optimized_str):
            return t.extract(optimized_str)


    logger.error("No template for %s", invoicefile)
    return False


def create_parser():
    """Returns argument parser """

    parser = argparse.ArgumentParser(
        description="Extract structured data from PDF files and save to CSV or JSON."
    )

    parser.add_argument(
        "--input-reader",
        choices=input_mapping.keys(),
        default="pdftotext",
        help="Choose text extraction function. Default: pdftotext",
    )

    parser.add_argument(
        "--input-reader-lang",
        choices=input_lang.keys(),
        default="deu",
        help="Choose text extraction language. Default: deu",
    )

    parser.add_argument(
        "--output-format",
        choices=output_mapping.keys(),
        default="none",
        help="Choose output format. Default: none",
    )

    parser.add_argument(
        "--output-date-format",
        dest="output_date_format",
        default="%Y-%m-%d",
        help="Choose output date format. Default: %%Y-%%m-%%d (ISO 8601 Date)",
    )

    parser.add_argument(
        "--output-name",
        "-o",
        dest="output_name",
        default="invoices-output",
        help="Custom name for output file. Extension is added based on chosen format.",
    )

    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Enable debug information."
    )

    parser.add_argument(
        "--copy",
        "-c",
        dest="copy",
        help="Copy and rename processed PDFs to specified folder.",
    )

    parser.add_argument(
        "--move",
        "-m",
        dest="move",
        help="Move and rename processed PDFs to specified folder.",
    )

    parser.add_argument(
        "--filename-format",
        dest="filename",
        default="{date} {invoice_number} {desc}.pdf",
        help="Filename format to use when moving or copying processed PDFs."
        'Default: "{date} {invoice_number} {desc}.pdf"',
    )

    parser.add_argument(
        "--template-folder",
        "-t",
        dest="template_folder",
        help="Folder containing invoice templates in yml file. Always adds built-in templates.",
    )

    parser.add_argument(
        "--exclude-built-in-templates",
        dest="exclude_built_in_templates",
        default=False,
        help="Ignore built-in templates.",
        action="store_true",
    )


    parser.add_argument(
        "--anonymize",
        dest="anonymize",
        help="Anonymize invoice and archive it"
    )

    parser.add_argument(
        "input_files",
        type=argparse.FileType("r"),
        nargs="+",
        help="File or directory to analyze.",
    )

    return parser


def main(args=None):
    """Take folder or single file and analyze each."""
    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    input_module = input_mapping[args.input_reader]

    input_module_lang = "deu"
    if args.input_reader_lang:
        input_module_lang = args.input_reader_lang
    
    output_module = output_mapping[args.output_format]

    templates = []
    # Load templates from external folder if set.
    if args.template_folder:
        templates += read_templates(os.path.abspath(args.template_folder))

    # Load internal templates, if not disabled.
    if not args.exclude_built_in_templates:
        templates += read_templates()
    output = []
    for f in args.input_files:
        res = extract_data(f.name, templates=templates, input_module_lang=input_module_lang)
        if res:
            logger.info(res)
            output.append(res)
            if args.copy:
                filename = args.filename.format(
                    date=res["date"].strftime("%Y-%m-%d"),
                    invoice_number=makeFilename(res["invoice_number"]),
                    desc=makeFilename(res["desc"]),
                )
                
                newName = join(args.copy, filename)
                shutil.copyfile(f.name, newName)

                if args.anonymize:
                    from anonymize import anonymize
                    anonymize(newName, args.anonymize)
                    
            if args.move:
                filename = args.filename.format(
                    date=res["date"].strftime("%Y-%m-%d"),
                    invoice_number=makeFilename(res["invoice_number"]),
                    desc=makeFilename(res["desc"]),
                )
                
                newName = join(args.move, filename)
                shutil.move(f.name, join(args.move, filename))

                if args.anonymize:
                    from anonymize import anonymize
                    anonymize(newName, args.anonymize)
        f.close()

    if output_module is not None:
        output_module.write_to_file(output, args.output_name, args.output_date_format)

def makeFilename(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import re
    import unicodedata
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)

    return value

if __name__ == "__main__":
    main()

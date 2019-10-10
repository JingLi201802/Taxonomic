import PyPDF2
import os
import requests
import pandas as pd
import re
import txtCrawl

border_words = ["in", "sp", "type", "and", "are", "figs"]
pre_buffer = 15
post_buffer = 20
created_files = []

# -----------------------------------------------Converting PDF to String----------------------------------------------


# Uses PDFBox to convert the PDF to a TXT file for analysis.
def pdf_to_text(file_name):
    file_path = replace_whitespaces(file_name)
    # Todo: detect when a .txt file is not created and cleanly exit with an error message (unavoidable due to
    #  permissions)
    os.system("java -jar pdfbox-app-2.0.16.jar ExtractText " + file_path)
    created_files.append(file_path)


# Removes temporary files
def cleanup():
    for txt in created_files:
        path = txt.replace(".pdf", ".txt")
        try:
            os.remove(path)
        except:
            print("Failed to remove {}".format(path))


def remove_punctuation(str):
    result_str = str.replace(",", "")
    result_str = result_str.replace(".", "")
    result_str = result_str.replace(" ", "")
    result_str = result_str.replace("&", "")
    result_str = result_str.replace(":", "")
    result_str = result_str.replace("(", "")
    result_str = result_str.replace(")", "")
    return result_str


# Finds high level information about the pdf like author
# data published, zoobank id etc. Does not look in the references section.
# Todo: fix issue where two words on different lines are merged during conversion
def find_document_data(doc_string, reference_index):
    word_list = doc_string.split(" ")
    url_list = []
    for word in word_list[:reference_index]:
        if word.__contains__("http"):
            word = word[word.index("http"):]
            url_list.append(word)

    for url in url_list:
        if url.__contains__("zootaxa") or url.__contains__("zoobank"):
            print("Self referencing information: " + url)


# Use anystyle.io to analyse references within a txt file.
# Currently has issues with false positives (Interpreting random sentences as references)
# TODO: Change command to work on multiple operating systems.
def find_references(txt_path):
    command = "anystyle --overwrite -f xml find {} {}".format(txt_path, get_example_path(""))
    os.system(command)

    # Add to list of files to cleanup later
    created_files.append(get_example_path(txt_path.split("/")[-1].replace(".txt", ".xml")))


# Returns an iterator containing the details and locations of all coordinates of the form xxºxx'xx"[NSEW]
def find_coordinates(doc_string):
    file = open(doc_string, 'r', encoding="utf8")
    string = file.read()
    # Regex taken from Regexlib.com ("DMS Coordinate by Jordan Pollard")
    res = re.findall(r"""[0-9]{1,2}[:|°|º][0-9]{1,2}[:|'](?:\b[0-9]+(?:\.[0-9]*)?|\.[0-9]+\b)"?[N|S|E|W]""", string, re.UNICODE)
    return res


# Todo: Given a string index, find the nearby name which that information is most likely to belong to.
def associate_info_with_name():
    return None

# -----------------------------------------------File operations--------------------------------------------------


def get_root_dir():
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)
    return parent_dir


# Abstract out the identical part of these two functions soonTM
def get_example_path(pdf_name):
    result = os.path.join(get_root_dir(), "Examples/PDFs/{}".format(pdf_name))
    return result.replace("\\", "/")


def get_output_path(name):
    result = os.path.join(get_root_dir(), "Output/{}/".format(name))
    if not os.path.exists(result):
        os.makedirs(result)
    return result.replace("\\", "/")


def get_config_path():
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)
    return os.path.join(parent_dir, "Config")


def get_configurations():
    get_key_words(get_config_path())


def replace_whitespaces(file_name):
    path = get_example_path(file_name)
    print (path)
    if(os.path.exists(path)):
        os.rename(path, path.replace(" ", "_"))
    return path.replace(" ", "_")


def get_key_words(config_path):
    key_word_file = "BorderWords.txt"
    txtCrawl.border_words.clear()
    file = open(key_word_file)
    lines = file.read().split("\n")
    for line in lines:
        if line.startswith("#"):
            continue

        txtCrawl.border_words.append(line)


# / means go one level deeper in JSON, [] means that the value should be treated as a list
direct_mappings = {
    "verbatim": "verbatim",
    "details[]/genus/value": "genus",
    "details[]/specificEpithet/value": "specificEpithet",
    "details[]/specificEpithet/authorship/value": "taxonomicNameAuthorship",
    "canonicalName/value": "taxonomicNameString", # The API and web version give different names for this field
    "canonicalName/simple": "taxonomicNameString", # Check if it's okay that canonical omits subgenus for subspecies
    "details[]/infraspecificEpithets[]/value": "infraspecificEpithet",
    "details[]/infragenericEpithet/value": "infragenericEpithet",
    "normalized": "taxonomicName",   # ask about this one
    "details[]/specificEpithet/combinationAuthorship/years[]": "namePublishedInYear",


    # Some of these duplciates may not be necessary
    "details[]/infraspecificEpithets[]/authorship/value": "taxonomicNameAuthorship",
    "details[]/specificEpithet/authorship/value": "taxonomicNameAuthorship",
    "details[]/specificEpithet/authorship/combinationAuthorship/authors[]": "combinationAuthorship",
    "details[]/specificEpithet/authorship/basionymAuthorship/authors[]": "basionymAuthorship",
    "details[]/infraspecificEpithets[]/authorship/combinationAuthorship/authors[]": "combinationAuthorship",
    "details[]/infraspecificEpithets[]/authorship/basionymAuthorship/authors[]": "basionymAuthorship",

    # Choose the year from the most relevant author, these entries overwrite previous so order is important
    "details[]/specificEpithet/authorship/basionymAuthorship/year/value": "namePublishedInYear",
    "details[]/specificEpithet/authorship/combinationAuthorship/year/value": "namePublishedInYear",
    "details[]/infraspecificEpithets[]/authorship/combinationAuthorship/year/value": "namePublishedInYear",
    "details[]/infraspecificEpithets[]/authorship/basionymAuthorship/year/value": "namePublishedInYear",
}

# ------------------------------------------ Create final output layer -------------------------------------------------


def raise_error(error_message):
    print("ERROR: " + error_message)


def analyse_pdf(pdf_name):
    get_configurations()
    pdf_to_text(pdf_name)

    if not os.path.exists(replace_whitespaces(pdf_name.replace(".pdf", ".txt"))):
        raise_error(
            "The PDF could not be converted to TXT, most likely because of a permissions issue from the PDF's creator")
        cleanup()
        return

    txtCrawl.get_csv_output_test(
        replace_whitespaces(pdf_name.replace(".pdf", ".txt")), direct_mappings,
        get_output_path(pdf_name.replace(".pdf", "")))
    cleanup()

# --------------------------------------------- Testing Code -----------------------------------------------------------

#analyse_pdf("Kurina_2019_Zootaxa4555_3 Diptera Mycetophilidae Manota new sp (1).pdf")
analyse_pdf("JABG31P037_Lang.pdf")
#analyse_pdf("CaseStudy3-ASB16_Dicranoloma (2).pdf")


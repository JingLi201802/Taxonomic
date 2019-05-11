import PyPDF2
import os
import requests
from nltk.corpus import words


common_ending_words = ["in", "sp."]
common_preceding_words = ["as", "australia"]
pre_buffer = 15
post_buffer = 15


def create_pdf_reader(path):
    pdf_file_obj = open(path, 'rb')
    return PyPDF2.PdfFileReader(pdf_file_obj)


def read_all_pages(pdf_reader):
    page_index = 0
    result = ""
    while page_index < pdf_reader.getNumPages():
        page = (pdf_reader.getPage(page_index).extractText())
        page = normalise_spacing(page)
        result = result + page
        page_index = page_index + 1
    return result


def read_page(page_num, pdf_reader):
    page = (pdf_reader.getPage(page_num).extractText())
    page = normalise_spacing(page)
    return page


def normalise_spacing(page):
    page = page.replace("\n", " ")
    page = page.replace("  ", " ")
    return page


def process_string(doc_string):
    working_index = 0

    for word in doc_string.split(" "):
        if word == "sp.":
            name = doc_string.split(" ")[working_index-pre_buffer: working_index+post_buffer]
            print(name)
            request_str = ""
            index = 0
            for name_component in name:
                if name_component.lower() in common_ending_words and index > pre_buffer+1:
                    break
                elif index < pre_buffer and name_component.lower() in common_preceding_words:
                    request_str = ""
                    continue
                request_str = request_str + ("+" + name_component)
                index += 1

            print(request_str[1:])
            #r = requests.get('http://parser.globalnames.org/api?q=' + (request_str[1:])) #print(r.json())
        working_index = working_index + 1


def get_example_path(pdf_name):
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)
    result = os.path.join(parent_dir, "Examples/PDFs/{}".format(pdf_name))
    return result.replace("\\", "/")


process_string(read_all_pages(create_pdf_reader(get_example_path("853.pdf"))))


def remove_punctuation(str):
    result_str = str.replace(",", "")
    result_str = result_str.replace(".", "")
    result_str = result_str.replace(" ", "")
    result_str = result_str.replace("&", "")
    return result_str

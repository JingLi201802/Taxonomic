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


# Replaced by PDFBox, function is kept so that the program can be executed if java is unavailable
def create_pdf_reader(path):
    pdf_file_obj = open(path, 'rb')
    return PyPDF2.PdfFileReader(pdf_file_obj)


# Replaced by PDFBox, function is kept so that the program can be executed if java is unavailable
def read_all_pages(pdf_reader):
    page_index = 0
    result = ""
    while page_index < pdf_reader.getNumPages():
        page = (pdf_reader.getPage(page_index).extractText())
        result = result + page
        page_index = page_index + 1
    return result


# Replaced by PDFBox, function is kept so that the program can be executed if java is unavailable
def read_page(page_num, pdf_reader):
    page = (pdf_reader.getPage(page_num).extractText())
    page = normalise_spacing(page)
    return page


# Uses PDFBox to convert the PDF to a TXT file for analysis.
def pdf_to_text(file_name):
    file_path = replace_whitespaces(file_name)
    os.system("java -jar pdfbox-app-2.0.16.jar ExtractText " + file_path)
    created_files.append(file_path)


# Removes temporary files
def cleanup():
    for txt in created_files:
        path = txt.replace(".pdf", ".txt")
        print ("Removing {}".format(path))
        try:
            os.remove(path)
        except:
            print("Failed to remove {}".format(path))

# Takes the path to a text file and returns a single-line string
def normalise_spacing(string):
    string = string.replace("\n", " ")
    string = string.replace("  ", " ")
    return string


def remove_punctuation(str):
    result_str = str.replace(",", "")
    result_str = result_str.replace(".", "")
    result_str = result_str.replace(" ", "")
    result_str = result_str.replace("&", "")
    result_str = result_str.replace(":", "")
    result_str = result_str.replace("(", "")
    result_str = result_str.replace(")", "")
    return result_str

# ---------------------------------- Extracting Information from Natural Language ----------------------------------


def process_string(doc_string):
    find_new_names(doc_string)
    find_coordinates(doc_string)
    reference_index = find_references(doc_string)
    find_document_data(doc_string, reference_index)


# currently does not return anything, just prints out relevant information #
# If a document mentions a name with sp. n. twice first is usually in abstract while second is description
# Later be amended to return the location of the string within the document.
def find_new_names(doc_string):
    working_index = 0
    word_list = normalise_spacing(doc_string).split(" ")
    combined_request_str = ""
    debugstr=""
    post_buffer = 20
    skip_next = False # Used to avoid detection of the same name twice
    for word in word_list:

        if skip_next:
            skip_next = False
            continue

        if word == "nov." or word == "sp.":
            skip_next = True
            confidence = 0
            name = word_list[working_index-pre_buffer: working_index+post_buffer]

            request_str = ""
            index = 0
            for name_component in name:
                if index > pre_buffer and remove_punctuation(name_component.lower()) in border_words and not remove_punctuation(name_component.lower()) == "":
                    confidence += 1
                    break

                elif index < pre_buffer and remove_punctuation(name_component.lower()) in border_words and not remove_punctuation(name_component) == "":
                    request_str = ""
                    debugstr = ""
                    confidence = 1
                    index += 1
                    continue

                name_component = name_component.replace("&", "%26")
                if len(remove_punctuation(name_component)) > 0:
                    request_str = request_str + ("+" + name_component)
                    debugstr += (name_component + " ")
                index += 1
            print("Confidence: {} for name: {}".format(confidence, debugstr))

            combined_request_str = combined_request_str + request_str + "|"
        working_index = working_index + 1

    r = requests.get('http://parser.globalnames.org/api?q=' + (combined_request_str[1:-1]))
    return r.json()


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
    return os.path.join(parent_dir, "Configuration")


def get_configurations():
    get_key_words(get_config_path())


def replace_whitespaces(file_name):
    path = get_example_path(file_name)
    if(os._exists(path)):
        os.rename(path, path.replace(" ", "_"))
    return path.replace(" ", "_")


def get_key_words(config_path):
    key_word_file = "BorderWords.txt"
    txtCrawl.border_words.clear()
    file = open(os.path.join(config_path, key_word_file))
    lines = file.read().split("\n")
    for line in lines:
        if line.startswith("#"):
            continue

        txtCrawl.border_words.append(line)

# ------------------------------------ Handling JSON from GNParser ----------------------------------------------------


def parse_json_list(json):
    name_results = []

    # Change this definition to be dependent on the dictionary mapping below so we don't need to change both each time
    json_targets = direct_mappings.keys()

    for item in json:
        print("item:" + str(item) + "\nResult")
        print(get_json_fields(item, json_targets))
        name_results.append(get_json_fields(item, json_targets))

    return name_results

# Add support for lists
def get_json_fields(json, targets):
    output_dict = dict()

    if not json['parsed']:
        print("This name was not able to be parsed")
        output_dict['verbatim'] = "unparsable"
        return output_dict


    for target in targets:
        index = 0
        target_path = target.split("/")
        pointer = json

        for node in target_path:
            if node.__contains__("[]"):
                if node.replace("[]", "") in pointer:
                    pointer = pointer[node.replace("[]", "")][0]
                    if node == target_path[-1]:
                        output_dict[target] = pointer
                else:
                    break

            else:
                if node in pointer:
                    pointer = pointer[node]
                    if node == target_path[-1]:
                        output_dict[target] = pointer

                else:
                    break

            index += 1
    return output_dict


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


def deduce_tnu_values(df, name_results):
    index = 1

    while index < df.size and not isinstance(df.at[index, 'scientificName'], float):

        # Uninomial -----------
        # Todo: change functionality so it detects uninomial- only 1 rank
        df.at[index, "uninomial"] = (df.at[index, 'scientificName'].split(" ")) == 1

        # TaxonRank ----------
        # Later need to add support for discovering new families and also tidy up and abstract
        if not isinstance(df.at[index, 'infraspecificEpithet'], float):
            df.at[index, "taxonRank"] = 'infraspecificEpithet'

        elif not isinstance(df.at[index, 'specificEpithet'], float):
            df.at[index, "taxonRank"] = 'specificEpithet'

        elif not isinstance(df.at[index, 'infragenericEpithet'], float):
            df.at[index, "taxonRank"] = 'infragenericEpithet'

        elif not isinstance(df.at[index, 'genus'], float):
            df.at[index, "taxonRank"] = 'genus'

        # VerbatimTaxonRank -----------
        # Temporary liberty before I clarify this point
        df.at[index, "verbatimTaxonRank"] = df.at[index, "taxonRank"]

        # TaxonomicNameStringWithAuthor ----------
        if not isinstance(df.at[index, "scientificNameAuthorship"], float):
            df.at[index, "fullNameWithAuthorship"] = df.at[index, "scientificName"] + " " + df.at[index, "scientificNameAuthorship"]
        index += 1

    return df

# ------------------------------------------ Create final output layer -------------------------------------------------


# Takes a list of GNParser results (a list of dictionaries) and deduces possible TNU fields for output
def add_dict_data_to_df(name_results):
    index = 1
    # Change this definition later to take columns from direct mappings + some others
    # Change the index definition to be dynamic
    df = pd.DataFrame(index=range(1, 10), columns=
     ["kindOfName", "scientificName", "taxonomicNameStringWithAuthor", "cultivarNameGroup",
      'verbatim', "uninomial", 'genus', "combinationAuthorship", "basionymAuthorship", "namePublishedInYear",
      "taxonRank", "verbatimTaxonRank", "taxonomicName", "protonym", "accordingTo", "nameAccordingTo",
      'infragenericEpithet', 'specificEpithet', "infraspecificEpithet", 'scientificNameAuthorship'])

    for result in name_results:
        print(result)
        for key in result:
            if key in direct_mappings:
                df.iloc[index][direct_mappings.get(key)] = result.get(key)

        index += 1

    df = deduce_tnu_values(df, name_results)
    print(df)

    return df


def get_csv_output(path):

    pdf_to_text(path)
    string_file = open(path.replace(".pdf", ".txt"), 'r', encoding="utf8")
    string = string_file.read()
    json = parse_json_list(find_new_names(string))
    df = add_dict_data_to_df(json)
    df.fillna(0.0).to_csv(get_output_path((path.split("/")[-1])[:-4]))

def analyse_pdf(pdf_name):
    get_configurations()
    pdf_to_text(pdf_name)
    txtCrawl.get_csv_output_test(
        replace_whitespaces(pdf_name.replace(".pdf", ".txt")), direct_mappings,
        get_output_path(pdf_name.replace(".pdf", "")))
    cleanup()

# --------------------------------------------- Testing Code -----------------------------------------------------------

analyse_pdf("Kurina_2019_Zootaxa4555_3 Diptera Mycetophilidae Manota new sp (1).pdf")
analyse_pdf("JABG31P037_Lang.pdf")


# pdf_to_text(get_example_path("JABG31P037_Lang.pdf"))
# process_string(get_example_path("JABG31P037_Lang.txt"))
# get_csv_output(get_example_path("JABG31P037_Lang.pdf"))
# print(find_references(convert(get_example_path("JABG31P037_Lang.pdf"))))
# (process_string(read_all_pages(
#    create_pdf_reader(get_example_path("853.pdf")))))

# get_csv_output("JABG31P037_Lang.pdf")
# get_csv_output("TestNames.pdf")
# print (find_references(read_all_pages(create_pdf_reader((get_example_path("853.pdf"))))))



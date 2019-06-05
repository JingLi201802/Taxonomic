import PyPDF2
import os
import requests
import pandas as pd


common_ending_words = ["in", "sp", "type", "and", "are", "figs"]
common_preceding_words = ["as", "australia", "holo", "iso", "perth", "canb", "species", "and"]
pre_buffer = 15
post_buffer = 20

# -----------------------------------------------Converting PDF to String----------------------------------------------


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
    reference_index = find_references(doc_string)
    find_document_data(doc_string, reference_index)


#currently does not return anything, just prints out relevant information #
# If a document mentions a name with sp. n. twice first is usually in abstract while second is description
#Later be amended to return the location of the string within the document.
def find_new_names(doc_string):
    working_index = 0
    word_list = doc_string.split(" ")
    combined_request_str = ""
    debugstr=""
    post_buffer = 20
    for word in word_list:
        if word == "nov." or word == "sp.":
            confidence = 0
            name = word_list[working_index-pre_buffer: working_index+post_buffer]
            # Abstract this to include variations of sp. nov. later and ensure they are close together as well
            if name.__contains__("nov.") or name.__contains__("Nov."):
                name = name[:pre_buffer]
                confidence += 1

            request_str = ""
            index = 0
            for name_component in name:
                if index > pre_buffer and remove_punctuation(name_component.lower()) in common_ending_words and not remove_punctuation(name_component.lower()) == "":
                    confidence += 1
                    break

                elif index < pre_buffer and remove_punctuation(name_component.lower()) in common_preceding_words and not remove_punctuation(name_component) == "":
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


# currently uses naiive approach: finding the last usage of the word references,
# should work 99% of the time but can still be improved
def find_references(doc_string):
    references = ""
    word_list = doc_string.split(" ")
    index = 0
    reference_index = 0
    for word in word_list:
        if word.lower() == "references":
            references = word_list[index:]
            reference_index = index
        index += 1

    if reference_index == 0:
        print("No reference section was detected")
        return reference_index
    print("References begin at word number " + str(reference_index))
    return reference_index


# Todo: extract coordinate information
def find_coordinates():
    return None


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
    result = os.path.join(get_root_dir(), "Output/{}_OUTPUT.xlsx".format(name))
    return result.replace("\\", "/")


def get_config_path():
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)
    return os.path.join(parent_dir, "Configuration")


def get_configurations():
    get_key_words(get_config_path())


def get_key_words(config_path):
    index = 0
    key_word_files = ["CommonPrecedingWords.txt", "CommonEndingWords.txt"]
    common_ending_words.clear()
    common_preceding_words.clear()
    while index < 2:
        file = open(os.path.join(config_path, key_word_files[index]))
        lines = file.read().split("\n")
        for line in lines:
            if line.startswith("#"):
                continue

            if key_word_files[index].__contains__("Preceding"):
                common_preceding_words.append(line)

            else:
                common_ending_words.append(line)
        index += 1

# ------------------------------------ Handling JSON from GNParser ----------------------------------------------------


def parse_json_list(json):
    name_results = []

    # Change this definition to be dependent on the dictionary mapping below so we don't need to change both each time
    json_targets = direct_mappings.keys()

    for item in json:
        name_results.append(get_json_fields(item, json_targets))

    return name_results

# Add support for lists
def get_json_fields(json, targets):
    if not json['parsed']:
        print("This name was not able to be parsed")
        return

    output_dict = dict()
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


# Todo: Attempt to fix situations where tabs/newlines are not registered by PyPDF which often interferes with parsing.
def correct_unintentional_joining():
    return None


# / means go one level deeper in JSON, [] means that the value should be treated as a list
direct_mappings = {
    "verbatim": "verbatim",
    "details[]/genus/value": "genus",
    "details[]/specificEpithet/value": "specificEpithet",
    "details[]/specificEpithet/authorship/value": "scientificNameAuthorship",
    "canonicalName/value": "scientificName", # The API and web version give different names for this field
    "canonicalName/simple": "scientificName", # Check if it's okay that canonical omits subgenus for subspecies
    "details[]/infraspecificEpithets[]/value": "infraspecificEpithet",
    "details[]/infragenericEpithet/value": "infragenericEpithet",
    "normalized": "taxonomicName",   # ask about this one
    "details[]/specificEpithet/combinationAuthorship/years[]": "namePublishedInYear",


    # Some of these duplciates may not be necessary
    "details[]/specificEpithet/authorship/value": "scientificNameAuthorship",
    "details[]/specificEpithet/authorship/combinationAuthorship/authors[]": "combinationAuthorship",
    "details[]/specificEpithet/authorship/basionymAuthorship/authors[]": "basionymAuthorship",
    "details[]/infraspecificEpithets[]/authorship/value": "scientificNameAuthorship",
    "details[]/infraspecificEpithets[]/authorship/combinationAuthorship/authors[]": "combinationAuthorship",
    "details[]/infraspecificEpithets[]/authorship/basionymAuthorship/authors[]": "basionymAuthorship",

    # Choose the year from the most relevant author I assume, these entries overwrite previous so order is important
    "details[]/specificEpithet/authorship/basionymAuthorship/year/value": "namePublishedInYear",
    "details[]/specificEpithet/authorship/combinationAuthorship/year/value": "namePublishedInYear",
    "details[]/infraspecificEpithets[]/authorship/combinationAuthorship/year/value": "namePublishedInYear",
    "details[]/infraspecificEpithets[]/authorship/basionymAuthorship/year/value": "namePublishedInYear",
}


def deduce_tnu_values(df, name_results):
    index = 1

    while index < df.size and not isinstance(df.at[index, 'scientificName'], float):

        # Uninomial -----------
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
        df.at[index, "taxonomicNameStringWithAuthor"] = df.at[index, "scientificName"] + " " + df.at[index, "scientificNameAuthorship"]
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
                df.set_value(index=index, col=direct_mappings.get(key), value=result.get(key))

        index += 1

    df = deduce_tnu_values(df, name_results)
    print(df)

    return df


def get_excel_output(path):
    reader = create_pdf_reader(get_example_path(path))
    json = parse_json_list(find_new_names(read_all_pages(reader)))
    df = add_dict_data_to_df(json)
    df.fillna(0.0).to_excel(get_output_path(path[:-4]))


# --------------------------------------------- Testing Code -----------------------------------------------------------

get_configurations()
# (process_string(read_all_pages(
#    create_pdf_reader(get_example_path("853.pdf")))))

#get_excel_output("JABG31P037_Lang.pdf")
get_excel_output("TestNames.pdf")


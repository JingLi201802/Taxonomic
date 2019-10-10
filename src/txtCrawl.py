import requests
import pandas as pd
import re
import json
import time

border_words = ["in", "sp", "type", "and", "are", "figs"]
name_list = []  # Make this non global in future
pre_buffer = 15
post_buffer = 1
word_locations = dict()


def get_csv_output_test(txt_filepath, direct_mappings, output_dir):
    publication_txt = open(txt_filepath, "r", encoding="utf-8")
    publication_string = publication_txt.read()
    names = parse_json_list(find_new_names(publication_string), direct_mappings)

    tndf = create_taxonomic_names(names, direct_mappings, output_dir)
    create_name_index_list(tndf, publication_string)
    create_bibliographic_reference(output_dir)
    create_typification(publication_string, output_dir)
    create_taxonomic_name_usages(output_dir)


def create_taxonomic_names(names, direct_mappings, output_dir):
    index = 1
    taxonomic_names_df = pd.DataFrame(index=range(1, len(names)+2), columns=
    ["taxonomicNameString", "fullNameWithAuthorship", "rank", "uninomial", "genus", "infragenericEpithet",
     "specificEpithet", "infraspecificEpithet", "cultivarNameGroup", "taxonomicNameAuthorship", "combinationAuthorship",
     "basionymAuthorship", "combinationExAuthorship", "basionymExAuthorship", "nomenclaturalStatus", "basedOn",
     "kindOfName", "nameRegistrationString"])
    print ("name length is {}".format(len(names)))
    # If there is a 1:1 relationship with GNParser result, put it straight into the dataframe
    for result in names:
        print(result)
        for key in result:
            if key in direct_mappings:
                taxonomic_names_df.iloc[index][direct_mappings.get(key)] = result.get(key)

        index += 1

    # Deduce the missing fields from what we have
    taxonomic_names_df = deduce_taxonomic_name_values(taxonomic_names_df)
    taxonomic_names_df = taxonomic_names_df.fillna(0.0)
    taxonomic_names_df.to_csv("{}taxonomicName.csv".format(output_dir))
    return taxonomic_names_df


def create_bibliographic_reference(output_dir):
    bibliographic_reference_df = pd.DataFrame(index=range(1, 10), columns=
    ["id", "title", "author", "year", "isbn", "issn", "citation", "shortRef", "doi", "volume",
     "edition", "pages", "displayTitle", "published", "publicationDate", "publishedLocation", "publisher",
     "refAuthorRole", "refType", "tl2", "uri", "publicationRegistration"])
    bibliographic_reference_df.fillna(0.0).to_csv("{}bibliographicReference.csv".format(output_dir))


def create_typification(doc_string, output_dir):
    detect_type_descriptions(doc_string)
    typification_df = pd.DataFrame(index=range(1, 10), columns=["nameUsage, typeOfType, typeName, typificationString"])
    typification_df.fillna(0.0).to_csv("{}typification.csv".format(output_dir))


def create_taxonomic_name_usages(output_dir):
    taxonomic_usage_df = pd.DataFrame(index=range(1, 10), columns=
    ["accordingTotaxonomicNameUsageLabel, verbatimNameString, verbatimRank, taxonomicStatus, acceptedNameUsage",
     "hasParent", "kindOfNameUsage", "microReference", "etymology"])
    taxonomic_usage_df.fillna(0.0).to_csv("{}taxonomicNameUsages.csv".format(output_dir))


def deduce_taxonomic_name_values(df):
    index = 1
    while index < len(df):
        if isinstance(df.at[index, 'taxonomicNameString'], float):
            index += 1
            continue

        # Uninomial -----------
        # Todo: change functionality so it detects uninomial- only 1 rank
        if (len(df.at[index, 'taxonomicNameString'].split(" "))) == 1:
            df.at[index, 'uninomial'] = df.at[index, 'taxonomicNameString']

        # TaxonRank ----------
        # Later need to add support for discovering new families and also tidy up and abstract
        if not isinstance(df.at[index, 'infraspecificEpithet'], float):
            df.at[index, "rank"] = 'infraspecificEpithet'

        elif not isinstance(df.at[index, 'specificEpithet'], float):
            df.at[index, "rank"] = 'specificEpithet'

        elif not isinstance(df.at[index, 'infragenericEpithet'], float):
            df.at[index, "rank"] = 'infragenericEpithet'

        elif not isinstance(df.at[index, 'genus'], float):
            df.at[index, "rank"] = 'genus'

        else:
            print("NO RANK DETECTED")

        # fullNameWithAuthorship ----------
        if not isinstance(df.at[index, "taxonomicNameAuthorship"], float):
            df.at[index, "fullNameWithAuthorship"] = df.at[index, "taxonomicNameString"] + " " + df.at[index, "taxonomicNameAuthorship"]
        index += 1

    return df


# Find the name which most closely precedes a given index
def associate_info(info_index, doc_string):
    doc = normalise_spacing(doc_string)
    best_diff = 10000000
    parent_name = "none"

    for key in word_locations.keys():
        difference = info_index - key
        if best_diff > difference > 0:
            best_diff = difference
            parent_name = word_locations[key]
    return parent_name


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
    result_str = result_str.replace("\n", "")
    return result_str


def parse_json_list(json, direct_mappings):
    name_results = []

    # Change this definition to be dependent on the dictionary mapping below so we don't need to change both each time
    json_targets = direct_mappings.keys()

    for item in json:
        name_results.append(get_json_fields(item, json_targets))

    return name_results


# Return true if the word is unlikely to be part of a name
def is_nl(word):
    if word.__contains__("http") or word.__contains__("www"):
        return True

    if detect_letter_and_number(word):
        return True

    # If the number is outside this range it will probably not be part of the name
    try:
        if float(remove_punctuation(word)) < 1000 or float(remove_punctuation(word)) > 2200:
            return True
        else:
            return False

    except ValueError:
        None

    if border_words.__contains__(remove_punctuation(word.lower())):
        return True

    return False


# https://www.tutorialspoint.com/How-to-check-if-a-string-has-at-least-one-letter-and-one-number-in-Python
def detect_letter_and_number(s):
    letter_flag = False
    number_flag = False
    for i in s:
        if i.isalpha():
            letter_flag = True
        if i.isdigit():
            number_flag = True
    return letter_flag and number_flag


def find_new_names(doc_string):
    working_index = 0
    word_list = normalise_spacing(doc_string).split(" ")
    combined_request = []
    debugstr=""
    skip_next = False  # Used to avoid detection of the same name twice
    for word in word_list:
        if skip_next:
            skip_next = False
            working_index = working_index + 1
            continue

        if word.lower() == "sp." or word.lower() == "gen.":
            skip_next = True
            confidence = 0
            name = word_list[working_index-pre_buffer: working_index+post_buffer]

            request_str = ""
            index = 0
            for name_component in name:
                if index > pre_buffer:
                    break

                elif index < pre_buffer and is_nl(name_component) \
                        and not remove_punctuation(name_component) == "":
                    request_str = ""
                    debugstr = ""
                    confidence = 1
                    index += 1
                    continue

                name_component = name_component.replace("&", "%26")
                if len(remove_punctuation(name_component)) > 0:
                    request_str = request_str + (" " + name_component)
                    debugstr += (name_component + " ")
                index += 1
            print("Confidence: {} for name: {}".format(confidence, debugstr))

            combined_request.append(request_str)  # combined_request_str = combined_request_str + request_str + "|"
        working_index = working_index + 1

    r = requests.post("http://parser.globalnames.org/api", json.dumps(combined_request))
    print(r)
    return r.json()


def detect_type_descriptions(doc_string):
    word_list = doc_string.split(" ")
    # uses_dms_coordinates = count_coordinates() > 2
    print("------------SEARCHING FOR TYPE DESCRIPTION---------------")
    word_index = 0
    for word in word_list:
        trust = False
        if remove_punctuation(word.lower()) == "holotype" or word.lower().__contains__("holo:"):
            end_point = word_index
            # If the word holotype seems to be used midway through a sentence it can usually be ignored
            if ["the", "a", "one", "their"].__contains__(word_list[word_index-1].lower()):
                print("discarded sentence usage")
                word_index = word_index + 1
                continue

            if set(map(str.lower, map(remove_punctuation, word_list[word_index-3:word_index+3]))) & set(["male", "female"]):
                print("holotype adjacent to gender")
                trust = True

            # If the holotype instance is thought to be a definition, search forward for the next instance of paratype:
            if trust:
                index = 0  # The index relative to the instance of "holotype"
                while index < 200:
                    if remove_punctuation(word_list[word_index + index]).lower().__contains__("paratype"):
                        end_point = word_index + index - 1
                        print("End point found. Type string reads: {}".format(word_list[word_index:end_point]))
                        break
                    index = index + 1

            print(word_list[word_index])

        word_index = word_index + 1
    # Search for variations of holo and paratype

    # Search around these instances to try and see if they are used as headings. Can search for: Coordinates, gender etc.
    # can also search to see if it is preceded by the/a
    # to work out if the heading precedes a description.
    # Can also search for "figure or fig" to try and filter out image captions
    print("----------------Finished searching for types---------------")
    return ""


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
                if node.replace("[]", "") in pointer and not node == "authors[]":
                    pointer = pointer[node.replace("[]", "")][0]
                    if node == target_path[-1]:
                        output_dict[target] = pointer
                # Check if this works. Should append all authors, but may crop
                elif node.replace("[]", "") in pointer:
                    result = ""
                    pointer = pointer[node.replace("[]", "")]
                    for author in pointer:
                        result = result + ", " + author

                    output_dict[target] = result[2:]
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


# possible utils

# Check names for overlap, for example new genuses and their subspecies will cause issues
# Also should account for cases where the genus is abbreviated eg G. astericus and Goodenia astericus
def create_name_index_list(taxonomic_names_df, doc_string):
    # Create a list of names in the document
    for index, row in taxonomic_names_df.iterrows():
        if isinstance(row['taxonomicNameString'], float):
            continue
        name_list.append(str(row['taxonomicNameString']))

    print (name_list)
    for name in name_list:
        result = re.finditer(name, doc_string)
        for match in result:
            word_locations[match.span()[1]] = name

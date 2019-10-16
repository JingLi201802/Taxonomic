import requests
import pandas as pd
import re
import json
import citationScraperPDF

border_words = ["in", "sp", "type", "and", "are", "figs"]

name_list = []
word_locations = dict() # Inverse index struct containing names and their indexes
word_locations_excl_figs = dict() # Same as above but excl names thought to be in image captions
name_string_to_verbatim = dict()
word_to_char = dict()


# main function, creates and populates output files
def get_csv_output(txt_filepath, direct_mappings, output_dir):
    publication_txt = open(txt_filepath, "r", encoding="utf-8")
    publication_string = publication_txt.read()
    publication_txt.close()
    names = parse_json_list(find_new_names(publication_string), direct_mappings)
    create_word_to_char(publication_string)

    bib_ref = create_bibliographic_reference(publication_string, output_dir)
    tndf = create_taxonomic_names(names, publication_string, direct_mappings, bib_ref, output_dir)
    tudf = create_taxonomic_name_usages(tndf, output_dir)
    create_typification(publication_string, tudf, output_dir)



# Create the taxonomic names output file
def create_taxonomic_names(names, doc_string, direct_mappings, bibref_df, output_dir):
    index = 0
    taxonomic_names_df = pd.DataFrame(index=range(1, len(names)+1), columns=
    ["id", "taxonomicNameString", "fullNameWithAuthorship", "rank", "uninomial", "genus", "infragenericEpithet",
     "specificEpithet", "infraspecificEpithet", "cultivarNameGroup", "taxonomicNameAuthorship", "combinationAuthorship",
     "basionymAuthorship", "combinationExAuthorship", "basionymExAuthorship", "nomenclaturalStatus", "basedOn",
     "kindOfName", "nameRegistrationString", "verbatimTaxonomicNameString"])
    print ("name length is {}".format(len(names)))
    # If there is a 1:1 relationship with GNParser result, put it straight into the dataframe
    for result in names:
        for key in result:
            if key in direct_mappings:
                taxonomic_names_df.iloc[index][direct_mappings.get(key)] = result.get(key)
        index += 1

        # Remove empty rows
        if isinstance(taxonomic_names_df.at[index, "taxonomicNameString"], float):
            taxonomic_names_df.drop(index=index)
            index -= 1


    # Deduce the missing fields from what we have
    taxonomic_names_df = deduce_taxonomic_name_values(taxonomic_names_df)

    # This is called before duplicates are dropped because its important that the list contains each instance of names
    create_name_index_list(taxonomic_names_df, doc_string)

    # Drop duplicates, preferring to keep names with authors
    taxonomic_names_df = taxonomic_names_df.sort_values('fullNameWithAuthorship', ascending=False)
    taxonomic_names_df = taxonomic_names_df.drop_duplicates(subset="taxonomicNameString")

    index = 0
    while index < len(taxonomic_names_df):
        if not isinstance(taxonomic_names_df.iloc[index]["taxonomicNameString"], float):
            taxonomic_names_df.iloc[index]['id'] = "TN-{}".format(index+1)
            taxonomic_names_df.iloc[index]['kindOfName'] = "scientific"
        index += 1

    taxonomic_names_df = taxonomic_names_df.fillna(0.0)
    taxonomic_names_df.to_csv("{}taxonomicName.csv".format(output_dir))
    return taxonomic_names_df


# Create the bibliographic reference output file
def create_bibliographic_reference(doc_string, output_dir):
    bibliographic_reference_df = pd.DataFrame(index=range(1, 2), columns=
    ["id", "title", "author", "year", "isbn", "issn", "citation", "shortRef", "doi", "volume",
     "edition", "pages", "PARENT:", "displayTitle", "published", "publicationDate", "publishedLocation", "publisher",
     "refAuthorRole", "refType", "tl2", "uri", "publicationRegistration"])

    doi = find_doi(doc_string)
    results_dic = dict()
    results_dic['success'] = 'false'  # citationScraperPDF.get_bib_results(doi)
    results_dic['formatchanged'] = 'false'

    # Respond to various errors which may occur when trying to scrape citethisforme
    if results_dic['formatchanged'] == 'true':
        bibliographic_reference_df.iloc[0]['id'] = "IMPORTANT: The layout of citethisforme's page may have changed!" \
                                                   "If this error persists the program will likely have to be updated" \
                                                   "in order to regain it's autocitation functionality."
        bibliographic_reference_df.fillna(0.0).to_csv("{}bibliographicReference.csv".format(output_dir))
        return

    if results_dic['success'] == 'false':
        bibliographic_reference_df.iloc[0]['id'] = "FAILED"
        bibliographic_reference_df.iloc[0]['title'] = "This happens occasionally due to citethisforme's somewhat " \
                                                   "inconsistent responses. Waiting for a minute and then " \
                                                   "retrying may fix the problem."
        print("citethisforme scraping unsuccessful")
        bibliographic_reference_df.fillna(0.0).to_csv("{}bibliographicReference.csv".format(output_dir))
        return

    bibliographic_reference_df.iloc[0]['id'] = "BIB-1"

    simple_fields = ["publisher", "title", "year", "doi", "volume", "pages", "uri", "displayTitle"]
    for field in simple_fields:
        bibliographic_reference_df.iloc[0][field] = results_dic[field]

    bibliographic_reference_df.iloc[0]['author'] = citationScraperPDF.concat_authors(results_dic)
    bibliographic_reference_df.fillna(0.0).to_csv("{}bibliographicReference.csv".format(output_dir))
    return bibliographic_reference_df


# Create the typification output file
def create_typification(doc_string, tudf, output_dir):
    type_data = detect_type_descriptions(doc_string)
    typdf = pd.DataFrame(index=range(1, len(type_data)+2), columns=
    ["nameUsage", "typeOfType", "typeName", "typificationString", "coordinates"])
    index = 0
    for name in type_data:
        type_string, type_type = type_data[name]

        # This name simplification process should be kept the same as in create_tnu as they are matched by it.
        _, simple_name = remove_identifiers(name_string_to_verbatim[name])
        typdf.iloc[index]["typeName"] = simple_name

        typdf.iloc[index]["nameUsage"] = \
            tudf.loc[tudf["taxonomicNameUsageLabel"] == typdf.iloc[index]["typeName"]].iloc[0]["id"]

        typdf.iloc[index]["typificationString"] = type_string
        typdf.iloc[index]["typeOfType"] = type_type

        coords_match = find_coordinates(type_string)
        if len(coords_match) > 0:
            typdf.iloc[index]["coordinates"] = coords_match[0]

        index += 1

    typdf.fillna(0.0).to_csv("{}typification.csv".format(output_dir))


# Create the TNU output file
def create_taxonomic_name_usages(tndf, output_dir):
    tudf = pd.DataFrame(index=range(1, len(tndf)), columns=
    ["id", "taxonomicName", "accordingTo", "taxonomicNameUsageLabel", "verbatimNameString", "verbatimRank",
     "taxonomicStatus", "acceptedNameUsage", "hasParent", "kindOfNameUsage", "microReference", "etymology"])

    # Dictionary containing corresponding fields between the two csvs
    tn_tnu = {"taxonomicName": "id", "verbatimNameString": "verbatimTaxonomicNameString"}
    index = 0
    # Iterate over rows of the taxonomic NAME dataframe
    while index < len(tndf)-1:
        # Insert shared values
        for key, value in tn_tnu.items():
            tudf.iloc[index][key] = tndf.iloc[index][value]

        tudf.iloc[index]["accordingTo"] = "BIB-1"

        # This name simplification process should be kept the same as in create_typification as they are matched by it.
        identifier, name_usage_label = remove_identifiers(tudf.iloc[index]["verbatimNameString"])
        tudf.iloc[index]["taxonomicNameUsageLabel"] = name_usage_label
        tudf.iloc[index]["id"] = tndf.iloc[index]["id"].replace("TN", "TNU")
        tudf.iloc[index]["acceptedNameUsage"] = tudf.iloc[index]["id"]
        tudf.iloc[index]["kindOfNameUsage"] = identifier + "nov."
        index += 1
    tudf.fillna(0.0).to_csv("{}taxonomicNameUsages.csv".format(output_dir))
    return tudf

# From the output of GNParser, deduce what other values we can
def deduce_taxonomic_name_values(df):
    index = 1
    while index < len(df):
        if isinstance(df.at[index, 'taxonomicNameString'], float):
            index += 1
            continue


        # Uninomial -----------
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


# Find the name which most closely precedes a given index.
# ignore_figures means try to ignore names that are probably captions of images
def associate_info(info_index, ignore_figures):
    best_diff = float('inf')
    parent_name = "none"

    if ignore_figures:
        inv_index_struct = word_locations_excl_figs
    else:
        inv_index_struct = word_locations

    for key in inv_index_struct.keys():
        difference = info_index - key
        if best_diff > difference > 0:
            best_diff = difference
            parent_name = inv_index_struct[key]
    return parent_name, best_diff


# Flatten the string to a single, normally spaced line
def normalise_spacing(string):
    string = string.replace("\n", " ")
    string = string.replace("  ", " ")
    return string


def remove_punctuation(str):
    result_str = str.replace(",", "")
    result_str = result_str.replace(".", "")
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


# Interpret the mapping from direct_mappings to flatten the json and store it's data in output_dict
def get_json_fields(json, targets):
    output_dict = dict()

    if not json['parsed']:
        output_dict['verbatim'] = "unparsable"
        return output_dict


    for target in targets:
        index = 0
        target_path = target.split("/")
        pointer = json

        for node in target_path:
            if node.__contains__("[]"):
                if node.replace("[]", "") in pointer and not node == "authors[]":
                    # Most list values are basically always a single element except in EXTREMELY rare theoretical cases
                    pointer = pointer[node.replace("[]", "")][0]
                    if node == target_path[-1]:
                        output_dict[target] = pointer

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
    pre_buffer = 15
    post_buffer = 1
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

        if word.lower() == "sp." and \
                (word_list[working_index+1].__contains__("n.") or word_list[working_index+1].__contains__("nov")):
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
            # If name is impossibly short just skip it
            # In future, if name is impossibly short we should work backwards to extend it.
            if len(request_str) < 5:
                working_index = working_index + 1
                continue

            # If this evaluates to true there's usually some weird formatting stuff like ...........scientific Name
            if len(request_str[1:]) - len(remove_punctuation(request_str[1:])) > 8:
                combined_request.append(remove_punctuation(request_str[1:]))
            else:
                combined_request.append(request_str[1:])
        working_index = working_index + 1


    r = requests.post("http://parser.globalnames.org/api", json.dumps(combined_request))

    print(r)
    print(r.json())
    return r.json()


# Change to stop at diagnosis and description as well as holotype.
# Search for type descriptions and then associate them with the closest preceding name. Return a dictionary of name:desc
def detect_type_descriptions(doc_string):
    type_data = dict()
    word_list = normalise_spacing(doc_string).split(" ")
    print("------------SEARCHING FOR TYPE DESCRIPTION---------------")
    word_index = 0
    for word in word_list:
        trust = False
        if remove_punctuation(word.lower()) == "holotype" or word.lower().__contains__("holo:") \
                or word.lower().__contains__("holo-"):

            gender_before = False  # Whether the word before holotype should be included or not

            # If the word holotype seems to be used midway through a sentence it can usually be ignored
            if ["the", "a", "one", "their"].__contains__(word_list[word_index-1].lower()
                                                         or ["can", "was", "has", "is", "that", "from",
                                                             "where"].__contains__(word_list[word_index+1].lower())):
                word_index = word_index + 1
                continue

            # If the holotype is right next to a gender then it is usually a definition
            if set(map(str.lower, map(remove_punctuation, word_list[word_index-1:word_index+5]))) \
                    & set(["male", "female"]):
                trust = True

                if ["male", "female"].__contains__(remove_punctuation(word_list[word_index-1]).lower()):
                    gender_before = True

            if not trust:
                trust = find_coordinates(doc_string[word_to_char[word_index]:word_to_char[word_index]+500])

            # If the holotype instance is thought to be a definition, search forward for the next instance of paratype:
            if trust:
                index = 0  # The index relative to the instance of "holotype"
                while index < 130:
                    if word_list[word_index + index].lower().__contains__("paratype") \
                            or word_list[word_index + index].lower().__contains__("allotype") \
                            or word_list[word_index + index].lower().__contains__("para:"):
                        end_point = word_index + index - 1
                        name, _ = associate_info(word_to_char[word_index], ignore_figures=True)
                        type_desc = ""
                        if gender_before:
                            typification_range = word_list[word_index-1:end_point]
                        else:
                            typification_range = word_list[word_index:end_point]
                        for word2 in typification_range:
                            type_desc += word2 + " "
                        type_data[name] = type_desc, "holotype"
                        break
                    index = index + 1

        word_index = word_index + 1

    print("----------------Finished searching for types---------------")
    return type_data


# Creates a dictionary which is able to convert an index in the form of the mth word into the nth character.
def create_word_to_char(doc_string):

    word_list = normalise_spacing(doc_string).split(" ")
    word_index = 0
    character_index = 0
    for word in word_list:
        word_to_char[word_index] = character_index
        word_index += 1
        character_index += len(word) + 1


# Used so regex search terms aren't interpreted as more complicated queries
def escape_regex_chars(query):
    result = query.replace(".", "\.")
    result = result.replace(",", "\,")
    result = result.replace("(", "\(")
    result = result.replace(")", "\)")
    return result


def find_document_data(doc_string, reference_index):
    word_list = normalise_spacing(doc_string).split(" ")
    url_list = []
    for word in word_list[:reference_index]:
        if word.__contains__("http"):
            word = word[word.index("http"):]
            url_list.append(word)

    for url in url_list:
        if url.__contains__("zootaxa") or url.__contains__("zoobank"):
            print("Self referencing information: " + url)


# Returns an iterator containing the details and locations of all coordinates of the form xxºxx'xx"[NSEW]
def find_coordinates(doc_string):

    # Find a latitude or longitude coordinate in DMS format:
    find_dms_comp = r"""[0-9]{1,2}[\,|\.|:|°|º][0-6][0-9][\,|\.|'][0-9]{1,2}\.[0-9]{0,8}[\.|\,\"|] {0,1}[N|S|E|W]"""
    find_dms_pairs = find_dms_comp+r"[\,| ] {0,2}"+find_dms_comp

    # Returns all coordinates using decimals
    res2 = re.findall(find_dms_pairs + "|" +
                      r"""[0-9]{1,2}\.[0-9]{1,10}[N|S][\,|\;] {0,2}1[0-8][0-9]\.[0-9]{1,10}[E|W]""",
                      doc_string, re.UNICODE)
    return res2


def find_doi(doc_string):
    doi = re.search(r"""\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b""", doc_string)
    if doi:
        return doi.group(0)
    return "failed to detect doi"


# Check names for overlap, for example new genuses and their subspecies will cause issues
# Also should account for cases where the genus is abbreviated eg G. astericus and Goodenia astericus
def create_name_index_list(taxonomic_names_df, doc_string):
    doc_string = normalise_spacing(doc_string)
    # Create a list of names in the document
    for index, row in taxonomic_names_df.iterrows():
        if isinstance(row['taxonomicNameString'], float):
            continue
        name = str(row['taxonomicNameString'])
        name_list.append(name)
        name_string_to_verbatim[name] = str(row["verbatimTaxonomicNameString"])

    for name in name_list:
        result = re.finditer(escape_regex_chars(name_string_to_verbatim[name]), doc_string, re.UNICODE)
        for match in result:
            word_locations[match.span()[1]] = name

            prev_h_chars = doc_string[match.span()[1]-80:match.span()[1]].lower()
            if not (prev_h_chars.__contains__("fig.")
                    or prev_h_chars.__contains__("figure")
                    or prev_h_chars.__contains__(name_string_to_verbatim[name])):
                word_locations_excl_figs[match.span()[1]] = name


def remove_identifiers(name_str):
    identifiers = ["sp.", "comb.", "gen.", "Gen.", "Sp.", "species", "genus", "combination", "spec."]
    for identifier in identifiers:
        if len(name_str.split(identifier)) > 1:
            ans = name_str.split(identifier)[0][:-1]
            if ans[-1] == ",":
                return identifier, ans[:-1]
            return identifier, ans

    return "", name_str

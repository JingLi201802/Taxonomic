import xml.etree.ElementTree as ET
import os
from lxml import etree
import pandas as pd
import collections
import xlwt
import xlrd

"""get the infomation about contribution
   @param target: absolute url for the input file
"""


def get_contri_info(target):
    # initialize
    agents_list = []
    reference_list = []
    agents_id = 0
    reference_id = 0
    """for multiple articles"""
    # src_path = os.path.dirname(os.path.realpath(__file__))
    # print(src_path)
    # find all the xml files
    # path_dir = os.listdir(src_path)
    # print(path_dir)
    # xml_file = []
    # for i in path_dir:
    #    if ".xml" in i:
    #        xml_file.append(i)
    # print(xml_file)
    # xml_file_no = len(xml_file)

    # for file_name in xml_file:

    """for single input"""

    reference_list_item = {}
    agents = {}
    reference_id += 1
    reference_list_item["id"] = "ref:" + "%05d" % reference_id
    print(" ------------------------ a new file--------------------------")
    # print(file_name)
    # target = os.path.join(src_path, file_name)
    tree = etree.parse(target)

    reference_pool = tree.xpath("//notes//sec//p//text()")
    doi = tree.xpath("//article-meta//article-id [@pub-id-type='doi']//text()")[0]
    zooBankNo = tree.xpath("//article-meta//article-id [@pub-id-type='other']//text()")
    for i in zooBankNo:
        if "zoobank" in i: zooBankNo = i
    print(doi)
    print(zooBankNo)

    # print(type(reference_pool))

    print(reference_pool)
    separator = ""
    reference = separator.join(reference_pool)

    print(reference)

    name_year_index = reference.find("(")
    year_end = reference.find(")")
    title_end = reference.find(".")
    name = reference[:name_year_index]
    title = reference[year_end + 2: title_end]
    print(title)
    print(name)
    reference_list_item["author lookup"] = name
    year = reference[name_year_index + 1:year_end]
    print(year)
    reference_list_item["year"] = year
    reference_list_item["title"] = title

    fname_list = tree.xpath("//article-meta//contrib-group//name//surname//text()")
    gname_list = tree.xpath("//article-meta//contrib-group//name//given-names//text()")
    print(fname_list)
    reference_list_item["quickRef"] = ", ".join(fname_list) + " " + year
    print(reference_list_item)
    print(gname_list)

    no_of_contributor = len(fname_list)
    if no_of_contributor > 1:
        agents_id += 1
        agents["type"] = "foaf:Group"
        agents["name"] = name
        agents["id"] = "ag:" + "%05d" % agents_id
        reference_list_item["author"] = "ag:" + "%05d" % agents_id
        sub_contributor_list = []
        member_range = list(range(agents_id + 1, no_of_contributor + agents_id + 2))
        agents["members"] = ""
        for i in range(len(member_range) - 2):
            agents["members"] += "ag:" + "%05d" % member_range[i] + "|"
        agents["members"] += "ag:" + "%05d" % (member_range.pop() - 1)
        agents_list.append(agents)
        for i in range(no_of_contributor):
            agents_id += 1
            term = {}
            term["type"] = "foaf:Person"
            term["familyName"] = fname_list[i]
            term["givenName"] = gname_list[i]
            term["name"] = term["familyName"] + ", " + term["givenName"]
            term["id"] = "ag:" + "%05d" % agents_id
            sub_contributor_list.append(term)
        print(sub_contributor_list)
        agents_list += sub_contributor_list
    else:
        agents_id += 1
        agents["type"] = "foaf:Person"
        agents["familyName"] = fname_list[0]
        agents["givenName"] = gname_list[0]
        agents["name"] = agents["familyName"] + ", " + agents["givenName"]
        agents["id"] = "ag:" + "%05d" % agents_id
        reference_list_item["author"] = "ag:" + "%05d" % agents_id
        agents_list.append(agents)
    print(agents)
    print(no_of_contributor)
    reference_list_item["doi"] = doi
    reference_list_item["zoobank number"] = zooBankNo
    reference_list.append(reference_list_item)

    print(agents_list)

    return agents_list, reference_list


"""write the captured data into excel
   @param a_list : agent infomation list
   @param r_list : reference information list
"""


def write_excel(a_list, r_list):
    book = xlwt.Workbook()
    sheet = book.add_sheet("agents", cell_overwrite_ok=True)
    reference_sheet = book.add_sheet("references", cell_overwrite_ok=True)

    cols = ["id", "type", "name", "familyName", "givenName", "members"]
    cols_ref = ["id", "type", "quickRef", "author", "author lookup", "year", "title", "doi", "zoobank number"]
    title = sheet.row(0)
    title_ref = reference_sheet.row(0)
    for i in range(len(cols)):
        value = cols[i]
        title.write(i, value)
    for num in range(len(a_list)):
        row = sheet.row(num + 1)
        for index, col in enumerate(cols):
            if col in a_list[num].keys():
                value = a_list[num][col]
                row.write(index, value)
    for i in range(len(cols_ref)):
        value = cols_ref[i]
        title_ref.write(i, value)
    for num in range(len(r_list)):
        row = reference_sheet.row(num + 1)
        for index, col in enumerate(cols_ref):
            if col in r_list[num].keys():
                value = r_list[num][col]
                row.write(index, value)
    book.save("taxonomy.xls")



""" quick reference column extract"""

def quick_reference(r_list):
    #print("---------------------------------------")
    print(r_list)
    quickRef_list = []
    for e in r_list:
        quickRef_list.append(e["quickRef"])
    print(quickRef_list)
##lists, ref_list = get_contri_info("/Users/lijing/Documents/comp8715project/Taxonomic/xml_reader/example.xml")


def write_reference_to_excel(a_list, r_list):
    write_excel(a_list, r_list)
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)
    # agent_path = os.path.join(parent_dir, "Output/xmlOutput/{}_XmlOutput.csv".format("agents.csv"))
    # references_path = os.path.join(parent_dir, "Output/xmlOutput/{}_XmlOutput.csv".format("references.csv"))
    """excel to csv """
    # agents = pd.read_excel('taxonomy.xls', 'agents', index_col=0)
    # agents.to_csv(agent_path, encoding='utf-8')
    # references = pd.read_excel('taxonomy.xls', 'references', index_col=0)
    # references.to_csv(references_path, encoding='utf-8')

lists, ref_list = get_contri_info("C:/Users/51651/Documents/GitHub/Taxonomic/Examples/xmls/A_new_genus_and_two_new_species_of_miniature_clingfishes.xml")

quick_reference(ref_list)

write_reference_to_excel(lists, ref_list)

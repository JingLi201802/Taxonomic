import xml.etree.ElementTree as ET
import os
from lxml import etree
# import pandas as pd
import collections
import xlwt


def get_contri_info():
    agents_list = []
    reference_list = []
    agents_id = 0
    reference_id = 0

    src_path = os.path.dirname(os.path.realpath(__file__))
    # print(src_path)
    # find all the xml files
    path_dir = os.listdir(src_path)
    # print(path_dir)
    xml_file = []
    for i in path_dir:
        if ".xml" in i:
            xml_file.append(i)
    # print(xml_file)
    xml_file_no = len(xml_file)

    for file_name in xml_file:
        reference_list_item = {}
        agents = {}
        reference_id += 1
        reference_list_item["id"] = "ref:" + "%05d" % reference_id
        print(" ------------------------ a new file--------------------------")
        print(file_name)
        target = os.path.join(src_path, file_name)
        tree = etree.parse(target)

        reference_pool = tree.xpath("//notes//sec//p//text()")
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
        reference_list.append(reference_list_item)


        print(agents_list)

    return agents_list, reference_list



def write_excel(a_list,r_list):
    book = xlwt.Workbook()
    sheet = book.add_sheet("agents", cell_overwrite_ok=True)
    reference_sheet = book.add_sheet("references", cell_overwrite_ok=True)

    cols = ["id", "type", "name", "familyName", "givenName", "members"]
    cols_ref = ["id", "type", "quickRef", "author", "author lookup", "year", "title"]
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
        title_ref.write(i,value)
    for num in range(len(r_list)):
        row = reference_sheet.row(num + 1)
        for index, col in enumerate(cols_ref):
            if col in ref_list[num].keys():
                value = ref_list[num][col]
                row.write(index, value)
    book.save("test.xls")






"""
def get_reference_information():
    reference_dict = {}
    src_path = os.path.dirname(os.path.realpath(__file__))
    # print(src_path)
    target = os.path.join(src_path, "zookeys.pensoft.net.xml")
    tree = etree.parse(target)
    # root = tree.getroot()
    print(tree)
    for elem in tree.iter(tag='journal-meta'):
        print(elem.tag, elem.text)
        for title in elem:
            print(title.tag, title.text)
    journal_title = tree.xpath("//journal-title//text()")
    # print(journal_title[0])
    reference_dict["publisher"] = journal_title[0]
    title = tree.xpath("//article-meta//article-title//text()")
    publish = tree.xpath("//journal-meta//text()")

    print(publish)
    print("here")
    # print('\n'.join(title))
    separator = ""
    # print(separator.join(title))  # article-title under article-meta
    reference_dict["article_title"] = separator.join(title)

    contribution = tree.xpath("//article-meta//contrib-group//name//text()")
    contribution = separator.join(contribution)  # contribution name
    contribution_list = contribution.split()
    # print(contribution_list)
    new_name_list = []

    for i in range(0, int(len(contribution_list) / 2)):
        # print(i)
        new_name_list.append(contribution_list[2 * i] + " " + contribution_list[2 * i + 1])
    # print(new_name_list)
    new_name = ",".join(new_name_list)
    # print(new_name)
    reference_dict["contribution"] = new_name
    date = tree.xpath("//pub-date//year//text()")[0]  # publish year
    reference_dict["publish_year"] = date
    # print(date)
    print(reference_dict)

"""

"""   
    root = tree.getroot()
    for elem in tree.iter(tag='title-group'):
        print(elem.tag, elem.text)
        for title in elem:
            print(title.tag, title.text)
            for t1 in title:
               # print(t1.tag, t1.text)
                for t2 in t1:
                    print(t2.text)
"""
lists,ref_list = get_contri_info()


write_excel(lists,ref_list)

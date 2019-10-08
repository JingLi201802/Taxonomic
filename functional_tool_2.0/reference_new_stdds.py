import os
from lxml import etree
import pandas as pd
import collections
import xlwt
import re
import calendar


# new reference extraction instead of using the notes part(citation):

""" read the articles"""

def read_article(path):
    tree = etree.parse(path)
    # print(tree)


    reference_dict = {}

    reference_dict["id"] = "BIB-1"
    """get the journal title"""
    journal_title_group = tree.xpath("//journal-title-group//text()")
    reference_dict["publisher"] = journal_title_group[1]
    # print(reference_dict["publisher"])

    """ get doi and zoobank # """
    doi = tree.xpath("//article-meta//article-id [@pub-id-type='doi']//text()")[0]
    reference_dict["doi"] = "doi:" + doi
    zooBankNo = tree.xpath("//uri [@content-type=\"zoobank\"]//text()")
    if len(zooBankNo) == 0:
        zooBankNo = tree.xpath("//self-uri [@content-type=\"zoobank\"]//text()")
        print("---------")
        print(zooBankNo)
        reference_dict["publicationRegistration"] = zooBankNo[0]
    else:
        reference_dict["publicationRegistration"] = "http://zoobank.org/"+zooBankNo[0]
    # print(doi)
    # print(zooBankNo)
    """ get the reference pages """
    start_page = tree.xpath("//article-meta//fpage//text()")[0]
    last_page = tree.xpath("//article-meta//lpage//text()")[0]
    reference_dict["pages"] = start_page + "-" +last_page

    """ get the volume # """
    reference_dict["volume"] = tree.xpath("//article-meta//volume//text()")[0]
    print(reference_dict["volume"])

    """get the publish date information"""
    pub_date = tree.xpath("//article-meta//pub-date [@pub-type='epub']//text()")
    month_abbr = calendar.month_abbr[int(pub_date[3])]
    reference_dict["year"] = pub_date[-2]
    reference_dict["publicationDate"] = pub_date[1] + "-" + month_abbr + "-" + reference_dict["year"]

    """get the article title"""
    title_group = tree.xpath("//title-group//text()")
    # print(title_group)
    reference_dict["title"] = "".join(title_group[1:-1])

    """ get the authors name"""
    contrib_surname_group = tree.xpath("//contrib-group//surname/text()")
    print(contrib_surname_group)
    contrib_given_name_group = tree.xpath("//contrib-group//given-names/text()")
    print(contrib_given_name_group)
    contrib_name = []
    for i in range(len(contrib_given_name_group)):
        contrib_name.append(contrib_given_name_group[i] + " " + contrib_surname_group[i])
    # print(contrib_name)

    reference_dict["author"] = ",".join(contrib_name)
    print(reference_dict["author"])

    """ use the information already in the dictionary to make a citation"""
    # get the uppercases in given name
    upper_in_given_name = []
    for i in range(len(contrib_given_name_group)):
        upper_in_given_name.append("")
        for j in contrib_given_name_group[i]:
            if j.isupper() : upper_in_given_name[i] += j
    # print(upper_in_given_name)

    """ citation format: surname + given name + (year) + title + publisher + volume: + pages
        e.g. Conway KW, Moore GI, Summers AP (2019) A new genus and two new species of miniature clingfishes from
        temperate southern Australia (Teleostei, Gobiesocidae). ZooKeys 864: 35–65.
    """

    citation_name = []
    citation = ""
    for i in range(len(contrib_given_name_group)):
        citation_name.append(contrib_surname_group[i] + " " + upper_in_given_name[i])
    print(citation_name)
    citation += ", ".join(citation_name)
    citation += " ("+ reference_dict["year"] + ") " + reference_dict["title"] + ", " + reference_dict["publisher"] + \
                " " + reference_dict["volume"] + ": " +reference_dict["pages"] + "."
    print(citation)
    reference_dict["citation"] = citation

    return reference_dict


def write_excel(dict, patha):
    book = xlwt.Workbook()
    sheet = book.add_sheet("BibliographicResource", cell_overwrite_ok=True)
    title = sheet.row(0)
    cols = ["id","title","author","year","isbn","issn","citation","shortRef","doi",
            "volume", "edition","pages","parent","displayTitle","publicationDate",
            "published", "publishedLocation","publisher","refAuthorRole", "refType",
            "tl2","uri","publicationRegistration","verbatimAuthor"]
    for c in range(len(cols)):
        value = cols[c]
        title.write(c, value)
    row = sheet.row(1)
    # print(dict.keys())
    for index, col in enumerate(cols):
        if col in dict[0][0].keys():
            # print(col)
            value = dict[0][0][col]
            row.write(index, value)

    book.save("BibliographicResource_1.xls")
    # path = "C:/Users/51651/Documents/GitHub/Taxonomic/Output/xmlOutput"
    agents = pd.read_excel('BibliographicResource_1.xls', 'BibliographicResource', index_col=0)
    agents.to_csv(patha)







# # current abs path
# pwd = os.getcwd()
# print(pwd)
# # article path
# article_path = pwd +"\\articles"+"\A_new_genus_and_two_new_species_of_miniature_clingfishes.xml"
# print(article_path)
# my_dict = read_article(article_path)
#
# write_excel(my_dict, "BibliographicResource.csv")

#
# a = os.listdir("articles")
# print(a)
# pwd = os.getcwd()
# for i in a:
#     print(i+".....................")
#     my_dict = read_article(
#         pwd +"\\articles\\"+i)
#     write_excel(my_dict,i+"BibliographicResource.csv")
#





#
# def get_contri_info(target):
#
#     reference_id = 0
#
#     reference_list_item = {}
#     reference_id += 1
#     reference_list_item["id"] = "BIB-" + str(reference_id)
#     print(" ------------------------ a new file--------------------------")
#
#     tree = etree.parse(target)
#
#     reference_pool = tree.xpath("//notes//sec//p//text()")
#     print(reference_pool)
#
#     reference_list_item["citation"] = reference_pool[0]
#     doi = tree.xpath("//article-meta//article-id [@pub-id-type='doi']//text()")[0]
#     doi ="doi:"+doi
#     zooBankNo = tree.xpath("//article-meta//article-id [@pub-id-type='other']//text()")
#     reference_list_item["volume"] = tree.xpath("//article-meta//volume//text()")[0]
#     start_page = tree.xpath("//article-meta//fpage//text()")[0]
#     last_page = tree.xpath("//article-meta//lpage//text()")[0]
#
#     reference_list_item["pages"] = start_page + "-" +last_page
#     pub_date = tree.xpath("//article-meta//pub-date [@pub-type='epub']//text()")
#     month_abbr = calendar.month_abbr[int(pub_date[3])]
#
#     reference_list_item["year"] = pub_date[-2]
#     reference_list_item["publicationDate"] = pub_date[1] + "-" + month_abbr +"-" + reference_list_item["year"]
#
#
#
#     reference_list_item["publisher"] = tree.xpath("//journal-meta//journal-title-group//text()")[1]
#
#     separator = ""
#     reference = separator.join(reference_pool)
#     year_end = reference.find(")")
#     title_end = reference.find(".")
#
#     reference_list_item["title"] = reference[year_end + 2: title_end]
#
#
#     print(zooBankNo)
#     flag = 1
#     for i in zooBankNo:
#         if "zoobank" in i:
#             zooBankNo = i
#             flag = 0
#     print(doi)
#     print(zooBankNo)
#     reference_list_item["doi"] = doi
#     print("zoobank list")
#     # print(zooBankNo_list)
#     if not flag:
#         zooBankNo_list = zooBankNo.split(":")
#         reference_list_item["publicationRegistration"] = "http://" + zooBankNo_list[2] + "/" + zooBankNo_list[-1]
#     else:
#         reference_list_item["publicationRegistration"] =""
#     # print(zooBankNo_list)
#
#
#
#     fname_list = tree.xpath("//article-meta//contrib-group//name//surname//text()")
#     gname_list = tree.xpath("//article-meta//contrib-group//name//given-names//text()")
#     print(fname_list)
#     print(gname_list)
#     reference_list_item["author"] = ""
#     author_list = []
#     for i in range(len(fname_list)):
#         author_list.append(gname_list[i] + " " + fname_list[i])
#     reference_list_item["author"] = ",".join(author_list)
#     print(reference_list_item["author"])
#
#     reference_list_item["refType"] = "Article"
#
#     print(reference_list_item)
#     return reference_list_item
#
#
#
# def write_excel(dict, patha):
#     book = xlwt.Workbook()
#     sheet = book.add_sheet("BibliographicResource", cell_overwrite_ok=True)
#     title = sheet.row(0)
#     cols = ["id","title","author","year","isbn","issn","citation","shortRef","doi",
#             "volume", "edition","pages","parent","displayTitle","publicationDate",
#             "published", "publishedLocation","publisher","refAuthorRole", "refType",
#             "tl2","uri","publicationRegistration","verbatimAuthor"]
#     for c in range(len(cols)):
#         value = cols[c]
#         title.write(c, value)
#     row = sheet.row(1)
#     for index, col in enumerate(cols):
#         if col in dict.keys():
#             value = dict[col]
#             row.write(index, value)
#
#
#     book.save("BibliographicResource_1.xls")
#     # path = "C:/Users/51651/Documents/GitHub/Taxonomic/Output/xmlOutput"
#     agents = pd.read_excel('BibliographicResource_1.xls', 'BibliographicResource', index_col=0)
#     agents.to_csv(patha)
#
#
# a = os.listdir("articles")
# print(a)
# for i in a:
#     print(i+".....................")
#     my_dict = get_contri_info(
#         "C:/Users/51651/Documents/GitHub/Taxonomic/functional_tool_2.0/articles/"+i)
#     write_excel(my_dict,i+"BibliographicResource.csv")
# #



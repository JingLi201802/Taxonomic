import os
from lxml import etree
import pandas as pd
import collections
import xlwt
import re
import calendar

def get_contri_info(target):

    reference_id = 0

    reference_list_item = {}
    reference_id += 1
    reference_list_item["id"] = "BIB-" + str(reference_id)
    print(" ------------------------ a new file--------------------------")

    tree = etree.parse(target)

    reference_pool = tree.xpath("//notes//sec//p//text()")
    print(reference_pool)

    reference_list_item["citation"] = reference_pool[0]
    doi = tree.xpath("//article-meta//article-id [@pub-id-type='doi']//text()")[0]
    doi ="doi:"+doi
    zooBankNo = tree.xpath("//article-meta//article-id [@pub-id-type='other']//text()")
    reference_list_item["volume"] = tree.xpath("//article-meta//volume//text()")[0]
    start_page = tree.xpath("//article-meta//fpage//text()")[0]
    last_page = tree.xpath("//article-meta//lpage//text()")[0]

    reference_list_item["pages"] = start_page + "-" +last_page
    pub_date = tree.xpath("//article-meta//pub-date [@pub-type='epub']//text()")
    month_abbr = calendar.month_abbr[int(pub_date[3])]

    reference_list_item["year"] = pub_date[-2]
    reference_list_item["publicationDate"] = pub_date[1] + "-" + month_abbr +"-" + reference_list_item["year"]



    reference_list_item["publisher"] = tree.xpath("//journal-meta//journal-title-group//text()")[1]

    separator = ""
    reference = separator.join(reference_pool)
    year_end = reference.find(")")
    title_end = reference.find(".")

    reference_list_item["title"] = reference[year_end + 2: title_end]


    print(zooBankNo)
    for i in zooBankNo:
        if "zoobank" in i: zooBankNo = i
    print(doi)
    print(zooBankNo)
    reference_list_item["doi"] = doi
    zooBankNo_list = zooBankNo.split(":")
    print(zooBankNo_list)
    reference_list_item["publicationRegistration"] = "http://" + zooBankNo_list[2] + "/" + zooBankNo_list[-1]


    fname_list = tree.xpath("//article-meta//contrib-group//name//surname//text()")
    gname_list = tree.xpath("//article-meta//contrib-group//name//given-names//text()")
    print(fname_list)
    print(gname_list)
    reference_list_item["author"] = ""
    author_list = []
    for i in range(len(fname_list)):
        author_list.append(gname_list[i] + " " + fname_list[i])
    reference_list_item["author"] = ",".join(author_list)
    print(reference_list_item["author"])

    reference_list_item["refType"] = "Article"

    print(reference_list_item)
    return reference_list_item



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
    for index, col in enumerate(cols):
        if col in dict[0][0].keys():
            value = dict[0][0][col]
            row.write(index, value)


    book.save("BibliographicResource_1.xls")
    # path = "C:/Users/51651/Documents/GitHub/Taxonomic/Output/xmlOutput"
    agents = pd.read_excel('BibliographicResource_1.xls', 'BibliographicResource', index_col=0)
    agents.to_csv(patha)



# my_dict = get_contri_info("C:/Users/51651/Documents/GitHub/Taxonomic/Examples/xmls/A_new_genus_and_two_new_species_of_miniature_clingfishes.xml")
#
# write_excel(my_dict)

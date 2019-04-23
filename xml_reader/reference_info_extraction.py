import xml.etree.ElementTree as ET
import os
from lxml import etree
# import pandas as pd


def get_reference_information():
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
    print(journal_title[0])
    title = tree.xpath("//article-meta//article-title//text()")
    publish = tree.xpath("//journal-meta//text()")
    # print(publish)
    # print('\n'.join(title))
    separator = ""
    print(separator.join(title))  # article-title under article-meta

    contribution = tree.xpath("//article-meta//contrib-group//name//text()")
    contribution = separator.join(contribution)  # contribution name
    print(contribution)
    date = tree.xpath("//pub-date//year//text()")[0]  # publish year
    print(date)




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
get_reference_information()




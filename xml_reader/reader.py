import os
import xml.etree.ElementTree as parse

src_path = os.path.dirname(os.path.realpath(__file__))
print(src_path)
xml = os.path.join(src_path, "zookeys.pensoft.net.xml")
print(xml)

xml_tree = parse.parse(xml)

root = xml_tree.getroot()

for child in root:
    for elem in child:
        if elem.tag == "article-meta":
            for sub_elem in elem:
                if sub_elem.tag == "abstract":
                    for ss in sub_elem:
                        # print(ss.tag)
                        for sss in ss:
                            # print(sss.tag)
                            if sss.tag == "{http://www.plazi.org/taxpub}taxon-name" or "italic":
                                for tn in sss:
                                    if tn.tag == "{http://www.plazi.org/taxpub}taxon-name":
                                        for tnp in tn:
                                            print(tnp.attrib)
                                    else:
                                        print(tn.attrib)


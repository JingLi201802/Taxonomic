import xml.etree.ElementTree as ET
import pandas as pd

def get_tag_dict():
    """Reads tags_config.txt and maps each of the tags to their data category label. Returns a dictionary."""
    tag_source_file = open("../tags_config.txt", 'r')
    tag_dict = {}
    for line in tag_source_file.readlines():
        if line[0] == "#" or len(line) < 5:
            continue
        target_line = line.replace("\n", "")
        target_line = target_line.replace(" ", "")
        try:
            tags, category = target_line.split("->")
        except:
            print("The config file may be formatted incorrectly, the following line could not be parsed: \n{}\n "
                  "please make sure each line is in the format a, b, c ... -> d".format(line))
            exit(0)
        for tag in tags.split(","):
            tag_dict[tag] = category
    tag_source_file.close()
    return tag_dict




allinfoList=list()
tempGenSpe=dict()  # {'genus':genus_name,''species':species_name}
tempGenSpe['genus']=''
tempGenSpe['species']=''
df_nonEmpty=pd.DataFrame(columns=['genus','species'])


articleName='../aTerrestrialFrog.xml'
tree=ET.parse(articleName)
root=tree.getroot()

doi=''
zooBankNumber=''

# def nextToSpn():
#     snpOutLoc='front/article-meta/abstract/p/'
#     global articleName
#     root=ET.parse(articleName)
#     for item in root.iterfind(snpOutLoc):
#         if item.attrib

def get_doi():
    global doi
    global root
    global zooBankNumber
    doiloc='./front/article-meta/article-id'
    for item in root.iterfind(doiloc):
        if item.attrib['pub-id-type']=='doi':
            doi=item.text
        if item.attrib['pub-id-type']=='other' and ('zoobank' in item.text):
            zooBankNumber=item.text


def get_abstract_info():
    """read the xml's abstract, extract new genus and species, store in a pandas structure"""

    global df_nonEmpty
    global root
    abStructure='./front/article-meta/abstract/p/italic/{http://www.plazi.org/taxpub}taxon-name/{http://www.plazi.org/taxpub}taxon-name-part'


    for item in root.iterfind(abStructure):
        if item.attrib['taxon-name-part-type']=='genus':
            tempGenSpe['genus']=item.attrib['reg']
        if item.attrib['taxon-name-part-type']=='species':
            tempGenSpe['species']=item.attrib['reg']

        if tempGenSpe['species']!='':
            insertRow=pd.Series([tempGenSpe['genus'],tempGenSpe['species']],index=['genus','species'])
            df_nonEmpty=df_nonEmpty.append(insertRow,ignore_index=True)
            tempGenSpe['genus']=''
            tempGenSpe['species']=''



def snpSingleInfo(item):
    genus=''
    species=''

    for subItem in item:

        if subItem.tag=='{http://www.plazi.org/taxpub}taxon-name-part':

            if subItem.attrib['taxon-name-part-type']=='genus':

                genus=subItem.text

            if subItem.attrib['taxon-name-part-type']=='species':
                species=subItem.text

    return (genus,species)
    # if item.tag=='{http://www.plazi.org/taxpub}taxon-status':
    #     if item.text in ('sp.n.' or 'n.sp.'):

def snpInBodySys():
    global root

    for item in root.iterfind('./body/sec'):

        if item.attrib['sec-type']=='Systematics':

            for item2 in item:

                if item2.tag=='{http://www.plazi.org/taxpub}taxon-treatment':

                    for item3 in item2:

                        if item3.tag=='{http://www.plazi.org/taxpub}nomenclature':
                            genus,species='',''
                            if item3.findall('{http://www.plazi.org/taxpub}taxon-status'):

                                for item4 in item3:

                                    if item4.tag=='{http://www.plazi.org/taxpub}taxon-name':

                                        genus,species=snpSingleInfo(item4)
                                        # print(genus,species)

                        snpnode=item3.findall('{http://www.plazi.org/taxpub}taxon-status')
                        for node in snpnode:
                            if ET.iselement(node):
                                print(genus,species)



snpInBodySys()


# get_abstract_info()
# print(df_nonEmpty)
# get_doi()
# print('doi is: '+doi)
# print('ZooBank number is: \n'+zooBankNumber)














# import xml.etree.ElementTree as parse
# root = parse.parse('../xmlExample.xml')    # Parse XML file
# doc = root.getroot()


# print(doc.tag)
# print(doc.attrib)


# rootT = root.find('channel/title')
# rootL = root.find('channel/link')
# rootD = root.find('channel/description')
# print(rootT.tag, rootT.attrib)
# print(rootL.tag, rootL.attrib)
# print(rootD.tag, rootD.attrib)
# print(rootT.text)
# print(rootL.text)
# print(rootD.text)



# for c in root.iterfind('channel'):
#     print(c.findtext('title'))
#     print(c.findtext('link'))
#     print(c.findtext('description'))

#
# for item in root.iterfind('channel/item/values'):
#     print(item.findtext('title'))
#     print(item.findtext('link'))
#     print(item.findtext('description'))
#
#
# for it in root.iterfind('channel/item'):
#     print(it.tag, it.attrib)
#
#
# root2 = doc.find('channel/title')
# print(root2.tag)
# print(root2.attrib)


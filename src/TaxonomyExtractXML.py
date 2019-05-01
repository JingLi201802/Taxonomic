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







#articleName='../aTerrestrialFrog.xml'
#articleName='../26newSpecies.xml'
#articleName='../NewGeneraOfAustralianStilettoFlies.xml'
#articleName='../aNewSpeciesOfWesmaeliusKrügerFromMexico.xml'
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
    global root

    tempGenSpe=dict()  # {'genus':genus_name,''species':species_name}
    tempGenSpe['genus']=''
    tempGenSpe['species']=''
    df_nonEmpty=pd.DataFrame(columns=['genus','species'])


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
    return df_nonEmpty




def snp_single_info(item2):
    genus=''
    species=''
    holotype_and_loc=''


    if item2.tag=='{http://www.plazi.org/taxpub}taxon-treatment':

        for item3 in item2:

            if item3.tag=='{http://www.plazi.org/taxpub}nomenclature':

                if item3.findall('{http://www.plazi.org/taxpub}taxon-name') and \
                        item3.findall('{http://www.plazi.org/taxpub}taxon-status'):

                    for item4 in item3:
                        if item4.tag=='{http://www.plazi.org/taxpub}taxon-name':

                            for item5 in item4:
                                if(item5.tag=='{http://www.plazi.org/taxpub}taxon-name-part'):
                                    if item5.attrib['taxon-name-part-type']=='genus':

                                        genus=item5.text
                                        #print(genus)

                                    if item5.attrib['taxon-name-part-type']=='species':
                                        species=item5.text
                                        #print(species)

            if item3.tag=='{http://www.plazi.org/taxpub}treatment-sec':
                if 'holotype' in item3.attrib['sec-type'].lower() or 'material' in item3.attrib['sec-type'].lower():

                    for item41 in item3:
                        if item41.tag=='p' and holotype_and_loc=='':
                            if item41.text!=None:
                                if (('male' in item41.text.lower()) or ('female' in item41.text.lower())) \
                                        and  ('holotype' in item41.text.lower()):
                                    holotype_and_loc=item41.text
                                    break
                            else:
                                for item6 in item41:
                                    if item6.text!=None:
                                        if (('Holotype' in item6.text) or ('holotype' in item6.tail)):
                                            if item6.tail!=None:

                                                holotype_and_loc=item6.tail
                                                break
                                    if item6.tail!=None:
                                        if (('male' in item6.tail) or ('female' in item6.tail)):
                                            holotype_and_loc=item6.tail
                                            break




    if (genus!='' and species!='' and holotype_and_loc!=''):
        print('1: '+genus,species)
        print('2:' +holotype_and_loc)
        print("-------------------------------------")
        return [genus,species,holotype_and_loc]
    else:

        return ([])




def get_info_recursive(item):


    for ite1 in item:
        if ('sec-type' in ite1.attrib):

            if ('Systematic' or 'systematic' or 'Taxonomy' or 'taxonomy' ) in ite1.attrib['sec-type']:

                for ite2 in ite1:

                    row=snp_single_info(ite2)


                    if row!=[] and row!=None:

                        return row
            else:

                get_info_recursive(ite1)





def get_info_from_body():

    global root
    df=pd.DataFrame(columns=['genus','species','holotype'])

    for item in root.iterfind('./body/sec'):
        if(item.tag=='sec'):

            #if ('Systematic' or 'systematic' or 'Taxonomy' or 'taxonomy') in item.attrib['sec-type']:

            if ('Systematic' in item.attrib['sec-type']) or ('systematic' in item.attrib['sec-type']) or \
                    ('Taxonomy' in item.attrib['sec-type'])or ('taxonomy' in item.attrib['sec-type']):

                for i1 in item:

                    row=snp_single_info(i1)

                    if(row!=None and row!=[]):


                        dfseries=pd.Series(row,index=['genus','species','holotype'])
                        df=df.append(dfseries,ignore_index=True)

            else:
                row2=get_info_recursive(item)
                if(row2!=[]) and row2!=None:


                    dfseries=pd.Series(row2,index=['genus','species','holotype'])
                    df=df.append(dfseries,ignore_index=True)
    return df


print(get_info_from_body())




def names_in_abstract_and_body():
    names_in_abstract=get_abstract_info()
    names_in_body=snp_in_body_sys()
    df_nonEmpty=pd.merge(names_in_abstract,names_in_body,on=['genus','species'],how='outer')
    return df_nonEmpty






#
# print(names_in_abstract_and_body())
# get_doi()
# print('doi is: '+doi)
# print('ZooBank number is: \n'+zooBankNumber)
















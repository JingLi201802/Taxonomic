import xml.etree.ElementTree as ET
import pandas as pd
import os

"""This is used to extract taxonomic information from xml file. The information include species, genuse,
sub genus, scientific name, gender, location...But not include article reference information, such as 
agency."""
# src_path = os.path.dirname(os.path.realpath(__file__))
#
# path_dir = os.listdir(src_path)
# # print(path_dir)
# xml_file = []
# for i in path_dir:
#     if ".xml" in i:
#         xml_file.append(i)
# articleName=xml_file[0]
# #articleName='aTerrestrialFrog.xml'
# #articleName='example.xml'
# #articleName='NewGeneraOfAustralianStilettoFlies.xml'
# #articleName='aNewSpeciesOfWesmaeliusKrügerFromMexico.xml'
# #articleName='ThreeNewSpeciesOfRhaphiumfromChina.xml'
# #articleName='AnewNigerianHunterSnailSpecies.xml'
#
# tree=ET.parse(articleName)
# root=tree.getroot()
#
# doi=''
# zooBankNumber=''

def get_root_dir():
    abs_file_path = os.path.abspath(__file__)
    #print(abs_file_path)
    parent_dir = os.path.dirname(abs_file_path)
    #print(parent_dir)
    parent_dir = os.path.dirname(parent_dir)
    #print(parent_dir)
    return parent_dir



def get_example_path(xml_name):
    """The xml example is in Examples/xmls/ , get this path"""

    result = os.path.join(get_root_dir(), "Examples/xmls/{}".format(xml_name))
    return result.replace("\\", "/")


def get_output_path(name):
    """Output is stored in Output/xmlOutput/"""
    result = os.path.join(get_root_dir(), "Output/xmlOutput/{}_XmlOutput.csv".format(name))
    return result.replace("\\", "/")

def get_doi(root):
    doi = ''
    zooBankNumber = ''

    doiloc='./front/article-meta/article-id'

    for item in root.iterfind(doiloc):
        if item.attrib['pub-id-type']=='doi':
            doi=item.text
        if item.attrib['pub-id-type']=='other' and ('zoobank' in item.text):
            zooBankNumber=item.text
    return [doi,zooBankNumber]


def get_abstract_info(root):

    """read the xml's abstract, extract new genus and species, store in a pandas structure"""
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



def get_coordinates(itemP):
    for it in itemP:
        if it.tag=="named-content":
            if ("content-type" in it.attrib) and it.attrib['content-type']=="dwc:verbatimCoordinates":
                for it1 in it:
                    if ("content-type" in it1.attrib) and (it1.attrib['content-type'])=='geo-json':
                        return it1.text


def get_family(it):
    family=''
    for it1 in it:
        for it2 in it1:
            for it3 in it2:
                if ('content-type' in it3.attrib) and it3.attrib['content-type']=='family':

                    family=it3.text
                    return family


    return family


def snp_single_info(item2):
    """Read from the the tag {http://www.plazi.org/taxpub}taxon-treatment and below"""
    family=''
    genus=''
    subgenus=''
    species=''
    holotype_and_loc=''
    coordinate=''
    taxon_authority=''
    taxon_status=''


    if item2.tag=='{http://www.plazi.org/taxpub}taxon-treatment':
        for item3 in item2:
            if item3.tag=='{http://www.plazi.org/taxpub}treatment-meta':
                family=get_family(item3)
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
                                    if item5.attrib['taxon-name-part-type']=='subgenus':
                                        subgenus=item5.text
                                    if item5.attrib['taxon-name-part-type']=='species':
                                        species=item5.text
                                        #print(species)
                        if item4.tag=='{http://www.plazi.org/taxpub}taxon-authority':
                            taxon_authority=item4.text
                        if item4.tag=='{http://www.plazi.org/taxpub}taxon-status':
                            taxon_status=item4.text

            if item3.tag=='{http://www.plazi.org/taxpub}treatment-sec':
                if 'holotype' in item3.attrib['sec-type'].lower() or 'material' in item3.attrib['sec-type'].lower()\
                        or 'types' in item3.attrib['sec-type'].lower():

                    for item41 in item3:
                        if item41.tag=='p' and holotype_and_loc=='':

                            if item41.text!=None:
                                if ((('male' in item41.text.lower()) or ('female' in item41.text.lower())) \
                                        and  ('holotype' in item41.text.lower()))or ('holotype' in item41.text.lower()):
                                    holotype_and_loc=item41.text
                                    coordinate=get_coordinates(item41)

                                    break
                            else:
                                for item6 in item41:
                                    if item6.text!=None:
                                        if ('Holotype' in item6.text) or ('holotype' in item6.tail):
                                            if item6.tail!=None:

                                                holotype_and_loc=item6.tail
                                                coordinate=get_coordinates(item41)
                                                break
                                    if item6.tail!=None:
                                        if (('male' in item6.tail) or ('female' in item6.tail)):
                                            holotype_and_loc=item6.tail
                                            coordinate=get_coordinates(item41)
                                            break

    # if (genus!='' or species!=''):
    #     # print('1: ')
    #     # print(family)
    #     # print(genus)
    #     # print(subgenus)
    #     # print(species)
    #     # if taxon_authority!=None:
    #     #     print('2:'+taxon_authority)
    #     # if holotype_and_loc!=None:
    #     #     print('3:' +holotype_and_loc)
    #     # if(coordinate!=None):
    #     #     print("4:" +coordinate)
    #     # if taxon_status!=None:
    #     #     print('5:'+taxon_status)
    #     #
    #     # print("-------------------------------------")
    #
    #     return [family,genus,subgenus,species,taxon_authority,holotype_and_loc,coordinate,taxon_status]
    # else:
    #
    #     return ([])
    if (family+genus+subgenus+species)!="" and (taxon_status!=""):
        return [family, genus, subgenus, species, genus+" "+species,taxon_authority, holotype_and_loc, coordinate, taxon_status]




def get_info_recursive(item):
    """In the systematic' or 'taxonomy section of the article, use np_single_info() to recursive get
    taxonomic information"""

    for ite1 in item:
        if ('sec-type' in ite1.attrib):

            if ( 'systematic' or 'taxonomy' ) in ite1.attrib['sec-type'].lower():

                for ite2 in ite1:

                    row=snp_single_info(ite2)


                    if row!=[] and row!=None:

                        return row
            else:
                get_info_recursive(ite1)





def get_info_from_body(root):
    """read the article, use np_single_info() to recursive get
        taxonomic information"""
    df=pd.DataFrame(columns=['family','genus','subgenus','species','scientificName','authorship','holotype','coordinates','taxon_status'])

    for item in root.iterfind('./body/sec'):
        if(item.tag=='sec'):

            if ('systematic' in item.attrib['sec-type'].lower()) or ('taxonomy' in item.attrib['sec-type'].lower()):

                for i1 in item:

                    row=snp_single_info(i1)

                    if(row!=None and row!=[]):


                        dfseries=pd.Series(row,index=['family','genus','subgenus','species','scientificName','authorship','holotype','coordinates','taxon_status'])
                        df=df.append(dfseries,ignore_index=True)

            else:
                row2=get_info_recursive(item)
                if(row2!=[]) and row2!=None:


                    dfseries=pd.Series(row2,index=['family','genus','subgenus','species','scientificName','authorship','holotype','coordinates','taxon_status'])
                    df=df.append(dfseries,ignore_index=True)
    print(df)
    return df



def write_csv(articleName):
    path=get_example_path(articleName)
    tree = ET.parse(path)
    root = tree.getroot()
    df=get_info_from_body(root)
    df.to_csv(get_output_path(articleName))


if __name__ == '__main__':
    write_csv("A_new_genus_and_two_new_species_of_miniature_clingfishes.xml")

import xml.etree.ElementTree as ET
import pandas as pd
from xlrd import open_workbook
import xlrd
from xlutils.copy import copy
from xlutils.margins import number_of_good_rows as number_of_row
from xml_reader import reference_info_extraction



#articleName='aTerrestrialFrog.xml'
articleName='26newSpecies.xml'
#articleName='NewGeneraOfAustralianStilettoFlies.xml'
#articleName='aNewSpeciesOfWesmaeliusKrügerFromMexico.xml'
#articleName='ThreeNewSpeciesOfRhaphiumfromChina.xml'
#articleName='AnewNigerianHunterSnailSpecies.xml'

tree=ET.parse(articleName)
root=tree.getroot()

doi=''
zooBankNumber=''



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

    if (genus!='' or species!=''):
        # print('1: ')
        # print(family)
        # print(genus)
        # print(subgenus)
        # print(species)
        # if taxon_authority!=None:
        #     print('2:'+taxon_authority)
        # if holotype_and_loc!=None:
        #     print('3:' +holotype_and_loc)
        # if(coordinate!=None):
        #     print("4:" +coordinate)
        # if taxon_status!=None:
        #     print('5:'+taxon_status)
        #
        # print("-------------------------------------")

        return [family,genus,subgenus,species,taxon_authority,holotype_and_loc,coordinate,taxon_status]
    else:

        return ([])




def get_info_recursive(item):

    for ite1 in item:
        if ('sec-type' in ite1.attrib):

            if ( 'systematic' or 'taxonomy' ) in ite1.attrib['sec-type'].lower():

                for ite2 in ite1:

                    row=snp_single_info(ite2)


                    if row!=[] and row!=None:

                        return row
            else:
                get_info_recursive(ite1)





def get_info_from_body():

    global root
    df=pd.DataFrame(columns=['family','genus','subgenus','species','taxon_authority','holotype','coordinates','taxon_status'])

    for item in root.iterfind('./body/sec'):
        if(item.tag=='sec'):

            if ('systematic' in item.attrib['sec-type'].lower()) or ('taxonomy' in item.attrib['sec-type'].lower()):

                for i1 in item:

                    row=snp_single_info(i1)

                    if(row!=None and row!=[]):


                        dfseries=pd.Series(row,index=['family','genus','subgenus','species','taxon_authority','holotype','coordinates','taxon_status'])
                        df=df.append(dfseries,ignore_index=True)

            else:
                row2=get_info_recursive(item)
                if(row2!=[]) and row2!=None:


                    dfseries=pd.Series(row2,index=['family','genus','subgenus','species','taxon_authority','holotype','coordinates','taxon_status'])
                    df=df.append(dfseries,ignore_index=True)
    return df

def write_species_to_excel():
    get_doi()

    doi_data='DOI is: '+doi
    zoobank_data='ZooBank number is: \n'+zooBankNumber
    articledata=[doi_data,zoobank_data]
    body_data = get_info_from_body()

    rb=open_workbook('taxonomy.xls')
    workbook=copy(rb)

    worksheet=workbook.add_sheet('taxonomic_name')
    worksheet.write(0,0,doi_data)
    worksheet.write(1,0,zoobank_data)
    column_name_in_article=['named-content','tp:taxion-name-part','tp:taxion-name-part',
                            'tp:taxion-name-part','tp:taxon-authority','tp:treatment-sec',
                            'named-content','tp:taxon-status']
    for j in range(len(column_name_in_article)):
        worksheet.write(2,j,column_name_in_article[j])
    tnu_name=['scientificName','scienfiticNameAuthorship','taxonRank']
    worksheet.write_merge(3,3,1,3,tnu_name[0])
    worksheet.write(3,4,tnu_name[1])
    worksheet.write(3,7,tnu_name[2])


    column_name=['family','genus','subgenus','species','taxon_authority','holotype','coordinates','taxon_status']
    for i in range(len(column_name)):
        worksheet.write(4,i,column_name[i])


    pre_row_number=5
    print(pre_row_number)
    pdrow=body_data.shape[0]
    pdcoloum=body_data.shape[1]

    for i in range(pdrow):
        for j in range(pdcoloum):
            worksheet.write(i+pre_row_number,j,body_data.iloc[i,j])


    workbook.save('taxonomy.xls')

def write_excel():
    reference_info_extraction.write_reference_to_excel()
    write_species_to_excel()


write_excel()

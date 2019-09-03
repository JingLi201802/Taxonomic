import xml.etree.ElementTree as ET
import pandas as pd
import os

"""This is used to extract taxonomic information from xml file. The information include species, genuse,
sub genus, scientific name, gender, location...But not include article reference information, such as 
agency."""


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
    #result = os.path.join(parent_dir, "functional_tool_2.0/xls_folder/{}.xls".format(name))
    # result = os.path.join(get_root_dir(), "Examples/xmls/{}".format(xml_name))
    result = os.path.join(get_root_dir(), "functional_tool_2.0/uploaded_folder/{}".format(xml_name))
    return result.replace("\\", "/")



def get_output_path(name):
    """Output is stored in Output/xmlOutput/"""
    # result = os.path.join(get_root_dir(), "Output/xmlOutput/{}_XmlOutput.csv".format(name))
    result = os.path.join(get_root_dir(), "functional_tool_2.0/csv_folder/{}_XmlOutput.csv".format(name))
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
    ## For debugging:
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

# -----------------------------------------------mapping output to TNC_TaxonomicName standard (tnc_tn)----------------------------------------------

def tnc_tn_id(df):
    id_list = []
    for i in range(len(df)):
        id_list.append("TN-" + str(i))
    return id_list


def tnc_tn_tns(df):
    """TaxonomicNameString, the complete uninomial, binomial or trinomial name without any authority or
    year components. Mapping to taxonomicNameString in TNC_TaxonomicName"""
    taxonomicNameString_list = df['scientificName']
    return taxonomicNameString_list

#Todo: when Authorship is empty, the author of article has the authorship. Get it from reference_info_extraction.py
def tnc__tn_fnwa(df):
    """Mapping to fullNameWithAuthorship in TNC_TaxonomicName"""
    fullNameWithAuthorship_list=[]
    for i in range(len(df['scientificName'])):
        fullNameWithAuthorship_list.append(df['scientificName'][i]+' '+df['authorship'][i])
    return fullNameWithAuthorship_list

def tnc__tn_rank(df):
    """The taxonomic rank of the name. Use standard abbreviations. Mapping to rank in TNC_TaxonomicName"""
    rank_list=[]
    for status in df['taxon_status']:
        if 'gen' in status:
            rank_list.append('genus')
        elif 'sp' in status:
            rank_list.append('species')
        else:
            rank_list.append('')
    return rank_list


def tnc_tn_uninomial(df):
    """Single-word name string for a name of generic or higher rank. Mapping to uninomial in TNC_TaxonomicName"""
    uninomial_list=[]
    rank=tnc__tn_rank(df)
    taxon_name_strings=tnc_tn_tns(df)

    for i in range(len(taxon_name_strings)):
        if rank[i]=='species':
            uninomial_list.append('')
        else:
            # name=taxon_name_strings[i]
            # u=name.split(' ')[-1]
            uninomial_list.append(taxon_name_strings[i])
    return uninomial_list


def tnc_tn_genus(df):
    """The genus part of combination. This property should not be used for names at and above the rank of genus.
    For those names the uninomial property should be used. Mapping to genus in TNC_TaxonomicName"""
    genus_list=[]
    original_genus=df['genus']
    rank=tnc__tn_rank(df)
    for i in range(len(rank)):
        if rank[i]=='species':
            genus_list.append(original_genus[i])
        else:
            genus_list.append('')
    return genus_list



def tnc_tn_infragenericEpithet(df):
    """The infrageneric part of a binomial name at ranks above species but below genus.
    Mapping to infragenericEpithet in TNC_TaxonomicName"""
    infrageneric_epithet=df['subgenus']
    return infrageneric_epithet


#TODO: find for subspecies and add it with species .
def tnc_tn_specificEpithet(df):
    """The specific epithet part of a binomial or trinomial name at or below the rank of species.
    Mapping to specificEpithet in TNC_TaxonomicName"""
    specific_Epithet=df['species']
    return specific_Epithet


#TODO: find for subspecies.
def tnc_tn_infraspecificEpithet(df):
    """The infraspecific epithet part of a trinomial name below the rank of species."""
    infraspecific_Epithet=[]
    for i in range(len(df)):
        infraspecific_Epithet.append('')

    return infraspecific_Epithet

#Not implement. We didn't see any plant xml article.
def tnc_tn_cultivarNameGroup(df):
    """The epithet for the cultivar, cultivar group, grex, convar or graft chimera under the International Code for
    the Nomenclature of Cultivated Plants (ICNCP)."""
    cultivar_NameGroup=[]
    for i in range(len(df)):
        cultivar_NameGroup.append('')
    return cultivar_NameGroup


#TODO: 1.Full name. 2. If empty, the author of article has authorship
def tnc_tn_taxonomicNameAuthorship(df):
    """The full code-appropriate authorship string for the Taxonomic Name."""
    taxonomicNameAuthorship=df['authorship']
    return taxonomicNameAuthorship

#TODO: 1. definition. 2. extract the value.
def tnc_tn_combinationAuthorship(df):
    """Authorship of the combination"""
    combination_Authorship = []
    for i in range(len(df)):
        combination_Authorship .append('')
    return combination_Authorship

#TODO: 1. definition. 2. extract the value.
def tnc_tn_basionymAuthorship(df):
    """Authorship of the basionym"""
    basionym_Authorship = []
    for i in range(len(df)):
        basionym_Authorship.append('')
    return basionym_Authorship

def tnc_tn_combinationExAuthorship(df):
    """People the combination has been attributed to, but clients didn’t provide the validating description."""
    combinationExAuthorship=[]
    for i in range(len(df)):
        combinationExAuthorship.append('')

    return combinationExAuthorship


def tnc_tn_basionymExAuthorship(df):
    """People the basionym has been attributed to, but who didn’t provide the validating description."""
    basionymExAuthorship=[]
    for i in range(len(df)):
        basionymExAuthorship.append('')
    return basionymExAuthorship




#TODO: extract the value.
def tnc_tn_publicationYear(df):
    """Year of publication of the Taxonomic Name."""
    publication_year = []
    for i in range(len(df)):
        publication_year.append('')
    return publication_year


def tnc_tn_nomenclaturalCode(df):
    """Nomenclatural code that applies to the group of organisms the taxonomic name is for Botanical, Zoological"""
    nomenclatural_Code =[]
    for i in range(len(df)):
        nomenclatural_Code.append('Zoological')
    return nomenclatural_Code


#TODO: understand the definiton, the difference between this and rank
def tnc_tn_nomenclaturalStatus(df):
    """Status related to the original publication of the name and its conformance to the relevant rules of
    nomenclature."""
    nomenclaturalStatus=[]
    for i in range(len(df)):
        nomenclaturalStatus.append('')
    return nomenclaturalStatus


#TODO: the field is not defined.
def tnc_tn_basedOn(df):
    bs = []
    for i in range(len(df)):
        bs.append('')
    return bs

def tnc_tn_kindOfName(df):
    namekind = []
    for i in range(len(df)):
        namekind.append('scientific')
    return namekind


#TODO: need to know where to find it
def tnc_tn_nameRegistrationString(df):
    nrs = []
    for i in range(len(df)):
        nrs.append('')
    return nrs



def change_To_TNC_Taxonomic_name(df):

    df2=pd.DataFrame(columns=['id','taxonomicNameString','fullNameWithAuthorship','rank','uninomial','genus',
                              'infragenericEpithet','specificEpithet','infraspecificEpithet', 'cultivarNameGroup',
                              'taxonomicNameAuthorship','combinationAuthorship','basionymAuthorship',
                              'combinationExAuthorship', 'basionymExAuthorship','publicationYear','nomenclaturalCode',
                              'nomenclaturalStatus','basedOn','kindOfName','nameRegistrationString'])
    df2['id']=tnc_tn_id(df)
    df2['taxonomicNameString']=tnc_tn_tns(df)
    df2['fullNameWithAuthorship']=tnc__tn_fnwa(df)

    df2['rank']=tnc__tn_rank(df)
    df2['uninomial']=tnc_tn_uninomial(df)
    df2['genus']=tnc_tn_genus(df)

    df2['infragenericEpithet']=tnc_tn_infragenericEpithet(df)
    df2['specificEpithet']=tnc_tn_specificEpithet(df)

    df2['infraspecificEpithet']=tnc_tn_infraspecificEpithet(df)
    df2['cultivarNameGroup']=tnc_tn_cultivarNameGroup(df)
    df2['taxonomicNameAuthorship']=tnc_tn_taxonomicNameAuthorship(df)
    df2['combinationAuthorship']=tnc_tn_combinationAuthorship(df)
    df2['basionymAuthorship']=tnc_tn_basionymAuthorship(df)
    df2['combinationExAuthorship']=tnc_tn_combinationExAuthorship(df)
    df2['basionymExAuthorship']=tnc_tn_basionymExAuthorship(df)
    df2['publicationYear']=tnc_tn_publicationYear(df)
    df2['nomenclaturalCode']=tnc_tn_nomenclaturalCode(df)
    df2['nomenclaturalStatus']=tnc_tn_nomenclaturalStatus(df)
    df2['basedOn']=tnc_tn_basedOn(df)
    df2['kindOfName']=tnc_tn_kindOfName(df)
    df2['nameRegistrationString']=tnc_tn_nameRegistrationString(df)


    return df2




def write_csv(articleName):
    path=get_example_path(articleName)
    tree = ET.parse(path)
    root = tree.getroot()
    df=get_info_from_body(root)
    df2=change_To_TNC_Taxonomic_name(df)
    df2.to_csv(get_output_path(articleName.split(".")[0]))


if __name__ == '__main__':
    write_csv("A_new_genus_and_two_new_species_of_miniature_clingfishes.xml")




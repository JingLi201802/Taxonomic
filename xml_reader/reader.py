import xml.etree.ElementTree as ET
import pandas as pd
import os
import reference_info_extraction as refextrac

"""This is used to extract taxonomic information from xml file. The information include species, genuse,
sub genus, scientific name, gender, location...But not include article reference information, such as 
agency."""


def get_root_dir():
    abs_file_path = os.path.abspath(__file__)
    # print(abs_file_path)
    parent_dir = os.path.dirname(abs_file_path)
    # print(parent_dir)
    parent_dir = os.path.dirname(parent_dir)
    # print(parent_dir)
    return parent_dir


def get_example_path(xml_name):
    """The xml example is in Examples/xmls/ , get this path"""
    # result = os.path.join(parent_dir, "functional_tool_2.0/xls_folder/{}.xls".format(name))
    result = os.path.join(get_root_dir(), "Examples/xmls/{}".format(xml_name))
    # result = os.path.join(get_root_dir(), "functional_tool_2.0/uploaded_folder/{}".format(xml_name))
    return result.replace("\\", "/")


def get_output_path(name):
    """Output is stored in Output/xmlOutput/"""
    result = os.path.join(get_root_dir(), "Output/xmlOutput/{}_XmlOutput.csv".format(name))
    # result = os.path.join(get_root_dir(), "functional_tool_2.0/csv_folder/{}_XmlOutput.csv".format(name))
    return result.replace("\\", "/")


def get_doi(root):
    doi = ''
    zooBankNumber = ''

    doiloc = './front/article-meta/article-id'

    for item in root.iterfind(doiloc):
        if item.attrib['pub-id-type'] == 'doi':
            doi = item.text
        if item.attrib['pub-id-type'] == 'other' and ('zoobank' in item.text):
            zooBankNumber = item.text
    return [doi, zooBankNumber]


def get_abstract_info(root):
    """read the xml's abstract, extract new genus and species, store in a pandas structure"""
    tempGenSpe = dict()  # {'genus':genus_name,''species':species_name}
    tempGenSpe['genus'] = ''
    tempGenSpe['species'] = ''
    df_nonEmpty = pd.DataFrame(columns=['genus', 'species'])

    abStructure = './front/article-meta/abstract/p/italic/{http://www.plazi.org/taxpub}taxon-name/{http://www.plazi.org/taxpub}taxon-name-part'

    for item in root.iterfind(abStructure):
        if item.attrib['taxon-name-part-type'] == 'genus':
            tempGenSpe['genus'] = item.attrib['reg']
        if item.attrib['taxon-name-part-type'] == 'species':
            tempGenSpe['species'] = item.attrib['reg']

        if tempGenSpe['species'] != '':
            insertRow = pd.Series([tempGenSpe['genus'], tempGenSpe['species']], index=['genus', 'species'])
            df_nonEmpty = df_nonEmpty.append(insertRow, ignore_index=True)
            tempGenSpe['genus'] = ''
            tempGenSpe['species'] = ''
    return df_nonEmpty


# def get_coordinates(item_p):
#     for it in item_p:
#         if it.tag == "named-content":
#             if ("content-type" in it.attrib) and it.attrib['content-type'] == "dwc:verbatimCoordinates":
#                 for it1 in it:
#                     if ("content-type" in it1.attrib) and (it1.attrib['content-type']) == 'geo-json':
#                         return it1.text


def find_paragrapy_content(item_p, holotype_loc_coor_list):
    """use this to find the content of a paragrapy. Used in find holotype&location*coordinates,
    paratype&location*coordinates, etymology """
    for child in item_p:
        # print('child.tag: ', child.tag)
        if child.tag != '{http://www.plazi.org/taxpub}taxon-name':

            if child.text != '' and child.text != None:
                ctext = child.text.replace('/n', '')
                ctext = ctext.strip()
                holotype_loc_coor_list.append(ctext)

            find_paragrapy_content(child, holotype_loc_coor_list)
            # print('child.tail: ', child.tail)
            if child.tail != '' and child.tail != None:
                ctail = child.tail.replace('/n', '')
                ctail = ctail.strip()
                # print("child.tail: ", ctail)
                holotype_loc_coor_list.append(ctail)


def join_paragraph_content(item_p):
    """use this to connect the content of a paragrapy. Used in find holotype&location*coordinates,
        paratype&location*coordinates, etymology """
    hlc_list = []
    if item_p.text != None:
        item_p_text = (item_p.text.replace('/n', '')).strip()
        # print(item_p_text)
        hlc_list.append(item_p_text)
    find_paragrapy_content(item_p, hlc_list)

    if item_p.tail != None:
        root_tail = (item_p.tail.replace('/n', '')).strip()
        # print(root_tail)
        hlc_list.append(root_tail)
    hlc = ''.join(hlc_list)

    return hlc


def get_family(it):
    family = ''
    for it1 in it:
        for it2 in it1:
            for it3 in it2:
                if ('content-type' in it3.attrib) and it3.attrib['content-type'] == 'family':
                    family = it3.text
                    return family

    return family


def snp_single_info(item2):
    """Read from the the tag {http://www.plazi.org/taxpub}taxon-treatment and below"""
    Australian_Administrator_Region = ['new south wales', 'queensland', 'south australia', 'tasmania', 'victoria',
                                       'western australia', 'australian capital territory', 'jervis bay territory',
                                       'northern territory', 'nsw', 'qld', 'sa', 'tas', 'vic', 'wa', 'act', 'jbt', 'nt']
    family = ''
    genus = ''
    subgenus = ''
    species = ''
    holotype_and_loc_and_coor = ''
    paratype_and_loc_and_coor = ''
    zoo_bank=''
    etymology=''
    taxon_authority = ''
    taxon_status = ''


    if item2.tag == '{http://www.plazi.org/taxpub}taxon-treatment':
        for item3 in item2:
            if item3.tag == '{http://www.plazi.org/taxpub}treatment-meta':
                family = get_family(item3)
            elif item3.tag == '{http://www.plazi.org/taxpub}nomenclature':

                if item3.findall('{http://www.plazi.org/taxpub}taxon-name') and \
                        item3.findall('{http://www.plazi.org/taxpub}taxon-status'):

                    for item4 in item3:
                        if item4.tag == '{http://www.plazi.org/taxpub}taxon-name':

                            for item5 in item4:
                                if (item5.tag == '{http://www.plazi.org/taxpub}taxon-name-part'):
                                    if item5.attrib['taxon-name-part-type'] == 'genus':
                                        genus = item5.text
                                        # print(genus)
                                    if item5.attrib['taxon-name-part-type'] == 'subgenus':
                                        subgenus = item5.text
                                    if item5.attrib['taxon-name-part-type'] == 'species':
                                        species = item5.text
                                        # print(species)
                                if item5.tag=='object-id':
                                    if 'content-type' in item5.attrib:
                                        if item5.attrib['content-type']=='zoobank':
                                            zoo_bank=item5.text


                        if item4.tag == '{http://www.plazi.org/taxpub}taxon-authority':
                            taxon_authority = item4.text
                        if item4.tag == '{http://www.plazi.org/taxpub}taxon-status':
                            taxon_status = item4.text

            elif item3.tag == '{http://www.plazi.org/taxpub}treatment-sec':
                if ('holotype' in item3.attrib['sec-type'].lower() or 'material' in item3.attrib['sec-type'].lower() \
                        or 'types' in item3.attrib['sec-type'].lower()) and holotype_and_loc_and_coor=='':


                    for item41 in item3:
                        if item41.tag == 'p' and holotype_and_loc_and_coor == '':
                            holotype_and_loc_and_coor = join_paragraph_content(item41)
                            if 'holotype' in holotype_and_loc_and_coor:
                                break


                elif 'paratypes' in item3.attrib['sec-type'].lower() and paratype_and_loc_and_coor=='':

                    for item41 in item3:
                        if item41.tag == 'p' and paratype_and_loc_and_coor == '':
                            paratype_and_loc_and_coor = join_paragraph_content(item41)

                            if 'paratypes' in paratype_and_loc_and_coor:
                                break
                elif 'etymology' in item3.attrib['sec-type'].lower():
                    for item42 in item3:
                        if item42.tag=='p':
                            etymology=join_paragraph_content(item42)


    ## For debugging:
    # if (genus != '' or species != ''):
    #         print('1: ')
    #         print(family)
    #         print(genus)
    #         print(subgenus)
    #         print(species)
    #         if taxon_authority!=None:
    #             print('2:'+taxon_authority)
    #         if holotype_and_loc_and_coor!=None:
    #     print('*****************************')
    #     print('3:' + holotype_and_loc_and_coor)
    #     #     if(coordinate!=None):
    #     print('*****************************')
    #     print("4:" + paratypes_and_loc_and_coor)
    #     # if taxon_status!=None:
    #     #     print('5:'+taxon_status)
    #     #

    #     # print("-------------------------------------")
    #
    #     return [family,genus,subgenus,species,taxon_authority,holotype_and_loc,coordinate,taxon_status]
    # else:
    #
    #     return ([])

    if (family + genus + subgenus + species) != "" and (taxon_status != ""):
        print('zoobank: ',zoo_bank)

        return [family, genus, subgenus, species, genus + " " + species, taxon_authority, holotype_and_loc_and_coor,
                paratype_and_loc_and_coor, zoo_bank, etymology,taxon_status]


def get_info_recursive(item):
    """In the systematic' or 'taxonomy section of the article, use np_single_info() to recursive get
    taxonomic information"""

    for ite1 in item:
        if ('sec-type' in ite1.attrib):

            if ('systematic' or 'taxonomy') in ite1.attrib['sec-type'].lower():

                for ite2 in ite1:

                    row = snp_single_info(ite2)

                    if row != [] and row != None:
                        return row
            else:
                get_info_recursive(ite1)


def get_quick_ref(path):
    lists, ref_dict = refextrac.get_contri_info(path)
    # print('****************************************************************************************************')
    # print('****************************************************************************************************')
    # print(lists)
    # print('****************************************************************************************************')
    # print(ref_dict)
    # print('****************************************************************************************************')
    quick_ref = ref_dict[0]['quickRef']
    # print(quick_ref)
    # print('****************************************************************************************************')
    return quick_ref


def get_info_from_body(root):
    """read the article, use np_single_info() to recursive get
        taxonomic information"""
    df = pd.DataFrame(
        columns=['family', 'genus', 'subgenus', 'species', 'scientificName', 'authorship', 'holotype_and_loc_and_coor',
                 'paratype_and_loc_and_coor', 'zoo_bank','etymology','taxon_status'])

    for item in root.iterfind('./body/sec'):
        if (item.tag == 'sec'):

            if ('systematic' in item.attrib['sec-type'].lower()) or ('taxonomy' in item.attrib['sec-type'].lower()):

                for i1 in item:

                    row = snp_single_info(i1)

                    if (row != None and row != []):
                        dfseries = pd.Series(row, index=['family', 'genus', 'subgenus', 'species', 'scientificName',
                                                         'authorship', 'holotype_and_loc_and_coor',
                                                         'paratype_and_loc_and_coor','zoo_bank','etymology',
                                                         'taxon_status'])
                        df = df.append(dfseries, ignore_index=True)

            else:
                row2 = get_info_recursive(item)
                if (row2 != []) and row2 != None:
                    dfseries = pd.Series(row2, index=['family', 'genus', 'subgenus', 'species', 'scientificName',
                                                      'authorship', 'holotype_and_loc_and_coor',
                                                      'paratype_and_loc_and_coor','zoo_bank','etymology',
                                                      'taxon_status'])
                    df = df.append(dfseries, ignore_index=True)
    print(df)
    return df


# -----------------------------------------------mapping output to TNC_TaxonomicName standard (tnc_tn)----------------------------------------------

def tnc_tn_id(df):
    id_list = []
    for i in range(len(df)):
        id_list.append("TN-" + str(i + 1))
    return id_list


def tnc_tn_tns(df):
    """TaxonomicNameString, the complete uninomial, binomial or trinomial name without any authority or
    year components. Mapping to taxonomicNameString in TNC_TaxonomicName"""
    taxonomicNameString_list = df['scientificName']
    return taxonomicNameString_list


def tnc__tn_fnwa_publicationYear(df, path):
    """return two values. 1.Mapping to fullNameWithAuthorship in TNC_TaxonomicName.
    2. Year of publication of the Taxonomic Name."""


    quick_reference_str = get_quick_ref(path)

    qrlist = quick_reference_str.split(' ')[:-1]# quick reference without year
    year = quick_reference_str.split(' ')[-1]
    qr = ' '.join(qrlist)


    fullNameWithAuthorship_list = []
    for i in range(len(df['scientificName'])):
        sn = df['scientificName'][i]
        if df['scientificName'][i][-1] == ' ':
            sn = df['scientificName'][i][:-1]

        if df['authorship'][i] != '':

            fullNameWithAuthorship_list.append(sn + ' ' + df['authorship'][i])
        else:

            fullNameWithAuthorship_list.append(sn + ' ' + qr)

    return fullNameWithAuthorship_list, year


def tnc__tn_rank(df):
    """The taxonomic rank of the name. Use standard abbreviations. Mapping to rank in TNC_TaxonomicName"""
    rank_list = []
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
    uninomial_list = []
    rank = tnc__tn_rank(df)
    taxon_name_strings = tnc_tn_tns(df)

    for i in range(len(taxon_name_strings)):
        if rank[i] == 'species':
            uninomial_list.append('')
        else:
            name = taxon_name_strings[i]
            u = name.split(' ')[-1]
            uninomial_list.append(u)
    return uninomial_list


def tnc_tn_genus(df):
    """The genus part of combination. This property should not be used for names at and above the rank of genus.
    For those names the uninomial property should be used. Mapping to genus in TNC_TaxonomicName"""
    genus_list = []
    original_genus = df['genus']
    rank = tnc__tn_rank(df)
    for i in range(len(rank)):
        if rank[i] == 'species':
            genus_list.append(original_genus[i])
        else:
            genus_list.append('')
    return genus_list


def tnc_tn_infragenericEpithet(df):
    """The infrageneric part of a binomial name at ranks above species but below genus.
    Mapping to infragenericEpithet in TNC_TaxonomicName"""
    infrageneric_epithet = df['subgenus']
    return infrageneric_epithet


# TODO: find for subspecies and add it with species .
def tnc_tn_specificEpithet(df):
    """The specific epithet part of a binomial or trinomial name at or below the rank of species.
    Mapping to specificEpithet in TNC_TaxonomicName"""
    specific_Epithet = df['species']
    return specific_Epithet


# TODO: find for subspecies.
def tnc_tn_infraspecificEpithet(df):
    """The infraspecific epithet part of a trinomial name below the rank of species."""
    infraspecific_Epithet = []
    for i in range(len(df)):
        infraspecific_Epithet.append('')

    return infraspecific_Epithet


# Not implement. We didn't see any plant xml article.
def tnc_tn_cultivarNameGroup(df):
    """The epithet for the cultivar, cultivar group, grex, convar or graft chimera under the International Code for
    the Nomenclature of Cultivated Plants (ICNCP)."""
    cultivar_NameGroup = []
    for i in range(len(df)):
        cultivar_NameGroup.append('')
    return cultivar_NameGroup


def tnc_tn_taxonomicNameAuthorship(df, path):
    """The full code-appropriate authorship string for the Taxonomic Name."""
    quick_reference_str = get_quick_ref(path)
    qrlist = quick_reference_str.split(' ')[:-1]
    # get rid of year,
    qr = ' '.join(qrlist)

    taxonomicNameAuthorship = df['authorship']
    for i in range(len(taxonomicNameAuthorship)):
        if taxonomicNameAuthorship[i] == '':
            taxonomicNameAuthorship[i] = qr
    return taxonomicNameAuthorship


# TODO: 1. definition. 2. extract the value.
def tnc_tn_combinationAuthorship(df):
    """Authorship of the combination"""
    combination_Authorship = []
    for i in range(len(df)):
        combination_Authorship.append('')
    return combination_Authorship


# TODO: 1. definition. 2. extract the value.
def tnc_tn_basionymAuthorship(df):
    """Authorship of the basionym"""
    basionym_Authorship = []
    for i in range(len(df)):
        basionym_Authorship.append('')
    return basionym_Authorship


def tnc_tn_combinationExAuthorship(df):
    """People the combination has been attributed to, but clients didn’t provide the validating description."""
    combinationExAuthorship = []
    for i in range(len(df)):
        combinationExAuthorship.append('')

    return combinationExAuthorship


def tnc_tn_basionymExAuthorship(df):
    """People the basionym has been attributed to, but who didn’t provide the validating description."""
    basionymExAuthorship = []
    for i in range(len(df)):
        basionymExAuthorship.append('')
    return basionymExAuthorship


def tnc_tn_nomenclaturalCode(df):
    """Nomenclatural code that applies to the group of organisms the taxonomic name is for Botanical, Zoological"""
    nomenclatural_Code = []
    for i in range(len(df)):
        nomenclatural_Code.append('Zoological')
    return nomenclatural_Code


# TODO: understand the definiton, the difference between this and rank
def tnc_tn_nomenclaturalStatus(df):
    """Status related to the original publication of the name and its conformance to the relevant rules of
    nomenclature."""
    nomenclaturalStatus = []
    for i in range(len(df)):
        nomenclaturalStatus.append('')
    return nomenclaturalStatus


# TODO: the field is not defined.
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


def tnc_tn_nameRegistrationString(df):

    nrs = df['zoo_bank']

    return nrs


def change_To_TNC_Taxonomic_name(df, path):
    df2 = pd.DataFrame(columns=['id', 'taxonomicNameString', 'fullNameWithAuthorship', 'rank', 'uninomial', 'genus',
                                'infragenericEpithet', 'specificEpithet', 'infraspecificEpithet', 'cultivarNameGroup',
                                'taxonomicNameAuthorship', 'combinationAuthorship', 'basionymAuthorship',
                                'combinationExAuthorship', 'basionymExAuthorship', 'publicationYear',
                                'nomenclaturalCode',
                                'nomenclaturalStatus', 'basedOn', 'kindOfName', 'nameRegistrationString'])
    df2['id'] = tnc_tn_id(df)
    df2['taxonomicNameString'] = tnc_tn_tns(df)
    df2['fullNameWithAuthorship'],df2['publicationYear'] = tnc__tn_fnwa_publicationYear(df, path)

    df2['rank'] = tnc__tn_rank(df)
    df2['uninomial'] = tnc_tn_uninomial(df)
    df2['genus'] = tnc_tn_genus(df)

    df2['infragenericEpithet'] = tnc_tn_infragenericEpithet(df)
    df2['specificEpithet'] = tnc_tn_specificEpithet(df)

    df2['infraspecificEpithet'] = tnc_tn_infraspecificEpithet(df)
    df2['cultivarNameGroup'] = tnc_tn_cultivarNameGroup(df)
    df2['taxonomicNameAuthorship'] = tnc_tn_taxonomicNameAuthorship(df, path)
    df2['combinationAuthorship'] = tnc_tn_combinationAuthorship(df)
    df2['basionymAuthorship'] = tnc_tn_basionymAuthorship(df)
    df2['combinationExAuthorship'] = tnc_tn_combinationExAuthorship(df)
    df2['basionymExAuthorship'] = tnc_tn_basionymExAuthorship(df)

    df2['nomenclaturalCode'] = tnc_tn_nomenclaturalCode(df)
    df2['nomenclaturalStatus'] = tnc_tn_nomenclaturalStatus(df)
    df2['basedOn'] = tnc_tn_basedOn(df)
    df2['kindOfName'] = tnc_tn_kindOfName(df)
    df2['nameRegistrationString'] = tnc_tn_nameRegistrationString(df)

    return df2


# -----------------------------------------------mapping output to TNC_TaxonomicNameUsage (tnc_tnu)-----------------
def usage_taxonomic_Name(df2):
    return tnc_tn_id(df2)


def usage_id(df2):
    length = len(tnc_tn_id(df2))

    usage_id_list = []
    for i in range(length):
        usage_id_list.append("TNU-" + str(i + 1))
    return usage_id_list


# TODO: need an exmaple to show the bibiliography of the taxonoic name
def usage_according_to(df2):
    """Reference to the source of this Taxonomic Name Usage or Taxonomic Name Usage Relationship
    Assertion ie. the BibliographicResource"""
    according_to = []
    for i in range(len(df2)):
        according_to.append('BIB-1')
    return according_to


def usage_taxonomicNameUsageLabel(df2, path):
    """Label for the taxonomic name usage; contains the taxonomic name and a reference to the publication
    the name has been used in. eg. TaxonomicName sec. Publication Author, year"""
    taxonomic_name_usage_label = []
    qf = get_quick_ref(path)
    for name in df2['taxonomicNameString']:
        if name[-1] == ' ':
            name = name[:-1]
        new = name + " sec " + qf
        taxonomic_name_usage_label.append(new)
    return taxonomic_name_usage_label


def usage_verbatim_NameString_verbatimRank(df2):
    length = len(df2)
    verbatim_name = []
    verbatim_rank = []
    for i in range(length):
        verbatim_name.append('')
        verbatim_rank.append('')
    return verbatim_name, verbatim_rank


def usage_taxonomicStatus(df2):
    taxonomic_status = []
    for kn in df2['kindOfName']:
        if kn == 'scientific':
            taxonomic_status.append('Accepted')
        else:
            taxonomic_status.append('')
    return taxonomic_status


# TODO: add the common name accpetedNameUsage
def usage_acceptedNameUsage(df2):
    """The currently valid (in zoology) or accepted (in botany) Taxonomic Name Usage, according to
    the author of the reference."""
    return usage_id(df2)


# TODO: find parent
def usage_hasParent(df2):
    """The TaxonomicNameUsage that is the hierachical parent for this TNU"""
    has_parent = []
    length = len(df2)
    for i in range(length):
        has_parent.append('')

    return has_parent


def usage_kindOfNameUsage(df2):
    """The kind of taxonomic name usage, e.g. primary, secondary. Needs full vocabulary. Indicates
    whether this name in this according to (source-reference) indicates the establishment (primary)
    versus application (secondary) of a name. Vocab needs to be established"""
    kind_name_usage = []
    for ele in df2['rank']:
        if ele == 'species':
            kind_name_usage.append('sp.nov.')
        elif ele == 'genus':
            kind_name_usage.append('gen.nov.')
        else:
            kind_name_usage.append('')
    return kind_name_usage


# TODO: extract the page number
def usage_microReference(df2):
    """page number"""
    page_of_target = []
    for i in range(len(df2)):
        page_of_target.append('')
    return page_of_target



def usage_etymology(df):
    """it's in tp:treatment-sec sec-type="etymology"""
    etymology = df['etymology']

    return etymology


def mapping_to_TNC_Taxonomic_name_usage(df,df2, path):
    df3 = pd.DataFrame(columns=['Id', 'taxonomicName', 'according to', 'taxonomicNameUsageLabel', 'verbatimNameString',
                                'dwc:verbatimRank', 'taxonomicStatus', 'acceptedNameUsage', 'hasParent',
                                'kindOfNameUsage',
                                'microReference', 'etymology'])
    df3['Id'] = usage_id(df2)
    df3['taxonomicName'] = usage_taxonomic_Name(df2)
    df3['according to'] = usage_according_to(df2)
    df3['taxonomicNameUsageLabel'] = usage_taxonomicNameUsageLabel(df2, path)

    df3['verbatimNameString'], df3['dwc:verbatimRank'] = usage_verbatim_NameString_verbatimRank(df2)

    df3['taxonomicStatus'] = usage_taxonomicStatus(df2)
    df3['acceptedNameUsage'] = usage_acceptedNameUsage(df2)
    df3['hasParent'] = usage_hasParent(df2)
    df3['kindOfNameUsage'] = usage_kindOfNameUsage(df2)
    df3['microReference'] = usage_microReference(df2)
    df3['etymology'] = usage_etymology(df)
    return df3


# -----------------------------------------------mapping output to TNC_Typification-------------------------------------

def mapping_to_typification(df, df2):

    i = 1
    full_name_with_author = df2['fullNameWithAuthorship']
    taxonomic_name_usage = []
    type_of_type = []
    type_name = []
    typification_string = []
    for ele1, ele2 in zip(df['holotype_and_loc_and_coor'], df['paratype_and_loc_and_coor']):


        if ele1 == '' and ele2 == '':
            taxonomic_name_usage.append('TNU-' + str(i))
            type_of_type.append('type species')
            type_name.append(full_name_with_author[i - 1])
            typification_string.append('')
        elif ele1 != '' and ele2 != '':
            taxonomic_name_usage.append('TNU-' + str(i))
            taxonomic_name_usage.append('TNU-' + str(i))
            type_of_type.append('holotype')
            type_of_type.append('paratype')
            type_name.append(full_name_with_author[i - 1])
            type_name.append(full_name_with_author[i - 1])
            typification_string.append(ele1)
            typification_string.append(ele2)
        else:
            taxonomic_name_usage.append('TNU-' + str(i))
            type_name.append(full_name_with_author[i - 1])
            if ele1 == '':
                type_of_type.append('paratype')
                typification_string.append(ele2)
            elif ele2 == '':
                type_of_type.append('holotype')
                typification_string.append(ele2)
        i += 1
    df4 = pd.DataFrame(columns=['TaxonomicNameUsage', 'typeOfType', 'typeName', 'typificationString'])
    df4['TaxonomicNameUsage']=taxonomic_name_usage
    df4['typeOfType']=type_of_type
    df4['typeName']=type_name
    df4['typificationString']=typification_string
    return df4


# -----------------------------------------------writing csv file-------------------------------------------------------
def write_csv(articleName):
    path = get_example_path(articleName)
    tree = ET.parse(path)
    root = tree.getroot()
    # generate data
    df = get_info_from_body(root)
    df2 = change_To_TNC_Taxonomic_name(df, path)
    df3 = mapping_to_TNC_Taxonomic_name_usage(df,df2, path)
    df4 = mapping_to_typification(df,df2)
    # write csv
    df2.to_csv(get_output_path(articleName.split(".")[0]))
    df3.to_csv(get_output_path("TNC_Taxonomic_name_usage"))
    df4.to_csv(get_output_path("TNC_Typification"))


if __name__ == '__main__':
    write_csv("A_new_genus_and_two_new_species_of_miniature_clingfishes.xml")
    # path = get_example_path("A_new_genus_and_two_new_species_of_miniature_clingfishes.xml")

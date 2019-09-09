from zipfile import ZipFile

import reference_new_stdds

import reader
import os

def runall(path):
    print("==========================")
    """get the current path """
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)

    """ path that stores xml files"""
    xml_path = parent_dir.replace("\\", "/") + "/Examples/xmls/"+path
    # print(xml_path)

    """ call RIE module"""
    ref_list = reference_new_stdds.get_contri_info(xml_path)
    reference_new_stdds.write_excel(ref_list)
    """ call reader module"""
    reader.write_csv(path)

    # Create a zip file
    with ZipFile(parent_dir.replace("\\", "/")+'/Output/xmlOutput/XMLOutput.zip', 'w') as zipObj:

        # # Add multiple files to the zip
        zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/TNC_Taxonomic_name_usage_XmlOutput.csv', "TNC_Taxonomic_name_usage_XmlOutput.csv")
        zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/TNC_Typification_XmlOutput.csv', "TNC_Typification_XmlOutput.csv")
        zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/{}_XmlOutput.csv'.format(path.replace(".xml","")), "{}_XmlOutput.csv".format(path.replace(".xml","")))
        zipObj.write(parent_dir.replace("\\", "/") + '/Output/xmlOutput/BibliographicResource.csv', "BibliographicResource.csv")



runall("A_new_genus_and_two_new_species_of_miniature_clingfishes.xml")


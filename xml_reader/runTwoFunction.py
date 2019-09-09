from zipfile import ZipFile

import reference_new_stdds
import reader
import os

def runall(path):
    """get the current path """
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)

    """ path that stores xml files"""
    xml_path = parent_dir.replace("\\", "/") + "/Examples/xmls/"+path
    # print(xml_path)

    """ call RIE module"""
    ref_list = reference_new_stdds.get_contri_info(xml_path)
    reference_info_extraction.write_reference_to_excel(ref_list)
    """ call reader module"""
    reader.write_csv(path)

    # Create a zip file
    with ZipFile(parent_dir.replace("\\", "/")+'/Output/xmlOutput/XMLOutput.zip', 'w') as zipObj:
        pass
        # Add multiple files to the zip
        # zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/agents.csv_XmlOutput.csv', "agents.csv")
        # zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/references.csv_XmlOutput.csv', "reference.csv")
        # zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/example_XmlOutput.csv', "readerOutput.csv")





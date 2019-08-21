from zipfile import ZipFile

import reference_info_extraction
import reader
import os


if __name__ == '__main__':
    """get the current path """
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)

    """ path that stores xml files"""
    xml_path = parent_dir.replace("\\", "/") + "/Examples/xmls/26newSpecies.xml"
    # print(xml_path)

    """ call RIE module"""
    lists, ref_list = reference_info_extraction.get_contri_info(xml_path)
    reference_info_extraction.write_reference_to_excel(lists, ref_list)
    """ call reader module"""
    reader.write_csv("26newSpecies.xml")

    # Create a ZipFile Object
    with ZipFile(parent_dir.replace("\\", "/")+'/Output/xmlOutput/sample2.zip', 'w') as zipObj2:
        # Add multiple files to the zip
        zipObj2.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/agents.csv_XmlOutput.csv')
        # zipObj2.write('test_1.log')
        # zipObj2.write('test_2.log')





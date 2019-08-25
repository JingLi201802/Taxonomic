from zipfile import ZipFile

import reference_info_extraction
import reader
import os

def runall(path):
    """get the current path """
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)

    """ path that stores xml files"""
    xml_path = parent_dir.replace("\\", "/") + "/functional_tool_2.0/uploaded_folder/"+path
    # print(xml_path)

    """ call RIE module"""
    lists, ref_list = reference_info_extraction.get_contri_info(xml_path)
    
    reference_info_extraction.write_reference_to_excel(lists, ref_list)
    """ call reader module"""
    reader.write_csv(path)

    # # Create a zip file
    # with ZipFile(parent_dir.replace("\\", "/")+'/Output/xmlOutput/XMLOutput.zip', 'w') as zipObj:
    #     # Add multiple files to the zip
    #     zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/agents.csv_XmlOutput.csv', "agents.csv")
    #     zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/references.csv_XmlOutput.csv', "reference.csv")
    #     zipObj.write(parent_dir.replace("\\", "/")+'/Output/xmlOutput/example_XmlOutput.csv', "readerOutput.csv")

#result = os.path.join(parent_dir, "functional_tool_2.0/xls_folder/{}.xls".format(name))

    # Create a zip file
    with ZipFile(parent_dir.replace("\\", "/")+'/functional_tool_2.0/csv_folder/' + path.split('.')[0] + '_XMLOutput.zip', 'w') as zipObj:
        # Add multiple files to the zip
        zipObj.write(parent_dir.replace("\\", "/")+'/functional_tool_2.0/csv_folder/agents.csv_XmlOutput.csv', "agents.csv")
        zipObj.write(parent_dir.replace("\\", "/")+'/functional_tool_2.0/csv_folder/references.csv_XmlOutput.csv', "reference.csv")
        zipObj.write(parent_dir.replace("\\", "/")+'/functional_tool_2.0/csv_folder/' + path.split('.')[0] + '_XmlOutput.csv', "TNC_TaxonomicName.csv")

    os.remove(parent_dir.replace("\\", "/")+'/functional_tool_2.0/csv_folder/agents.csv_XmlOutput.csv')
    os.remove(parent_dir.replace("\\", "/")+'/functional_tool_2.0/csv_folder/references.csv_XmlOutput.csv')
    os.remove(parent_dir.replace("\\", "/")+'/functional_tool_2.0/csv_folder/' + path.split('.')[0] + '_XmlOutput.csv')
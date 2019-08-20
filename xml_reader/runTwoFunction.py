import reference_info_extraction
# import reader
import os


if __name__ == '__main__':

    abs_file_path = os.path.abspath(__file__)

    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)

    xml_path = parent_dir.replace("\\", "/") + "/Examples/xmls/26newSpecies.xml"

    lists, ref_list = reference_info_extraction.get_contri_info(xml_path)
    print(xml_path)

    print(parent_dir)



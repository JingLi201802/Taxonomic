import reference_info_extraction
import reader
import os

if __name__ == '__main__':
    r_list = reference_info_extraction.lists
    r_ref_list = reference_info_extraction.ref_list
    abs_file_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_file_path)
    parent_dir = os.path.dirname(parent_dir)
    print(parent_dir)



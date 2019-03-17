def get_tag_dict():
    """Reads tags_config.txt and maps each of the tags to their data category label. Returns a dictionary."""
    tag_source_file = open("../tags_config.txt", 'r')
    tag_dict = {}
    for line in tag_source_file.readlines():
        if line[0] == "#" or len(line) < 5:
            continue
        target_line = line.replace("\n", "")
        target_line = target_line.replace(" ", "")
        try:
            tags, category = target_line.split("->")
        except:
            print("The config file may be formatted incorrectly, the following line could not be parsed: \n{}\n "
                  "please make sure each line is in the format a, b, c ... -> d".format(line))
            exit(0)
        for tag in tags.split(","):
            tag_dict[tag] = category
    tag_source_file.close()
    return tag_dict

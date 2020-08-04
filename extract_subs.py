import xml.etree.ElementTree as ET
import os
import math
import sys


def time_converter(time_str):
    time_str = time_str.replace(',', ':').replace('.',':').replace(' ', '')

    time_str = time_str.split(':')
    # Bugproofing
    if len(time_str) < 4:
        time_str.append('000')
    hours, mins, secs, msecs = list(time_str)
    msecs = int(msecs) + int(hours) * 3600000 + int(mins) * 60000 + int(secs) * 1000
    return msecs


def parse_subtitles(tree_root):
    """
    Extract subtitles from xml files as text
    :param tree_root: root of the xml tree
    :return: subtitles : a dictionary where key is subtitle ID and value is text and timestamps
    """
    time_start = -1
    time_end = -1
    sub_count = 0
    single_buffer = ''
    group_buffer = []
    group_id = None
    # Making a nan array to store subs
    subtitles = dict()
    for sub in tree_root:
        if sub.tag == 's':
            # Check for time start
            if sub[0].tag == 'time':
                time_start = time_converter(sub[0].attrib['value'])
                sub_count = 1
            else:
                sub_count += 1
            if sub[-1].tag == 'time':
                time_end = time_converter(sub[-1].attrib['value'])
            else:
                time_end = -1
            # Collecting subtitles
            single_buffer = ""
            for element in sub:
                if element.tag == 'w':
                    single_buffer = single_buffer + ' ' + element.text
            group_buffer.append((single_buffer, sub.attrib['id']))
            # Subtitles collected. Flush with time stamps if done
            if time_end != -1:
                duration = time_end - time_start
                fragment = math.floor(duration / sub_count)
                # print("CLEARING GROUP BUFFER")
                # print(group_buffer)
                # Assigning time fragments to subs
                stamp = time_start
                for single_sub, sub_id in group_buffer:
                    subtitles[sub_id] = (single_sub, stamp, stamp + fragment - 80)
                    stamp = stamp + fragment + 80
                group_buffer = []
                single_buffer = ''
    # Bugproofing: if last sub is not closed
    if group_buffer:
        time_end = time_start + 1000
        duration = time_end - time_start
        fragment = math.floor(duration / sub_count)
        for single_sub, sub_id in group_buffer:
            subtitles[sub_id] = (single_sub, stamp, stamp + fragment - 80)
            stamp = stamp + fragment + 80
        group_buffer = []
    return subtitles


def write_to_file(filename, subs, indices):
    """

    :param filename: name of file to write to
    :param subs: dictionary containing subtitles
    :param indices: a list of indices (str) to access subtitles from subs
    :return:
    """
    with open(filename, 'a+') as f:
        buffer = ''
        for index in indices:
            buffer = buffer + subs[index][0]
        f.write(buffer + '\n')
    return


def parse_documents(alignment_filename):
    """
    Given a file with alignments of subtitles between source and target language, produce contextualised
    sentences in .txt format of overlap of at least 0.9
    :param alignment_filename: file which contains alignment of subtitles and paths to them
    :return:
    """

    """
    Part 1: Parse alignments
    """
    align_tree = ET.parse(alignment_filename)
    collection = align_tree.getroot()
    # Identify aligned files
    for document in collection:
        if sys.argv[1] == 'server':
            path_to_xml = '../../datasets/OpenSubtitles/OpenSubtitles/xml'
            path_to_output = 'out/'
        else:
            path_to_xml = 'datasets/OpenSubtitles/xml'
            path_to_output = ''

        src_file = os.path.join(os.getcwd(), path_to_xml, document.attrib['fromDoc'][:-3])
        tgt_file = os.path.join(os.getcwd(), path_to_xml, document.attrib['toDoc'][:-3])
        print("Parsing the alignment of \n {} and \n {}...".format(src_file, tgt_file))
        cxt_src = None
        cxt_tgt = None
        cxt_id = None
        pairs_to_parse = []
        for alignment in document:
            # if it is a pair and it has the overlap of at least 0.9
            if 'overlap' in alignment.attrib.keys() and float(alignment.attrib['overlap']) > 0.9:
                src, tgt = alignment.attrib['xtargets'].split(';')
                src, tgt = src.split(), tgt.split()
                id = int(alignment.attrib['id'][2:])
                # Check for context; context sentence must exist and it must be the immediate previous sentence
                if cxt_src is not None and id == cxt_id + 1:
                    pairs_to_parse.append((src, tgt, cxt_src, cxt_tgt))
                cxt_src, cxt_tgt, cxt_id = src, tgt, id
        """
        Part 2: print context and main sentences to files
        """
        # Parse subtitles from subtitle files
        # Parse source text
        src_tree = ET.parse(src_file)
        src_root = src_tree.getroot()
        src_subtitles = parse_subtitles(src_root)
        # Parse target text
        tgt_tree = ET.parse(tgt_file)
        tgt_root = tgt_tree.getroot()
        tgt_subtitles = parse_subtitles(tgt_root)
        for pair in pairs_to_parse:
            src, tgt, cxt_src, cxt_tgt = pair
            cxt_time_end, src_time_start = src_subtitles[cxt_src[0]][2], src_subtitles[src[-1]][1]
            time_difference = src_time_start - cxt_time_end
            # Context and source sentence must be within 7 sec distance
            if time_difference < 7000:  # in milliseconds
                print(src, tgt)
                write_to_file(os.path.join(path_to_output, 'src'), src_subtitles, src)
                write_to_file(os.path.join(path_to_output, 'tgt'), tgt_subtitles, tgt)
                write_to_file(os.path.join(path_to_output, 'src.context'), src_subtitles, cxt_src)
                write_to_file(os.path.join(path_to_output, 'tgt.context'), tgt_subtitles, cxt_tgt)


if __name__ == '__main__':
    if sys.argv[1] == 'server':
        parse_documents('../../datasets/OpenSubtitles/align_en_pl.xml')
    else:
        parse_documents("datasets/align_en_pl_sample.xml")

    # print(src_subtitles[src[0]])

    # Add to files

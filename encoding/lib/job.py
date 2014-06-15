import os
import subprocess

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_mlt(talk, output_file):
    mlt = Element('mlt')
    for cut_file in talk["cut_list"]:
        producer = SubElement(mlt, 'producer', id=cut_file["filename"])
        producer_property = SubElement(producer, "property", name="resource")
        producer_property.text = cut_file["filepath"] + "/" + cut_file["filename"]

    playlist = SubElement(mlt, "playlist", id="playlist0")



    for cut_file in talk["cut_list"]:
#        print cut_file
        args = {}
        args['producer'] = cut_file['filename']
        print cut_file
        if 'in' in cut_file and cut_file['in']:
            args['in'] = str(int(cut_file['in'].total_seconds()) * 25)
            playlist_entry = SubElement(playlist, "entry", args)
        if 'out' in cut_file and cut_file['out']:
            args['out'] = str(int(cut_file['out'].total_seconds()) * 25)
            playlist_entry = SubElement(playlist, "entry", args)
        if 'in' not in cut_file and 'out' not in cut_file:
            playlist_entry = SubElement(playlist, "entry", args)

    print prettify(mlt)

    main_file = open(output_file, "w")
    main_file.write(prettify(mlt));
    main_file.close()
    #ElementTree.ElementTree(prettify(mlt)).write(output_file)


def create_title(talk, output_file):
    with open(os.devnull, 'wb') as DEVNULL:
        subprocess.Popen(["./gen_image.pl", output_file, talk["title"] + "\n" + talk["presenters"]], stderr=DEVNULL)

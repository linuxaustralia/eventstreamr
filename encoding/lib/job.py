import os
import subprocess

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom

def create_mlt(talk, output_file):
    mlt = Element('mlt')
    playlist = SubElement(mlt, "playlist", id="playlist0")
    for cut_file in talk["cut_list"]:
        producer = SubElement(mlt, 'producer', id=cut_file["filename"])
        producer_property = SubElement(producer, "property", name="resource")
        producer_property.text = cut_file["filepath"] + "/"  + cut_file["filename"]
        args = {} 
        args['producer'] = cut_file['filename']
        if 'in' in cut_file and cut_file['in']:
            args['in'] = str(int(cut_file['in'].total_seconds()) * 25)
        if 'out' in cut_file and cut_file['out']:
            args['out'] = str(int(cut_file['out'].total_seconds()) * 25)
        playlist_entry = SubElement(playlist, "entry", args)
    ElementTree.ElementTree(mlt).write(output_file)

def create_title(talk, output_file):
    with open(os.devnull, 'wb') as DEVNULL:
        subprocess.Popen(["./gen_image.pl", output_file, talk["title"] + "\n" + talk["presenters"]], stderr=DEVNULL)

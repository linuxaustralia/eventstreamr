import os
import subprocess

from lxml.etree import ElementTree, Element, SubElement

def create_mlt(talk, output_file, dv_frame_rate):
    mlt = Element('mlt')
    playlist = Element("playlist", id="playlist0")
    for cut_file in talk["cut_list"]:
        # Create the producer
        producer = SubElement(mlt, 'producer', id=cut_file["filename"])
        producer_property = SubElement(producer, "property", name="resource")
        producer_property.text = os.path.join(cut_file["filepath"],cut_file["filename"])

        # Create the playlist entry
        args = {}
        args['producer'] = cut_file['filename']
        # Check if we have any cuts, and calculate the appropriate frame
        if 'in' in cut_file and cut_file['in']:
            args['in'] = str(int(cut_file['in'].total_seconds()) * dv_frame_rate)
        if 'out' in cut_file and cut_file['out']:
            args['out'] = str(int(cut_file['out'].total_seconds()) * dv_frame_rate)
        playlist_entry = SubElement(playlist, "entry", args)

    # The playlist must be after the producers
    mlt.append(playlist)

    # Write out the tree
    ElementTree(mlt).write(output_file, pretty_print=True)

def create_title(talk, output_file):
    with open(os.devnull, 'wb') as DEVNULL:
        subprocess.Popen(["./gen_image.pl", output_file, talk["title"] + "\n" + talk["presenters"]], stderr=DEVNULL)

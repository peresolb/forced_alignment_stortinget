#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json
import nltk
import re
from raw_conversion import raw


def get_par_lines(myjson):
    """Takes as input a transcription from Google Cloud StT in the form of
    a loaded json file. Returns a list of strings with each paragraph of that
    transcription, which can be used as input to the Aeneas forced alignment tool.
    Certain features of the parliamentary proceedings transcription guidelines are
    altered with regexes to improve performence, and words marked as inaudible or
    deleted in the Språklabben transcription tool are removed."""
    returnlist = []
    replacements = [(r'([^\s]+\\)([^\s]+)', r'\2'), (r'¤', r''), (r'\*', r''), (r'([^\s]+)\- ', r'\1 '), (r'([^\s]+)\-([^\s]+)', r'(\1 \2)')]
    for par in myjson['paragraphs']:
        mydict = {}
        mydict['id'] = par['id']
        mydict['words'] = par['words']
        mydict['start'] = mydict['words'][0]['startTime']
        mydict['end'] = mydict['words'][-1]['endTime']
        purewords = [w['text'] for w in mydict['words'] if w.get('audibility') != 'INAUDIBLE' and w.get('deleted') != True]
        mystring = ' '.join(purewords)
        for p,r in replacements:
            mystring = re.sub(p, r, raw(mystring))
        mydict['string'] = mystring
        returnlist.append(mydict)
    return returnlist



if __name__ == "__main__":
    try:
        googlejsonfile = sys.argv[1]
    except IndexError:
        sys.exit("Please provide filenames: json_to_lines pygooglejsonfile")

    if not os.path.exists(googlejsonfile):
        sys.exit("Please provide a valid filename for the googlejsonfile")
    else:
        with open(googlejsonfile, 'r') as google:
            googlejson = json.load(google)

    lines = get_par_lines(googlejson)

    with open(("%s.lines.txt" % googlejsonfile), "w") as outfile:
        for l in lines:
            outfile.write("%s\n" % l['string'])
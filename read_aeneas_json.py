#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json
import nltk
import re
from json_to_lines import get_par_lines

def parse_aeneas(googledict, aeneasdict):
    """Takes as input a transcription from Google Cloud StT,
    in the form of a dictionary loaded from a json file,
    as well as the same text forcefully aligned with Aeneas,
    also in the form of a dictionary loaded from the json output
    from Aeneas. Returns a list of dictionaries, one for each
    paragraph, with 'id'=paragraph id, 'start'= start time code from
    Aeneas in nanoseconds, 'end'= end time code from Aeneas in nanoseconds"""
    paragraphs = get_par_lines(googledict)
    aeneaslist = [frag for frag in aeneasdict['fragments']]
    bil = 1000000000
    timecodelist = [{'id': paragraphs[n]['id'], 'start': int(float(aeneaslist[n]['begin'])*bil), 'end': int(float(aeneaslist[n]['end'])*bil)} for n in range(len(paragraphs))]
    return timecodelist


if __name__ == "__main__":    
    try:
        googlejson = sys.argv[1]
        aeneasjson = sys.argv[2]
    except IndexError:
        sys.exit("Please provide filenames: python read_aeneas_json.py googlejson aeneasjson")

    with open(googlejson, 'r') as google:
        googledict = json.load(google)    

    with open(aeneasjson, 'r') as aeneas:
        aeneasdict = json.load(aeneas)

    print(parse_aeneas(googledict, aeneasdict))

#!/usr/bin/env python
# coding=utf-8

import sys
import os
import json
from json_to_lines import get_par_lines
from audioread import audio_open


def get_edges(googledict, soundfile):
    """Takes as input a Google Clous StT transcription,
    in the form of a loaded json file, and the transcribed
    sound file. Registers the head and tail, i.e the time, in
    seconds, between the start of the sound file and the start
    of the speech as as recognized by the transcription, and
    the time, in seconds, between the end of the speech and the
    end of the sound file. The head and tail are printed to the terminal."""
    with audio_open(soundfile) as sf:
        duration = sf.duration
    bil = 1000000000
    paragraphs = get_par_lines(googledict)
    head = paragraphs[0]['start']/bil
    speechend = paragraphs[-1]['end']/bil
    tail = duration-speechend
    print("%s %s" % (head, tail))


if __name__ == "__main__":    
    try:
        audiofile = sys.argv[1]
        googlejson = sys.argv[2]
    except IndexError:
        sys.exit("Please provide filenames: python get_head_tail.py audiofile googlejson")

    with open(googlejson, 'r') as google:
        googledict = json.load(google)
    
    get_edges(googledict, audiofile)
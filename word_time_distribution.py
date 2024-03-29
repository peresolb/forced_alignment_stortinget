#!/usr/bin/env python
# coding=utf-8

import re
import sys
import os
import json
from raw_conversion import raw


def distribute_words(wordlist):
    """Takes a list of word tokens in the Google Cloud StT format.
    Keeps the start time code of the first token and the end time code
    of the last token, and distributes the other timecodes according to
    a syllable count heuristics."""
    returnlist = []
    start = wordlist[0]['startTime']
    end = wordlist[-1]['endTime']
    timespan = end-start
    replacements = (r'(.+)(\\.+)', r'\1')
    nuclei = re.compile(r'[aeiouyæøåAEIOUYÆØÅ¤]{1,2}')
    pairlist = []
    for word in wordlist:
        myword = re.sub(replacements[0], replacements[1], raw(word['text']))
        syllables = nuclei.findall(myword)
        if word.get('deleted') == True:
            pairlist.append((word, 0))
        else:
            score = 1
            if len(syllables) > 1:
                score += len(syllables)-1
            pairlist.append((word, score))
    syllength = sum([x[1] for x in pairlist])
    length = len(wordlist)
    average_word_length = timespan/length
    average_syll_length = timespan/syllength
    for n in range(len(pairlist)):
        token = pairlist[n][0]
        syllcount = pairlist[n][1]
        wordlength = syllcount*average_syll_length
        if n == 0:
            token['endTime'] = int(token['startTime']+wordlength)
            returnlist.append(token)
        elif n == len(wordlist)-1:
            token['startTime'] = int(returnlist[-1]['endTime'])
            returnlist.append(word)
        else:
            token['startTime'] = int(returnlist[-1]['endTime'])
            token['endTime'] = int(token['startTime']+wordlength)
            returnlist.append(token)
    return returnlist


def redistribute_words(googledict):
    """Takes as input a Google Cloud StT transcription. Returns
    a dict, compatible with Google Cloud StT and Språklabben, which corresponds to
    the Google transcriptions with the start and end timecodes from the input, but
    with the timecodes of all other words generated by the heuristics in
    word_time_distributrion.distribute words."""
    returndict = {'paragraphs': []}
    for n, par in enumerate(googledict['paragraphs']):
        mydict = {}
        mydict['id'] = par['id']
        if par.get('speaker') != None:
            mydict['speaker'] = par['speaker']
        mydict['startTime'] = par['startTime']
        mydict['words'] = par['words']
        mydict['words'][0]['startTime'] = par['words'][0]['startTime']
        mydict['words'][-1]['endTime'] = par['words'][-1]['endTime']
        mydict['words'] = distribute_words(mydict['words'])
        returndict['paragraphs'].append(mydict)
    return returndict

if __name__ == "__main__":    
    try:
        googlejson = sys.argv[1]
        outfile = sys.argv[2]
    except IndexError:
        sys.exit("Please provide filenames: python word_time_distribution.py googlejson outfile")

    with open(googlejson, 'r') as google:
        googledict = json.load(google)


    newdict = redistribute_words(googledict)

    with open(outfile, 'w') as out:
        json.dump(newdict, out, ensure_ascii=False)
#!/usr/bin/env python
# coding=utf-8

import sys
import os
import json
from json_to_lines import get_par_lines
import pandas as pd
from read_aeneas_json import parse_aeneas


def config_tester(gold_dict, basejson, expjson):
    golddata = get_par_lines(gold_dict)
#    counter = 8
#    while counter > 0:
#        dummy1 = compute_alignments(soundfile, asr_dict)
#        counter -= 1
    base = parse_aeneas(gold_dict, basejson)
    print(base)
    exp = parse_aeneas(gold_dict, expjson)
    comparisons = [(' '.join([w['text'] for w in golddata[n]['words']]), int(golddata[n]['start']), base[n]['start'], exp[n]['start'], int(golddata[n]['end']), base[n]['end'], exp[n]['end'])\
                  for n in range(len(golddata))]
    df = pd.DataFrame(comparisons, columns = ['string', 'gold_start', 'base_start', 'exp_start', 'gold_end', 'base_end', 'exp_end'])
    base_start_diff = abs(df['gold_start']-df['base_start'])/1000000000
    exp_start_diff = abs(df['gold_start']-df['exp_start'])/1000000000
    base_end_diff = abs(df['gold_end']-df['base_end'])/1000000000
    exp_end_diff = abs(df['gold_end']-df['exp_end'])/1000000000
    diffs = pd.concat([df['string'], base_start_diff-exp_start_diff, base_end_diff-exp_end_diff], axis=1)
    diffs.columns = ['string', 'start: base_divergence-exp_divergence', 'End: base_divergence-exp_divergence']
    print(diffs)
    def FA_accuracy(startdiff, enddiff):
        edgecount = len(startdiff)+len(enddiff) 
        print(edgecount)
        positives = len([x for x in startdiff if x < 0.02])+len([x for x in enddiff if x <= 0.02])
        print(positives)
        accuracy = (positives*100)/edgecount
        return accuracy
    base_accuracy = FA_accuracy(base_start_diff, base_end_diff)
    exp_accuracy = FA_accuracy(exp_start_diff, exp_end_diff)
    base_sum = sum(base_start_diff+base_end_diff)
    exp_sum = sum(exp_start_diff+exp_end_diff)
    print("base accuracy:%s\nexp accuracy:%s\nbase sum: %s\nexp sum: %s" % (base_accuracy, exp_accuracy, base_sum, exp_sum))
    




if __name__ == "__main__":
    try:
        goldfile = sys.argv[1]
        basefile = sys.argv[2]
        expfile = sys.argv[3]
    except IndexError:
        sys.exit("Please provide filenames: python test_FA.py goldfile basefile expfile")

    with open(goldfile, 'r') as gold:
        golddict = json.load(gold)
    
    with open(basefile, 'r') as base:
        basedict = json.load(base)
    
    with open(expfile, 'r') as exp:
        expdict = json.load(exp)

config_tester(golddict, basedict, expdict)
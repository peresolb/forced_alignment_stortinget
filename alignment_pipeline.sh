#!/bin/bash
if test $# -ne 2
then
echo "Usage:$0 <date> <id>"
exit
fi
date=$1
id=$2
audiofile=audio/${date}.flac

echo "Downloading transcript:"
curl -X GET   https://api-dot-spraklabben.appspot.com/transcripts/${id}/paragraphs   -H 'Content-Type: application/json'   -H 'Postman-Token: 2ae3e85b-519a-42ce-b42a-dc0dcd8e223f'   -H 'cache-control: no-cache' --user Ohi4V7ctCCfXicc6XjHQ1T1PFDq1:c3cccf8d276d9f4736f7e48961eec1a401b2883c8ee214dcd499a45c4af05407 > intermediary/GET_${date}_$(/bin/date +%Y-%m-%d).json

transcription=intermediary/GET_${date}_$(/bin/date +%Y-%m-%d).json
copy $transcription non-aligned

echo "Finding head and tail of audio file"
head_tail=$(python get_head_tail.py tmp/${date}.flac $transcription)
head=$(echo $head_tail | grep  -oP "^\d*\.\d*")
tail=$(echo $head_tail | grep  -oP "\d*\.\d*$")

echo "Converting transcription to lines"
python json_to_lines.py $transcription
lines=$transcription.lines.txt

echo "Running forced alignment"
python -m aeneas.tools.execute_task $audiofile $lines -r="mfcc_window_length=0.15|mfcc_window_shift=0.05|mfcc_size=25" "task_language=nor|is_text_type=plain|os_task_file_format=json|is_audio_file_head_length=$head|is_audio_file_tail_length=$tail|task_adjust_boundary_algorithm=beforenext|task_adjust_boundary_beforenext_value=0.050" intermediary/AENEAS_${date}_$(/bin/date +%Y-%m-%d).json

aeneas=intermediary/AENEAS_${date}_$(/bin/date +%Y-%m-%d).json

echo "Creating New aligned transcription"
python align.py $transcription $aeneas aligned/ALIGNED__${date}_$(/bin/date +%Y-%m-%d).json
new_transcription=aligned/ALIGNED__${date}_$(/bin/date +%Y-%m-%d).json

echo "Pushing aligned transcription to Språklabben"
curl -X PUT   https://api-dot-spraklabben.appspot.com/transcripts/${id}/paragraphs   -H 'Content-Type: application/json'   -H 'Postman-Token: 5e8937eb-9f2d-4af4-8d53-9ccc073fb8a2'   -H 'cache-control: no-cache' --user Ohi4V7ctCCfXicc6XjHQ1T1PFDq1:c3cccf8d276d9f4736f7e48961eec1a401b2883c8ee214dcd499a45c4af05407   --data-binary "@${new_transcription}"
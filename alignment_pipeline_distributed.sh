#!/bin/bash
if test $# -ne 2
then
    echo "Usage:$0 <date> <id>"
    exit
fi
date=$1
id=$2
now=$(/bin/date +%Y-%m-%d-%H-%M)
audiofile=audio/${date}.flac
if [ ! -e $audiofile ]
then
    echo "audiofile not found"
    exit
fi

key=$(cat key.txt)

echo "Downloading transcript:"
curl -X GET   https://api-dot-spraklabben.appspot.com/transcripts/${id}/paragraphs   -H 'Content-Type: application/json'   -H 'Postman-Token: 2ae3e85b-519a-42ce-b42a-dc0dcd8e223f'   -H 'cache-control: no-cache' --user $key > intermediary/GET_${date}_${now}.json

transcription=intermediary/GET_${date}_${now}.json

cp $transcription archive/GET_${date}_${now}.json

if [ -e $transcription ]
then
    cp $transcription non-aligned
else
    echo "Transcription not found"
    exit
fi

echo "Finding head and tail of audio file"
head_tail=$(python get_head_tail.py $audiofile $transcription)
head=$(echo $head_tail | grep  -oP "^\d*\.\d*")
tail=$(echo $head_tail | grep  -oP "\d*\.\d*$")
echo "head: $head; tail: $tail"

echo "Converting transcription to lines"
python json_to_lines.py $transcription
lines=$transcription.lines.txt

cp $lines archive/GET_${date}_${now}.json.lines.txt

echo "Running forced alignment"
#if multilevel
#python -m aeneas.tools.execute_task $audiofile $lines -r="mfcc_window_length=0.15|mfcc_window_shift=0.05|mfcc_size=25" "task_language=nor|is_text_type=mplain|os_task_file_format=json|is_audio_file_head_length=$head|is_audio_file_tail_length=$tail|task_adjust_boundary_algorithm=beforenext|task_adjust_boundary_beforenext_value=0.050" intermediary/AENEAS_${date}_${now}.json
#sentence only
python -m aeneas.tools.execute_task $audiofile $lines \
-r="mfcc_window_length=0.15|mfcc_window_shift=0.05|mfcc_size=25" \
"task_language=nor|is_text_type=plain|os_task_file_format=json|is_audio_file_head_length=$head|is_audio_file_tail_length=$tail|task_adjust_boundary_algorithm=beforenext|task_adjust_boundary_beforenext_value=0.050" \
intermediary/AENEAS_${date}_${now}.json

aeneas=intermediary/AENEAS_${date}_${now}.json

cp $aeneas archive/AENEAS_${date}_${now}.json

if [ -e $aeneas ]
then
    echo "Creating sent-aligned transcription"
    python align.py $transcription $aeneas intermediary/SENT_ALIGNED_${date}_${now}.json
    new_transcription=intermediary/SENT_ALIGNED_${date}_${now}.json
else
    echo "Alignmentfile not found"
    exit
fi

if [ -e $new_transcription ]
then
    echo "Splitting audiofile"
    python chopper.py $new_transcription $audiofile 
else
    echo "Transcription not found"
    exit
fi

slices=$(ls intermediary | grep -Po "(?<=SENT_ALIGNED_${date}_${now}.json.lines.)\d*_\d*" | sort)
filelist=''

for elem in $slices
do
    audioslice=intermediary/SENT_ALIGNED_${date}_${now}.json.sound.${elem}.flac
    lineslice=intermediary/SENT_ALIGNED_${date}_${now}.json.lines.${elem}.txt
    if [ -e $audioslice ] && [ -e $lineslice ]
    then
        echo "Running forced alignment on $audioslice"
        python -m aeneas.tools.execute_task $audioslice $lineslice -r="mfcc_window_length=0.15|mfcc_window_shift=0.05|mfcc_size=25" \
        "task_language=nor|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=beforenext|task_adjust_boundary_beforenext_value=0.050" \
        intermediary/WORD_ALIGNED_${date}_${now}_${elem}_aeneas.json
        currentfile=intermediary/WORD_ALIGNED_${date}_${now}_${elem}_aeneas.json
        if [ -e $currentfile ]
        then
            filelist+="$currentfile,"
        else
            echo "Fail at $currentfile"
            exit
        fi
    else
        echo "$audioslice or $lineslice does not exist"
        exit
    fi
done

echo "Creating word-aligned transcription"
python merge_transcriptions.py $new_transcription $filelist aligned/WORD_ALIGNED_${date}_${now}.json

word_aligned=aligned/WORD_ALIGNED_${date}_${now}.json

if [ -e $word_aligned ]
then
    cp $word_aligned archive/
    python view_diffs.py $new_transcription $word_aligned | more
    #echo "Pushing aligned transcription to Språklabben"
    #curl -X PUT   https://api-dot-spraklabben.appspot.com/transcripts/${id}/paragraphs   -H 'Content-Type: application/json'   -H 'Postman-Token: 5e8937eb-9f2d-4af4-8d53-9ccc073fb8a2'   -H 'cache-control: no-cache' --user $key   --data-binary "@${new_transcription}" > curl_output/PUT_word_aligned_${date}_${now}.json
else
    echo "$word_aligned does not exist"
    exit
fi
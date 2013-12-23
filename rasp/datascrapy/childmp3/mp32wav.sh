#!/usr/bin/env bash
# mp3 to wav

mkdir -pv wav
for mp3 in mp3/*.mp3
do
	oldname=${mp3##*/}
	newname=wav/${oldname%.*}.wav
	echo "convert: " $mp3 '->' $newname
	mpg123 -m -q -w $newname $mp3
done

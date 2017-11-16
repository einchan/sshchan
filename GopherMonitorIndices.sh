#!/bin/bash

inotifywait -m -r -q --format '%w%f' -e modify boards | while read FILE
do
	echo "changes in $FILE"
	python3 ConvertToGopher.py $FILE
done

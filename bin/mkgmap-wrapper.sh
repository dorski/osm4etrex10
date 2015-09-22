#!/bin/sh

MKGMAP_JARFILE=./lib/mkgmap/mkgmap.jar

nice -n19 java \
	-Xms1024M \
	-Dlog.config=./lib/mkgmap_log.props \
	-jar ${MKGMAP_JARFILE} \
	-c ./share/mkgmap.config \
	$1 \
	./share/typfiles/73280000.txt
	#--report-style-stats \ # only for a special snapshot

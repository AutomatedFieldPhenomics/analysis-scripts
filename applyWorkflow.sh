#!/bin/bash

# applyWorkflow - A script to apply an image processing workflow on an image set

usage() 
{
	echo "usage: applyWorkflow [[[-d directory] [-p workflow] [-i outdir] [-t imgType]] | [-h]]"
}

##### Main

# Set default values of variables
directory=.
workflow=workflow.py
outdir=.
imgType=png

# Get arguments
while [ "$1" != "" ]; do
	case $1 in
		-d | --directory )	shift
					directory=$1
					;;
		-p | --workflow ) 	shift
					workflow=$1
					;;
	 	-i | --outdir )		shift
					outdir=$1
					;;
		-h | --help )		usage
					exit
					;;
		-t | --type )		shift
					imgType=$1
					;;
		* )			usage
					exit 1
	esac
	shift
done

for f in $directory/*.$imgType; do
	$workflow -i $f -r $f.json -o $outdir 	
done

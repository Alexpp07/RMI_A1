#!/bin/bash

challenge="1"
host="localhost"
robname="theAgent"
pos="0"
outfile="solution"

while getopts "c:h:r:p:f:" op
do
    case $op in
        "c")
            challenge=$OPTARG
            ;;
        "h")
            host=$OPTARG
            ;;
        "r")
            robname=$OPTARG
            ;;
        "p")
            pos=$OPTARG
            ;;
        "f")
            outfile=$OPTARG
            ;;
        default)
            echo "ERROR in parameters"
            ;;
    esac
done

shift $(($OPTIND-1))

case $challenge in
    1)
        # how to call agent for challenge 1
        python3 ciber_Rato_Tools/pClientC1/mainRob.py -h "$host" -p "$pos" -r "$robname"
        ;;
    2)
        # how to call agent for challenge 2
        python3 ciber_Rato_Tools/pClientC2/mainRob2.py -h "$host" -p "$pos" -r "$robname" -f "$outfile"
        mv $outfile $outfile.map             # if needed
        ;;
    3)
        # how to call agent for challenge 3
        python3 ciber_Rato_Tools/pClientC2/mainRob3.py -h "$host" -p "$pos" -r "$robname" -f "$outfile"
        mv $outfile $outfile.map           # if needed
        ;;
esac

#!/usr/bin/bash


# Name: Chris Armour
# License: GPL-3
# Lincense URL: https://www.gnu.org/licenses/gpl-3.0.en.html
# The script will take a range of IP address octet and run a nmap scan on them



 
CIDR=192.168.0
STARTOCTET=''
ENDOCTET=''


# Get the script arguments
while getopts C:c:S:s:E:e:O:o: flag
do
    case "${flag}" in
    	C) CIDR=${OPTARG};;
    	c) CIDR=${OPTARG};;
    	S) STARTOCTET=${OPTARG};;
    	s) STARTOCTET=${OPTARG};;
    	E) ENDOCTET=${OPTARG};;
    	e) ENDOCTET=${OPTARG};;
        O) filename=${OPTARG};;
        o) filename=${OPTARG};;
    esac
done
 
# Check if Filename args was not set through args
if [ -z "$filename" ]; then
    echo "No output file specified. Use -O or -o followed by the file name to set the output file."
    exit 1
fi

# Check if start Octet was not set through args
if [ -z "$STARTOCTET" ]; then
  echo "Please enter the starting octet..."
  read STARTOCTET
fi
 
# Check if End Octet was not set through args
if [ -z "$ENDOCTET" ]; then
  echo "Please enter the ending octet..."
  read ENDOCTET
fi

# Check if start Octet is not a number
[ -n "$STARTOCTET" ] && [ $STARTOCTET -ge 0 ] && [ $STARTOCTET -le 255 ] && [ "$STARTOCTET" -eq "$STARTOCTET" ] 2>/dev/null
if [ $? -ne 0 ]; then
   echo $STARTOCTET is not a valid number
   exit 1
fi
 
# check if End Octet is not a number and out of range
[ -n "$ENDOCTET" ] && [ $ENDOCTET -ge 0 ] && [ $ENDOCTET -le 255 ] && [ "$ENDOCTET" -eq "$ENDOCTET" ] 2>/dev/null
if [ $? -ne 0 ]; then
   echo $ENDOCTET is not a valid number
   exit 1
fi
 
# Check if End Octet is less than Start Octet
if (( $ENDOCTET < $STARTOCTET)); 
then
    echo "Start octect must be earlier than ending octet"
    exit 1
fi

# Define timestamp function
function timestamp() {
    date --utc +"%Y-%M-%d %H:%M:%S UTC" # current time UTC
}
# Run Nmap scan for each IP address within range
for i in $(seq $STARTOCTET $ENDOCTET)
do
    echo "scanning $CIDR.$i"
    
    #Structure output file
    echo -e "\nTimestamp: $(timestamp)" >> $filename
    echo "IP address: $CIDR.$i" >> $filename
    echo "PORT     STATE SERVICE" >> $filename
    nmap -Pn -F $CIDR.$i | grep open >> $filename
    
    # Check grep output status
    if [ $? -ne 0 ]; then
   	echo "No open ports" >> $filename
    fi
done


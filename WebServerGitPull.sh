#!/usr/local/bin/bash
set -e
set -o pipefail

if [[ $# -eq 0 ]] ; then
    echo "Repository Not Specified, Script Terminated!"
    exit 1
fi

if [ -z "$1" ]
  then
    echo "Repository Not Specified, Script Terminated!"
    exit 1
fi

if [ -z "$2" ]
  then
    echo "File Path Not Specified, Script Terminated!"
    exit 1
fi

GitHubRepoDirectory=$2
Repository=$1

printf "\nRepository Name: ${Repository}"
printf "\nRepository Full Path: ${GitHubRepoDirectory}\n\n"

cd "${GitHubRepoDirectory}"
git reset --hard
git pull --verbose

cd "${GitHubRepoDirectory}"
printf "\n#### Setting Permissions ####\n\n"
chmod -Rvv ug=rwx,o=rx .

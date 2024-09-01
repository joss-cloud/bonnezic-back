#!/bin/bash

find /home/web/mouvize.com/_text2mp3 -mtime +1 -exec rm {} \;
short_server_name="bonnezic"
bck_mysql_folder="/home/bonnezic/backup/mysql/"
bck_file_folder="/home/bonnezic/backup/"
server_backup="backup.dirigeable.eu"
path_config="/home/bonnezic/config/backup/"

prg_name=$(basename -- "$0")
prg_name="${prg_name%.*}"
prg_folder=$(dirname $(readlink -f $0))"/"
yyyymmdd_hhmmss=$(date "+%Y")$(date "+%m")$(date "+%d")'_'$(date "+%H")$(date "+%M")$(date "+%S")

my_lib=$prg_folder$prg_name"_lib.sh"
my_backup_zip="/backup_"$short_server_name"_"$yyyymmdd_hhmmss".zip"

. $my_lib
fnct_backup_crontab
fnct_backup_mysql
fnct_make_backup_zip
fnct_backup_copy_to_server


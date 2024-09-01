#!/bin/bash

MYSQLDUMP="$(which mysqldump)"
path_config="/home/bonnezic/config/backup/"
prg_name="backup"
short_server_name="bonnezic"
db_host="localhost"
filao_usr_file=$path_config"filao_usr_file.cnf"
db_list=$path_config"/db_list.txt"

bck_mysql_folder="/home/bonnezic/backup/mysql/"

for mydb in $(cat $db_list)
do
	my_bd=$bck_mysql_folder"bonnezic_"$mydb"*.sql"
	file_to_be_removed=$(ls -ltr $my_bd|sed '1d'| awk -F" " '{print $9}')
	echo "remove : "$file_to_be_removed
	rm $file_to_be_removed
done

for my_db in $(cat $db_list)
do
	my_datetime_oneline=$(date "+%Y")$(date "+%m")$(date "+%d")'_'$(date "+%H")$(date "+%M")$(date "+%S")
	FILE=$bck_mysql_folder$short_server_name"_"$my_db"_"$my_datetime_oneline".sql"
	echo "dump db my_db to FILE : "$FILE
	my_cmd="$MYSQLDUMP --defaults-extra-file=$filao_usr_file -h $db_host --routines -B -F  --delete-source-logs $my_db > $FILE"
	echo $my_cmd
	echo "*********************"
	$MYSQLDUMP --defaults-extra-file=$filao_usr_file -h $db_host --routines -B -F  --delete-source-logs $my_db > $FILE
	echo "*********************"
done	

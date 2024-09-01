#!/bin/bash

bck_mysql_folder="/home/bonnezic/backup/mysql/"
bck_file_folder="/home/bonnezic/backup/"
path_config="/home/bonnezic/config/backup/"
filao_usr_file=$path_config"filao_usr_file.cnf"
dbname="bobine"
tableName1="film"
tableName2="imdb"
tableName3="event"

MYSQLDUMP="$(which mysqldump)"
FILE=$bck_mysql_folder$tableName1".sql"
$MYSQLDUMP --defaults-extra-file=$filao_usr_file $dbname $tableName1 >$FILE
FILE=$bck_mysql_folder$tableName2".sql"
$MYSQLDUMP --defaults-extra-file=$filao_usr_file $dbname $tableName2 >$FILE
FILE=$bck_mysql_folder$tableName3".sql"
$MYSQLDUMP --defaults-extra-file=$filao_usr_file $dbname $tableName3 >$FILE

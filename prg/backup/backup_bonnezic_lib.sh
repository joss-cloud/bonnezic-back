#!/bin/bash

	function fnct_backup_mysql
	{
		MYSQLDUMP="$(which mysqldump)"
		path_config="/home/bonnezic/config/backup/"
		db_host="localhost"
		filao_usr_file=$path_config"filao_usr_file.cnf"
		db_list=$path_config"/db_list.txt"

		for mydb in $(cat $db_list)
		do
			my_bd=$bck_mysql_folder$short_server_name"_"$mydb"*.sql"
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
	}

	function fnct_backup_crontab {
		path_backup_crontab=$bck_file_folder
		my_crontab=$path_backup_crontab$short_server_name"_crontab.txt"
		crontab -l > $my_crontab
	}
	
function fnct_make_backup_zip {
    # Vérifiez si la variable path_config est définie
    if [ -z "$path_config" ]; then
        echo "La variable path_config n'est pas définie."
        exit 1
    fi

    files_list="${path_config}/backup_files_list.txt"
    exclude_list="${path_config}/backup_exclude_folders.txt"

    if [ -f "$files_list" ]; then
        echo "$files_list exists"
    else
        echo "$files_list does not exist"
        exit 1
    fi

    # Initialiser la liste des fichiers à zipper
    to_be_zip=()

    # Lire le fichier files_list et ajouter chaque fichier à la liste des fichiers à zipper
    while IFS= read -r my_file; do
        to_be_zip+=("$my_file")
    done < "$files_list"

    # Initialiser la liste des dossiers à exclure
    exclude_args=()

    # Vérifiez l'existence du fichier exclude_list
    if [ -f "$exclude_list" ]; then
        # Lire le fichier exclude_list et ajouter chaque dossier à la liste des dossiers à exclure
        while IFS= read -r my_file; do
            exclude_args+=("-x")
            exclude_args+=("$my_file")
        done < "$exclude_list"
    else
        echo "$exclude_list does not exist, no folders will be excluded."
    fi

    # Créer le nom du fichier de sauvegarde zip
    my_backup_zip="/backup_${short_server_name}_${yyyymmdd_hhmmss}.zip"

    # Supprimer les fichiers zip existants dans le répertoire racine
    rm -f /*.zip

    # Afficher les fichiers à zipper et les dossiers à exclure pour vérification
    echo "Fichiers à zipper : ${to_be_zip[@]}"
    echo "Dossiers et fichiers à exclure : ${exclude_args[@]}"

    # Construire la commande zip avec les fichiers à zipper et les exclusions
    zip_command=("zip" "-r" "$my_backup_zip")
    for file in "${to_be_zip[@]}"; do
        zip_command+=("$file")
    done
    for exclude in "${exclude_args[@]}"; do
        zip_command+=("$exclude")
    done

    # Afficher la commande à exécuter pour vérification
    echo "Commande exécutée :"
    echo "${zip_command[@]}"

    # read -p "Press any key to resume ..."

    # Exécuter la commande zip
    "${zip_command[@]}"
}







	
	function fnct_backup_copy_to_server
	{
		scp -v -o StrictHostKeyChecking=no $my_backup_zip root@$server_backup:/home/backup/$short_server_name/
		export errorlevel=$?
		if [ 0 != $errorlevel ]
		then
			echo "error scp"
			exit 1
		fi
	}

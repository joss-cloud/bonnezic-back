import os
import glob
import subprocess

# Fonction pour trouver le fichier bobine*.sql le plus récent
def find_latest_backup(directory):
    list_of_files = glob.glob(os.path.join(directory, 'bonnezic_bobine*.sql'))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

# Fonction pour modifier le fichier de sauvegarde
def modify_backup_file(original_file, new_db_name):
    with open(original_file, 'r') as file:
        filedata = file.read()

    # Remplacer les occurrences de `CREATE DATABASE` et `USE`
    filedata = filedata.replace('CREATE DATABASE', f'-- CREATE DATABASE')
    filedata = filedata.replace('USE `bobine`', f'USE `{new_db_name}`')

    modified_file = f"/tmp/modified_{os.path.basename(original_file)}"
    with open(modified_file, 'w') as file:
        file.write(filedata)

    return modified_file

# Fonction pour restaurer la base de données
def restore_database(backup_file, config_file, new_db_name):
    # Commande pour vérifier si la base de données existe
    check_db_cmd = f"mysql --defaults-extra-file={config_file} -e 'USE {new_db_name}'"
    db_exists = subprocess.call(check_db_cmd, shell=True)

    # Si la base de données n'existe pas, la créer
    if db_exists != 0:
        create_db_cmd = f"mysql --defaults-extra-file={config_file} -e 'CREATE DATABASE {new_db_name}'"
        subprocess.call(create_db_cmd, shell=True)

    # Modifier le fichier de sauvegarde
    modified_backup_file = modify_backup_file(backup_file, new_db_name)

    # Commande pour restaurer la base de données
    restore_cmd = f"mysql --defaults-extra-file={config_file} {new_db_name} < {modified_backup_file}"
    subprocess.call(restore_cmd, shell=True)

    # Supprimer le fichier de sauvegarde modifié
    os.remove(modified_backup_file)

# Répertoire de sauvegarde
backup_directory = "/home/bonnezic/backup/mysql"
# Fichier de configuration MySQL
mysql_config_file = "/home/bonnezic/config/backup/bobine_usr_file.cnf"  
# Nom de la nouvelle base de données
new_database_name = "bobine_dev"

# Trouver le fichier de sauvegarde le plus récent
latest_backup_file = find_latest_backup(backup_directory)

if latest_backup_file:
    print(f"Le fichier de sauvegarde le plus récent est : {latest_backup_file}")
    # Restaurer la base de données
    restore_database(latest_backup_file, mysql_config_file, new_database_name)
    print(f"La base de données {new_database_name} a été restaurée avec succès.")
else:
    print("Aucun fichier de sauvegarde trouvé.")

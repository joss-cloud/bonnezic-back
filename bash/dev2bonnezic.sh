#!/bin/bash

root_folder="/home/web/bonnezic.com"
source_folder="/home/web/bonnezic.com/dev"
target_folder="/home/web/bonnezic.com/prod"
owner="root"
exclude_paths=(".git" ".gitignore")

# Convertir les chemins exclus en un format compatible avec la commande find
exclude_find_expr=""
for path in "${exclude_paths[@]}"; do
    exclude_find_expr="$exclude_find_expr -path '$target_folder/$path' -prune -o"
done

# Commande pour supprimer les fichiers
find_command="find '$target_folder' -mindepth 1 $exclude_find_expr -type f -exec rm -f {} \;"
echo "Running command to delete files: $find_command"
eval $find_command

# Commande pour supprimer les répertoires
find_command="find '$target_folder' -mindepth 1 $exclude_find_expr -type d -exec rm -rf {} \;"
echo "Running command to delete directories: $find_command"
eval $find_command

# Commande pour supprimer les liens symboliques
find_command="find '$target_folder' -mindepth 1 $exclude_find_expr -type l -exec rm -f {} \;"
echo "Running command to delete symbolic links: $find_command"
eval $find_command

cp -r $source_folder/_css/ $target_folder/_css/
cp -r $source_folder/_js/ $target_folder/_js/
cp -r $source_folder/_php/ $target_folder/_php/
cp $source_folder/index.php $target_folder/
cp $source_folder/rien.gif $target_folder/
cp $source_folder/*.ico $target_folder/

cd $target_folder
ln -s $root_folder/img img
ln -s $root_folder/img_music img_music
ln -s $root_folder/album album
ln -s $root_folder/images images
ln -s $root_folder/images_square images_square
ln -s $root_folder/_zic _zic
ln -s $root_folder/_zic_new _zic_new
ln -s $root_folder/last_tracks.json last_tracks.json
ln -s $root_folder/last_tracks_new.json last_tracks_new.json
ln -s $root_folder/denyhosts-master.zip denyhosts-master.zip


chown -R $owner $target_folder
setfacl -m g:root:rwX -R $target_folder
setfacl -m u:$owner:rwX -R $target_folder
setfacl -m u:www-data:rX -R $target_folder






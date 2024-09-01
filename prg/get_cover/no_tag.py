from mutagen.id3 import ID3, ID3NoHeaderError
from pathlib import Path
import os, time
import eyed3

arr_err = []
with open('no_tag.txt', "r") as file:
    flines = [line.strip() for line in file.readlines()]

for mp3_file in flines:
    try:
        mp3_name = Path(mp3_file).stem
        if mp3_name.count("-") == 0:
            print(f"/:\\ No dash. Impossible to modify mp3 tag {mp3_file}")
            arr_err.append(mp3_file)
            continue
            
        if mp3_name.count("-") > 1:
            print(f"/:\\ too many dash. Impossible to modify mp3 tag {mp3_file}")
            arr_err.append(mp3_file)
            continue
            
        mp3_name_arr = mp3_name.split("-")
        artist_name = mp3_name_arr[0].strip()
        title_name = mp3_name_arr[1].strip()

        try:
            audio_file = eyed3.load(mp3_file)
            if audio_file is None:
                raise ValueError(f"Erreur : Impossible de charger le fichier MP3 {mp3_file}")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier MP3 {mp3_file}: {e}")
            arr_err.append(mp3_file)
            continue
        
        print(f"Modification : {artist_name} - {title_name}")
        try:
            audio_file.tag.artist = artist_name
            audio_file.tag.title = title_name
            audio_file.tag.save()
        except Exception as e:
            print(f"Erreur lors de la modification des tags pour {mp3_file}: {e}")
            arr_err.append(mp3_file)

    except Exception as e:
        print(f"Erreur inattendue pour le fichier {mp3_file}: {e}")
        arr_err.append(mp3_file)

with open("err_tag.txt", "w") as opfile:
    opfile.write("\n".join(arr_err))

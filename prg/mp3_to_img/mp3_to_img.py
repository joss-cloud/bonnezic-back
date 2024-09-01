from mutagen.id3 import ID3, ID3NoHeaderError, APIC
import os, glob
from pathlib import Path

# Chemins des dossiers et du fichier MP3
mp3_folder = r'/home/zic'
img_folder = "/home/web/img_music"
glob_path = f"{mp3_folder}/**/*.*"

folder_mp3=r'/home/zic/RapFunk/'
my_mp3='New Jersey Kings - Get Organized.mp3'
mp3_file=f"{folder_mp3}{my_mp3}"
print(f"mp3_file : {mp3_file}")
mp3_name = Path(mp3_file).stem
img_file = os.path.join(img_folder, mp3_name + ".jpeg")

try:
    audio = ID3(mp3_file)
    if 'APIC:' in audio:
        artwork = audio['APIC:'].data
        with open(img_file, 'wb') as img:
            img.write(artwork)
            print(f"Image enregistrée sous : {img_file}")
    else:
        print(f"{mp3_name} : Aucune image trouvée dans les tags ID3.")
except ID3NoHeaderError:
    print(f"Le fichier {mp3_file} n'a pas de tags ID3.")
except Exception as e:
    print(f"Erreur inattendue lors de la lecture des tags ID3 pour {mp3_file}: {e}")


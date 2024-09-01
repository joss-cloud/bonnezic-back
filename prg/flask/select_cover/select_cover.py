from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os,time
import shutil
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import eyed3

app = Flask(__name__)

# Chemins
mp3_folder = r'/home/zic'
album_folder = "/home/web/bonnezic.com/album"
img_tmp_folder = "/opt/bonnezic/prg/flask/select_cover/tmp"
discogs_token = 'sjckMNAunqfQScJKLOGoOFWRDeYBFMuCKuhJZTBm'

# Charger la liste des fichiers au démarrage
with open('no_album.txt', 'r') as file:
    files_to_process = [line.strip() for line in file.readlines()]

# Fonction pour servir les images à partir du dossier temporaire
@app.route('/tmp/<path:filename>')
def serve_image(filename):
    return send_from_directory(img_tmp_folder, filename)

def getmp3Tags(mp3_file):
    mp3_file = mp3_file.encode('utf-8').decode('utf-8')
    if os.path.isfile(mp3_file):
        audio_file = eyed3.load(mp3_file)
        if audio_file is None or audio_file.tag is None:
            return "no artist", "no title", "no album"
        return audio_file.tag.artist, audio_file.tag.title, audio_file.tag.album
    else:
        return "no artist", "no title", "no album"

        
def get_discogs_cover_art(artist, album, title):
    # Construire une requête de recherche plus précise
    query = f"{artist} {album}" if album else f"{artist} {title}"
    search_url = f"https://api.discogs.com/database/search?q={query}&token={discogs_token}"
    
    print(f"Requête envoyée à Discogs: {search_url}")  # Debugging: pour voir la requête utilisée
    response = requests.get(search_url)
    image_urls = []

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            for result in data['results']:
                image_url = result.get('cover_image')
                if image_url and "spacer.gif" not in image_url:
                    image_urls.append(image_url)
        return image_urls
    else:
        print(f"Erreur lors de la requête Discogs: {response.status_code}, Message: {response.text}")
        return []


def download_discogs_images(image_urls, mp3_name):
    temp_folder = os.path.join(img_tmp_folder, mp3_name)
    os.makedirs(temp_folder, exist_ok=True)
    image_paths = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.discogs.com/'
    }

    for index, image_url in enumerate(image_urls):
        time.sleep(1)  # Ajoute un délai de 1 seconde entre les requêtes
        for _ in range(3):  # Réessayer jusqu'à 3 fois en cas d'erreur 429
            response = requests.get(image_url, headers=headers)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                if width >= 400 and height >= 400:
                    save_name = f"{mp3_name}_discogs_{index}.jpg"
                    save_path = os.path.join(temp_folder, save_name)
                    img.save(save_path)
                    image_paths.append(save_name)
                else:
                    print(f"Image too small: {image_url}")
                break  # Quitter la boucle si la requête a réussi
            elif response.status_code == 429:
                print("Trop de requêtes envoyées. Nouvelle tentative après un délai.")
                time.sleep(2)  # Attendre 2 secondes avant de réessayer
            else:
                print(f"Erreur lors du téléchargement de l'image: {response.status_code}")
                break
    print(f"Téléchargement terminé pour {mp3_name}")
    return image_paths



@app.route('/')
def index():
    print("Accès à la page d'accueil")
    if files_to_process:
        first_mp3_name = Path(files_to_process[0]).stem
        print(f"Redirection vers le premier fichier: {first_mp3_name}")
        return redirect(url_for('select_cover', mp3_name=first_mp3_name))
    else:
        return "Aucun fichier à traiter."

@app.route('/select_cover/<mp3_name>', methods=['GET'])
def select_cover(mp3_name):
    # Chercher le chemin complet du fichier MP3 dans files_to_process
    mp3_path = next((file for file in files_to_process if Path(file).stem == mp3_name), None)

    if mp3_path is None:
        print(f"Chemin introuvable pour {mp3_name}")
        return "Chemin introuvable.", 404

    # Extraire les tags ID3
    artist, title, album = getmp3Tags(mp3_path)

    # Obtenir les images depuis Discogs en utilisant l'artiste, l'album et le titre
    image_urls = get_discogs_cover_art(artist, album, title)
    if not image_urls:
        print(f"Aucun résultat pour {mp3_name}. Passage au fichier suivant.")
        return save_cover_skip(mp3_name)
    
    # Télécharger les images en utilisant le nom de base du fichier MP3
    image_files = download_discogs_images(image_urls, mp3_name)
    
    # Rendre la page avec les informations de l'artiste, titre, album
    return render_template('select_cover.html', mp3_name=mp3_name, images=image_files, artist=artist, title=title, album=album)



@app.route('/save_cover', methods=['POST'])
def save_cover():
    try:
        selected_image = request.form['selected_image']
        mp3_name = request.form['mp3_name']
        print(f"Sauvegarde de l'image sélectionnée pour: {mp3_name}")

        final_image_path = os.path.join(album_folder, f"{mp3_name}.jpg")
        full_image_path = os.path.join(img_tmp_folder, mp3_name, selected_image)
        square_img(full_image_path)

        shutil.copy(full_image_path, final_image_path)

        temp_folder = os.path.join(img_tmp_folder, mp3_name)
        shutil.rmtree(temp_folder)

        # Supprimer la ligne du fichier no_album.txt
        remove_line_from_file(mp3_name)

        # Passer au fichier suivant
        files_to_process.pop(0)

        if files_to_process:
            next_mp3_name = Path(files_to_process[0]).stem
            print(f"Redirection vers le fichier suivant: {next_mp3_name}")
            return redirect(url_for('select_cover', mp3_name=next_mp3_name))
        else:
            print("Tous les fichiers ont été traités.")
            return "Tous les fichiers ont été traités."  # Ou rediriger vers l'accueil

    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'image: {e}")
        return f"Une erreur est survenue lors de l'enregistrement de l'image: {str(e)}", 500

def remove_line_from_file(mp3_name):
    try:
        with open('no_album.txt', 'r') as file:
            lines = file.readlines()

        # Construire la nouvelle liste sans la ligne correspondant à mp3_name
        new_lines = [line for line in lines if Path(line.strip()).stem != mp3_name]

        with open('no_album.txt', 'w') as file:
            file.writelines(new_lines)
        print(f"Ligne supprimée pour {mp3_name} dans no_album.txt")

    except Exception as e:
        print(f"Erreur lors de la suppression de la ligne du fichier: {e}")


def square_img(image_path):
    try:
        # Open the image located at image_path
        with Image.open(image_path) as img:
            width, height = img.size
            # Check if the image is not square and significantly different in dimensions
            print(f"{image_path} : {width}x{height}")
            if width != height and (width > height * 1.05 or height > width * 1.05):
                crop_image_to_square(image_path)
            else:
                print("image square")
    except IOError as e:
        print(f"Error opening image {image_path}: {e}")


def crop_image_to_square(image_to_be_cropped):
    print(f"/!\\ crop_image_to_square : {image_to_be_cropped}")
    img_name = Path(image_to_be_cropped).stem
    img_file_squared = os.path.join(album_folder, f"{img_name}.jpg")  # Utiliser album_folder ou un autre dossier approprié

    try:
        with Image.open(image_to_be_cropped) as img:
            width, height = img.size
            print(f"crop_image_to_square {image_to_be_cropped} : {width}x{height} to {img_file_squared}")
            if width > height:
                # Crop width so the final width = height
                px_to_crop = (width - height) / 2
                left = px_to_crop
                right = width - px_to_crop
                top = 0
                bottom = height
            elif width < height:
                # Crop height so the final height = width
                px_to_crop = (height - width) / 2
                left = 0
                right = width
                top = px_to_crop
                bottom = height - px_to_crop
            print(f"crop image to {img_file_squared} : {left}, {top}, {right}, {bottom}")
            im1 = img.crop((left, top, right, bottom))
            # Corrected save method with subsampling set to '2' (4:2:0)
            im1.save(img_file_squared, format='JPEG', quality=95, subsampling=2)
    except IOError as e:
        print(f"Error cropping image {image_to_be_cropped} : {e}")



    except IOError as e:
        print(f"Error cropping image {image_to_be_cropped} : {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

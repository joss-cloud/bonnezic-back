import requests
import re, os,time
import os.path,glob
from pathlib import Path
from PIL import Image
from io import BytesIO

# Chemins des dossiers et du fichier MP3
mp3_folder = r'/home/zic'
img_folder = "/home/web/img_music"
glob_path = f"{mp3_folder}/**/*.*"

token = "mawBiuJZXWtOVnycgbwXJDEsJaYbBgRYLMdkypvM"

def search_image(mp3_file):
    mp3_name = Path(mp3_file).stem
    img_file = os.path.join(img_folder, mp3_name + ".jpeg")
    save_name = mp3_name + ".jpeg"
    search_url = f"https://api.discogs.com/database/search?q={mp3_name}&token={token}"
    response = requests.get(search_url)
    image_urls=[]
    largest_image_url=""
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            for result in data['results']:
                print(f"Titre: {result['title']}, URL de l'image: {result.get('cover_image')}")
                image_urls.append(result.get('cover_image'))
        largest_image_url = find_largest_image(image_urls)
    else:
        print(f"Erreur lors de la requête: {response.status_code}, Message: {response.text}")
        
    print(f"Titre: {mp3_name}, URL de l'image: {largest_image_url}")  
    if largest_image_url != None and largest_image_url !="":
        download_image(largest_image_url, img_folder, save_name)


def get_image_dimensions_web(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Ceci lèvera une exception si la requête a échoué
        
        # Charger l'image à partir de la réponse
        image = Image.open(BytesIO(response.content))
        
        # Obtenir les dimensions
        width, height = image.size
        print(f"Dimensions de l'image : {width}x{height}")
    except requests.HTTPError as http_err:
        print(f"Erreur HTTP lors du téléchargement de l'image : {http_err}")
    except Exception as err:
        print(f"Erreur lors de l'obtention des dimensions de l'image : {err}")

def get_local_image_dimensions(image_path):
    try:
        # Ouvrir l'image située à image_path
        with Image.open(image_path) as img:
            width, height = img.size
            # print(f"Dimensions de l'image : {width}x{height}")
    except IOError as e:
        print(f"Erreur lors de l'ouverture de l'image : {e}")
        width=0
        height=0
    return width,height

def download_image(image_url, save_directory, save_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    time.sleep(3)
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        save_path = os.path.join(save_directory, save_name)
        # with open(save_path, 'wb') as image_file:
            # image_file.write(response.content)
        print(f"L'image a été téléchargée et sauvegardée sous : {save_path}")
    else:
        print(f"Erreur lors du téléchargement de l'image. Code de statut HTTP : {response.status_code}")


def extract_dimensions_from_url(url):
    match = re.search(r'/h:(\d+)/w:(\d+)', url)
    if match:
        return int(match.group(1)), int(match.group(2))  # Retourne hauteur, largeur
    else:
        return None, None

def find_largest_image(image_urls):
    max_area = 0
    largest_image_url = None
    
    for url in image_urls:
        height, width = extract_dimensions_from_url(url)
        if height and width:
            area = height * width
            if area > max_area:
                max_area = area
                largest_image_url = url
                
    return largest_image_url

nb_file=0
for mp3_file in glob.glob(glob_path, recursive=True):
    # print(f"mp3_file : {mp3_file}")
    mp3_name = Path(mp3_file).stem
    img_file = os.path.join(img_folder, mp3_name + ".jpeg")

    if os.path.isfile(img_file) == False:
        #nb_tiret= img_file.find("-")
        nb_tiret=img_file.count("-")
        if nb_tiret>1:        
            print(f"mp3_file : {mp3_file} ")
            nb_file+=1
        # img_file_arr=img_file.split("-")
        # if (img_file
        # print(f"{img_file_arr[0]}")
print(f"nb_file {nb_file}")
# print(f"nb_ko {nb_ko} nb_ok {nb_ok} cover_discogs {cover_discogs} no_cover_discogs {no_cover_discogs}")
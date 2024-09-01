from mutagen.id3 import ID3, ID3NoHeaderError, APIC
from pathlib import Path
import os, time, glob, re, logging, sys
import requests
from io import BytesIO
from PIL import Image
import eyed3
import urllib.parse
import datetime

# Variable globale pour le token Spotify
spotify_access_token = None

# Listes pour stocker les résultats
no_tag = []
no_album = []
no_cover = []
img_too_small = []

def get_spotify_access_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

def getmp3Tags(mp3_file):
    mp3_file = mp3_file.encode('utf-8').decode('utf-8')
    print(f"getmp3Tags mp3_file : {mp3_file}")
    if os.path.isfile(mp3_file):
        print(f"{mp3_file} exists")
        audio_file = eyed3.load(mp3_file)
        if audio_file is None:
            print(f"Erreur : Impossible de charger le fichier MP3 {mp3_file}")
            return "no artist", "no title", "no album"
        if audio_file.tag is None:
            print(f"Erreur : Aucune balise ID3 trouvée dans le fichier MP3 {mp3_file}")
            return "no artist", "no title", "no album"
        
        artist = audio_file.tag.artist.strip() if audio_file.tag.artist else "no artist"
        title = audio_file.tag.title.strip() if audio_file.tag.title else "no title"
        album = audio_file.tag.album.strip() if audio_file.tag.album else "no album"
        
        print("Artist: {}".format(artist))
        print("Album: {}".format(album))
        print("Track: {}".format(title))
        return artist, title, album
    else:
        print(f" file {mp3_file} does not exist ")
        print(f"Absolute path: {os.path.abspath(mp3_file)}")
        return "no artist", "no title", "no album"



def download_image(image_url, save_directory, save_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    time.sleep(3)
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        save_path = os.path.join(save_directory, save_name)
        try:
            with open(save_path, 'wb') as image_file:
                image_file.write(response.content)
                print(f"L'image a été téléchargée et sauvegardée sous : {save_path}")
                verify_and_resize_image(save_path)
            return save_path
        except OSError as e:
            print(f"Erreur lors de l'écriture de l'image sur le disque : {e}")
            return None
    else:
        print(f"Erreur lors du téléchargement de l'image. Code de statut HTTP : {response.status_code}")
        return None

def verify_and_resize_image(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            print(f"Dimensions originales de l'image : {width}x{height}")

            if width < 400 or height < 400:
                print("L'image est trop petite (moins de 400x400 pixels).")
                os.remove(image_path)
                return False
            
            square_img(image_path)
            return True
    except IOError as e:
        print(f"Erreur lors du traitement de l'image : {e}")
        return False

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
    img_file_squared = img_square_folder + img_name + ".jpg"
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

def get_deezer_album(artist_name, album_name, title_name, mp3_file):
    base_url = "https://api.deezer.com/search/album"
    
    # Construction de la chaîne de requête
    query = f'artist:"{artist_name}" album"{album_name}"'
    logging.info("Deezer query %s", query)
    
    encoded_query = urllib.parse.quote(query)
    # encoded_query = encoded_query.replace('%3A', '%253A').replace('%22', '%2522').replace('%20', '%2520')
    
    # Construction de l'URL finale
    url = f"{base_url}?q={encoded_query}"
    
    # Effectuer la requête
    response = requests.get(url)
    
    print(f"Requête envoyée : {response.url}")  # Log de l'URL
    print(f"Statut de la réponse : {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            album_info = data['data'][0]
            try:
                album_cover = album_info['cover_big']  # URL de la couverture en grande taille
                logging.info("Deezer album url : %s", album_cover)
                return album_cover
            except Exception as e:
                print(f"Erreur lors de la récupération du nom de l'album avec Deezer. {e}")
                logging.info("Deezer - Erreur lors de la récupération du nom de l'album %s", e)
                return None
        else:
            logging.info("Deezer album non trouvé")
            print(data)
    else:
        print(f"Erreur de requête: Status Code {response.status_code}")
        logging.info("Deezer - Erreur lors de la récupération du nom l'album %s", response.status_code)
        return None


        
def get_spotify_cover_art(artist_name, album_name, title_name, mp3_file):
    global spotify_access_token
    
    mp3_name = Path(mp3_file).stem
    img_file = mp3_name + ".jpg"
    
    def search_spotify(query, search_type):
        search_url = 'https://api.spotify.com/v1/search'
        search_params = {
            'q': query,
            'type': search_type,
        }
        headers = {
            'Authorization': f'Bearer {spotify_access_token}',
        }
        logging.info("Spotify - query %s",query)
        response = requests.get(search_url, headers=headers, params=search_params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Spotify - Erreur Spotify API : {response.status_code} - {response.text}")
            logging.info("Spotify - Erreur Spotify API : %s - %s",response.status_code,response.text)
            return None

    # Recherche par album
    query = f'artist:{artist_name} album:{album_name}'
    search_response_data = search_spotify(query, 'album')

    if search_response_data and search_response_data['albums']['items']:
        # Prenez la première réponse
        first_album = search_response_data['albums']['items'][0]
        album_cover = first_album['images'][0]['url'] if first_album['images'] else None
        logging.info("Spotify - album url : %s",album_cover)
        return album_cover
    else:
        # Si aucun album n'est trouvé, recherche par titre
        query = f'artist:{artist_name} track:{title_name}'
        search_response_data = search_spotify(query, 'track')

        if search_response_data and search_response_data['tracks']['items']:
            first_track = search_response_data['tracks']['items'][0]
            album_cover = first_track['album']['images'][0]['url'] if first_track['album']['images'] else None
            logging.info("Spotify - album url : %s",album_cover)
            return album_cover
        else:
            print("Spotify - Aucun album ou titre trouvé pour cet artiste.")
            logging.info("Spotify - titre non trouvé")
            return None

def get_discogs_cover_art(mp3_file):
    token = "sjckMNAunqfQScJKLOGoOFWRDeYBFMuCKuhJZTBm"
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
               # print(f"Titre: {result['title']}, URL de l'image: {result.get('cover_image')}")
                image_urls.append(result.get('cover_image'))
        largest_image_url = find_largest_image(image_urls)
        return largest_image_url
    else:
        print(f"Erreur lors de la requête: {response.status_code}, Message: {response.text}")
        return None
        
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

def process_image_search(artist_name, album_name, title_name, mp3_file, img_file,index,total_files):
    # Priorité à Deezer
    logging.info("%s/%s Traitement de %s",index,total_files,mp3_file)
    album_cover = get_deezer_album(artist_name, album_name, title_name,mp3_file)
    
    if album_cover:
        print(f"Image trouvée sur Deezer : {album_cover}")
        image_path = download_image(album_cover, album_folder, img_file)
        if image_path and verify_and_resize_image(image_path):
            return True
    
    # Si Deezer ne trouve pas ou échoue, on passe à Spotify
    album_cover = get_spotify_cover_art(artist_name, album_name, title_name, img_file)
    
    if album_cover:
        print(f"Image trouvée sur Spotify : {album_cover}")
        image_path = download_image(album_cover, album_folder, img_file)
        if image_path and verify_and_resize_image(image_path):
            return True
    
    # Si Spotify ne trouve pas ou échoue, on passe à Discogs    
    # album_cover = get_discogs_cover_art(mp3_file)
    
    # if album_cover:
        # print(f"Image trouvée sur discogs : {album_cover}")
        # image_path = download_image(album_cover, album_folder, img_file)
        # if image_path and verify_and_resize_image(image_path):
            # return True

    print(f"Image non trouvée pour {mp3_file}")
    logging.info("Image non trouvée pour %s",mp3_file)
    return False


def fnct_no_cover(my_txt):
    print("fnct_no_cover")
    with open("no_cover.txt", "a") as opfile:
        opfile.write(my_txt+"\n")

# Variables globales
mp3_folder = r'/home/zic'
album_folder="/home/web/bonnezic.com/album"
img_folder = "/home/web/bonnezic.com/img_music"
glob_path = f"{mp3_folder}/**/*.*"
client_id = '866acb59006f4f40a819bfcdf42ef953'
client_secret = '4a3366f26aed4193b53a3711e9be21c1'
deezer_id="475522"
deezer_secret="2686bdedde68f0ce0b7d5ecaab58a4be"
spotify_access_token = get_spotify_access_token(client_id, client_secret)

absolute_path = os.path.abspath(__file__)
current_path = os.path.dirname(absolute_path)
prg_name = os.path.basename(__file__).replace(".py", "")
now = datetime.datetime.now()
yyyymmdd_hhmmss = now.strftime("%Y%m%d_%H%M%S")
log_dir = "/opt/bonnezic/prg/get_cover"
log_file = f"{log_dir}/{prg_name}_{yyyymmdd_hhmmss}.log"

logging.basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,  # Initial logging level
    # stream=sys.stdout,
    filename=log_file
)

logger = logging.getLogger()
logger.info('Started')

with open('no_cover.txt', "r") as file:
    covered_files = {os.path.normpath(line.split(';')[0].strip()) for line in file.readlines()}

with open('no_album.txt', "r") as file:
    flines = [line.strip() for line in file.readlines()]

# Récupérer la liste de tous les fichiers correspondant au glob_path
all_files = glob.glob(glob_path, recursive=True)

# Nombre total de fichiers
total_files = len(all_files)
# for mp3_file in flines:
for index, mp3_file in enumerate(all_files, start=1):
    normalized_mp3_file = os.path.normpath(os.path.abspath(mp3_file))
    img_square_folder = "/home/web/bonnezic.com/album"
    mp3_name = Path(mp3_file).stem
    print("")
    print("**************************************************")
    print(f"tmt {index}/{total_files} {mp3_name}")
    logging.debug("Traitement %s/%s %s",index,total_files,mp3_name)
    img_file_full = os.path.join(album_folder, mp3_name + ".jpg")
    if os.path.isfile(img_file_full):
        print(f"{img_file_full} exists")
        logging.debug("%s exists",img_file_full)
        continue
    
    if normalized_mp3_file in covered_files:
        print(f"{mp3_file} is already in cover.txt, skipping...")
        logging.debug("%s is already in cover.txt, skipping...",mp3_file)
        continue
    print(f"{mp3_file} not in no_cover.txt")
    print(f"{img_file_full} does not exist")

    artist_mp3, title_mp3, album_mp3 = getmp3Tags(mp3_file)
    if artist_mp3 in [None, 'no artist', 'None']:
        no_tag.append(mp3_file)
        logging.info("%s No Tag Artist",mp3_file)
        continue
    if title_mp3 in [None, 'no title', 'None']:
        logging.info("%s No Tag Title",mp3_file)
        no_tag.append(mp3_file)
        continue
    if album_mp3 in [None, 'no album', 'None']:
        logging.info("%s No Tag Album",mp3_file)
        no_album.append(mp3_file)
        album_mp3="None"
        # continue
    

    # Recherche d'image via Deezer puis Spotify
    if not process_image_search(artist_mp3, album_mp3, title_mp3, mp3_file, img_file_full,index,total_files):
        my_txt=f"{mp3_file};{artist_mp3};{title_mp3};{album_mp3}"
        fnct_no_cover(my_txt)
        no_cover.append(mp3_file)
        # user_input = input("Do you want to continue? (yes/no): ")


with open("no_tag.txt", "w") as opfile:
    opfile.write("\n".join(no_tag))

    
print("********************************************************************************")
print(f"Traitement terminé")
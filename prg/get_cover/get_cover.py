import requests
from mutagen.id3 import ID3, ID3NoHeaderError, APIC
from pathlib import Path
import re, os,time
import os.path,glob
import requests
from io import BytesIO
from PIL import Image
import imghdr
import eyed3

# def getEyeD3Tags(mp3_file,access_token):
    # audio_file = eyed3.load(mp3_file)
    # if audio_file.tag is None:
        # print("No ID3 tag found")
        # return

    # print("")
    # print("***************************************************************")
    # print(mp3_file)
    # album_name=audio_file.tag.album
    # artist_name=audio_file.tag.artist
    # print(f"{artist_name} - {album_name}")
    # if album_name is not None and album_name!='no title' and album_name!='None':
        # print("Artist: {}".format(audio_file.tag.artist))
        # print("Album: {}".format(audio_file.tag.album))
        # print("Track: {}".format(audio_file.tag.title))
        # print("Track Length: {}".format(audio_file.info.time_secs))  # Assuming we want the length in seconds
        # print("Release Year: {}".format(audio_file.tag.getBestDate().year if audio_file.tag.getBestDate() else "Unknown"))
        # get_spotify_cover_art(artist_name,album_name,access_token,mp3_file)
    # else:
         # .append(mp3_file)
        # print("Nnone")

def getmp3Tags(mp3_file):
    mp3_file = mp3_file.encode('utf-8').decode('utf-8')
    print(f"getmp3Tags mp3_file : {mp3_file}")
    if os.path.isfile(mp3_file) == True:
        print(f"{mp3_file} exists")
        audio_file = eyed3.load(mp3_file)
        if audio_file.tag is None:
            return "no artist","no title","no album"
        print("Artist: {}".format(audio_file.tag.artist))
        print("Album: {}".format(audio_file.tag.album))
        print("Track: {}".format(audio_file.tag.title))
        return audio_file.tag.artist,audio_file.tag.title,audio_file.tag.album
    else:
        print(f" file {mp3_file} does not exist ")
        print(f"Absolute path: {os.path.abspath(mp3_file)}")
        return "no artist","no title","no album"


    
def get_spotify_access_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

def get_spotify_cover_art(artist_name,album_name,access_token,mp3_file):
    global img_missing
    mp3_name = Path(mp3_file).stem
    img_file = mp3_name + ".jpeg"
    img_full_file = os.path.join(img_folder, img_file)
    
    search_url = 'https://api.spotify.com/v1/search'
    search_params = {
        'q': f'artist:{artist_name} album:{album_name}',
        'type': 'album',
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    search_response = requests.get(search_url, headers=headers, params=search_params)
    search_response_data = search_response.json()
    albums = search_response_data['albums']['items']
    if albums:
        # Prend le premier album trouvé
        first_album = albums[0]
        largest_image = get_largest_image(first_album['images'])
        if largest_image:
            cover_url=largest_image['url']
            print(f"L'URL de l'image la plus grande est : {cover_url} {largest_image['height']}")
            download_image(cover_url, img_folder, img_file)
        else:
            print("Aucune image trouvée pour cet album.")
            no_cover.append(mp3_file)
    else:
        print("Aucun album trouvé pour cet artiste et cet album.")
        no_cover.append(mp3_file)

  
def get_local_image_dimensions(image_path):
    try:
        # Ouvrir l'image située à image_path
        with Image.open(image_path) as img:
            width, height = img.size
            # print(f"Dimensions de l'image : {width}x{height}")
    except IOError as e:
        print(f"Erreur lors de l'ouverture de l'image : {e}")
        height=0
    return height 

def get_deezer_album(artist_name, album_name, title_name):
    search_url = "https://api.deezer.com/search/album"
    params = {
        "q": f"artist:\"{artist_name}\" album:\"{album_name}\""
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            # Obtenez le premier résultat d'album
            album_info = data['data'][0]
            album_cover = album_info['cover_big']  # URL de la couverture en grande taille
            artist_info = album_info['artist']['name']  # Nom de l'artiste
            return album_cover
        else:
            print("Aucun résultat trouvé pour cet album.")
            return "ko"
    else:
        print(f"Erreur de requête: Status Code {response.status_code}")
        return "ko"
        

def get_deezer_cover_art(artist_name, title, mp3_file):
    mp3_name = Path(mp3_file).stem
    img_file = mp3_name + ".jpeg"
    search_url = "https://api.deezer.com/search"
    params = {
        "q": f"artist:\"{artist_name}\" track:\"{title}\"",
    }
    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        results = response.json()
        if results['data']:
            for track in results['data']:
                # Informations sur la piste
                artist = track['artist']['name']
                track_title = track['title']
                album_title = track['album']['title']
                # URL de la couverture de l'album
                cover_url = track['album']['cover_big']  # 'cover_big' peut être remplacé par 'cover' pour une image plus petite

                print(f"Artiste: {artist}, Titre: {track_title}, Album: {album_title}, Couverture: {cover_url},img_folder : {img_folder}, img_file : {img_file}")
                result_cover_size=fnct_check_cover_size(cover_url,img_file)
                if result_cover_size=="ok":
                    dwl_result=download_image(cover_url, img_folder, img_file)
                    if dwl_result=="ok":
                        print(f"download {img_file} ok")
                        break
                    else:
                        print(f"download {img_file} ko")
        else:
            print(f"deezer - {artist_name}, {title} Aucun résultat trouvé.")
    else:
        print(f"Erreur lors de la requête: {response.status_code}")
   
def fnct_check_cover_size(image_url,img_file):        
    print(f"get_image_dimensions_web({image_url})")
    img_w,img_h = get_image_dimensions_web(image_url)
    print(f"{img_file} {img_w}x{img_h}")
    if img_h<400 or img_w<400:
        result="ko"
        print(f"{img_file} {img_w}x{img_h} trop petite")
    else:
        result="ok"
    return result
    
def url_album_size_check(image_url):
    print(f"url_album_size_check : {image_url}")
    width=0
    height=0
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Ceci lèvera une exception si la requête a échoué
        
        # Vérifier si la réponse est une image
        image_format = imghdr.what(None, response.content)
        if image_format is None:
            print("Le contenu téléchargé n'est pas une image.")
            return 0, 0
        
        # Charger l'image à partir de la réponse
        image = Image.open(BytesIO(response.content))
        
        # Obtenir les dimensions
        width, height = image.size
        print(f"Dimensions de l'image : {width}x{height}")
        if width<400 or height<400:
            return "ko"
        else:
            return "ok"
    except requests.HTTPError as http_err:
        print(f"Erreur HTTP lors du téléchargement de l'image : {http_err}")
        return "ko"
    except Exception as err:
        print(f"Erreur lors de l'obtention des dimensions de l'image : {err}")
        return "ko"
    
        
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
        except OSError as e:
            # Gestion des erreurs d'écriture de fichier
            print(f"Erreur lors de l'écriture de l'image sur le disque : {e}")
            return "ko"
        return "ok"
    else:
        print(f"Erreur lors du téléchargement de l'image. Code de statut HTTP : {response.status_code}")
        return "ko"

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

def image_resize(image_path_to_be_resized):
    img_name = Path(image_path_to_be_resized).stem
    img_file_squared = img_square_folder + img_name + ".jpg"
    try:
        with Image.open(image_path_to_be_resized) as img:
            width, height = img.size
            # Resize the image if its width is greater than 600
            if width > 600:
                print(f"image_resize to {img_file_squared} 600x600")
                img_resized = img.resize((600, 600), Image.LANCZOS)
                img_resized.save(img_file_squared, format='JPEG', quality=95, subsampling=2)

    except IOError as e:
        print(f"Error resizing image {image_path_to_be_resized}: {e}")

def crop_image_to_square(image_to_be_cropped):
    print(f"crop_image_to_square : {image_to_be_cropped}")
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

    
    
mp3_folder = r'/home/zic'
album_folder="/home/web/bonnezic.com/album"
img_folder = "/home/web/bonnezic.com/img_music"
glob_path = f"{mp3_folder}/**/*.*"
nb_ko=0
img_too_small=[]
no_cover=[]
no_tag=[]
no_album=[]

client_id = '866acb59006f4f40a819bfcdf42ef953'
client_secret = '4a3366f26aed4193b53a3711e9be21c1'

access_token = get_spotify_access_token(client_id, client_secret)


# mp3_file="/home/zic/JazzWorld/Ray Baretto - Descarga La Moderna.mp3"
# mp3_name = Path(mp3_file).stem
# mp3_name_arr=mp3_name.split("-")
# Artist=mp3_name_arr[0].strip()
# Title=mp3_name_arr[1].strip()
# print(f"{Artist} {Title}")
# get_spotify_cover_art(Artist, Title,access_token,mp3_file)
file = open('missing_cover.txt', "r")
# utiliser readlines pour lire toutes les lignes du fichier
# La variable "lignes" est une liste contenant toutes les lignes du fichier
flines = file.readlines()
# fermez le fichier après avoir lu les lignes
file.close()


    
flines = [line.strip() for line in flines]
for mp3_file in glob.glob(glob_path, recursive=True):  
# for mp3_file in flines:
    img_square_folder="/home/web/bonnezic.com/album"
    print(f"mp3_file : {mp3_file}")
    mp3_name = Path(mp3_file).stem
    #album search
    img_file_full = os.path.join(album_folder, mp3_name + ".jpg")
    img_file = mp3_name + ".jpg"
    if os.path.isfile(img_file_full) == True:
        print(f"{img_file_full} exists")
        continue
    else:
        print(f"{img_file_full} does not exists")
    artist_mp3,title_mp3,album_mp3=getmp3Tags(mp3_file)
    if artist_mp3 is None or artist_mp3=='no artist' or artist_mp3=='None':
        no_tag.append(mp3_file)
        continue
    if title_mp3 is None or title_mp3=='no title' or title_mp3=='None':
        no_tag.append(mp3_file)
        continue
    if album_mp3 is None and album_mp3=='no album' and album_mp3=='None':
        no_album.append(mp3_file)
        continue
    url_album=get_deezer_album(artist_mp3,album_mp3,title_mp3)
    if url_album=="ko":
        no_album.append(mp3_file)
        continue
    if url_album_size_check(url_album)=="ko":
        no_album.append(mp3_file)
        continue
    if download_image(url_album, album_folder, img_file)=="ko":
        no_album.append(mp3_file)
        continue 
    square_img(img_file_full)
    
    
    # image_resize(img_file_full)
    
    
with open("no_album.txt", "w") as opfile:
    opfile.write("\n".join(no_album))
    
with open("no_tag.txt", "w") as opfile:
    opfile.write("\n".join(no_tag))
        #### print(img_file)
    # time.sleep(1)
    # nb_ko+=1
        # nb_tiret=img_file.count("-")
        # if nb_tiret>0: 
            # mp3_name_arr=mp3_name.split("-")
            # Artist=mp3_name_arr[0].strip()
            # Title=mp3_name_arr[1].strip()
            # print(" ")
            # print(f"{mp3_file}") 
            # cover_art_url = get_spotify_cover_art(Artist, Title,access_token,mp3_file)
            # print(f"cover_art_url : {cover_art_url}")
            
            ### search_title_on_deezer(Artist, Title,mp3_file)
            ### search_title_on_lastfm(Artist, Title,mp3_file)
            ### search_image_discogs(Artist, Title,mp3_file)
            ###search_release_musicbrainz(Artist, Title,mp3_file)
            
            

# print(f"nb_ko : {nb_ko}  ")
# print("\n")
# print(*img_too_small, sep = "\n")
# print("\n")
# print(*no_cover, sep = "\n")
# print("\n")
# print(*no_tag, sep = "\n")
# print("\n")
# print("NO ALbum")
# print(*no_album, sep = "\n")
# with open("missing_cover.txt", "w") as opfile:
    # opfile.write("\n".join(img_too_small))
    # opfile.write("\n")
    # opfile.write("\n".join(no_cover))
    # opfile.write("\n")
    # opfile.write("\n".join(no_tag))
    # opfile.write("\n")
    # opfile.write("\n".join(no_album))
print("********************************************************************************")
print(f"nb_ko : {nb_ko}  ")




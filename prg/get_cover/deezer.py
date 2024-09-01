import urllib.parse
import requests

def get_deezer_title(artist_name, title_name):
    base_url = "https://api.deezer.com/search"
    query = f'artist:"{artist_name}" track:"{title_name}"'
    encoded_query = urllib.parse.quote(query)
    params = {
        "q": encoded_query
    }
    
    response = requests.get(base_url, params=params)
    print(f"Requête envoyée : {response.url}")  # Log de l'URL
    print(f"Statut de la réponse : {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            track_info = data['data'][0]
            album_info = track_info.get('album')
            try:
                album_cover = album_info['cover_big']  # URL de la couverture en grande taille
                # logging.info("Deezer album url : %s",album_cover)
                return album_cover
            except Exception as e:
                print(f"Erreur lors de la récupération du nom de l'album avec Deezer. {e}")
                # logging.error("Deezer - Erreur lors de la récupération du nom de l'album %s", e)
                return None
        else:
            print(f"Aucun album trouvé pour {artist_name} - {title_name} sur Deezer.")
            return None
    else:
        print(f"Erreur de requête Deezer: Status Code {response.status_code}")
        return None

def get_deezer_album(artist_name, album_name):
    base_url = "https://api.deezer.com/search/album"
    query = f'artist:"{artist_name}" album"{album_name}"'
    encoded_query = urllib.parse.quote(query)
    params = {
        "q": encoded_query
    }
    
    response = requests.get(base_url, params=params)
    print(f"Requête envoyée : {response.url}")  # Log de l'URL
    print(f"Statut de la réponse : {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
                # Obtenez le premier résultat d'album
                album_info = data['data'][0]
                try:
                    album_cover = album_info['cover_big']  # URL de la couverture en grande taille
                    # logging.info("Deezer album url : %s",album_cover)
                    return album_cover
                except Exception as e:
                    print(f"Erreur lors de la récupération du nom de l'album avec Deezer. {e}")
                    #logging.info("Deezer - Erreur lors de la récupération du nom de l'album %s", e)
                    return None
        else:
            print("Deezer album non trouvé")
            return None

# album_cover_url = get_deezer_title("Francesco De Masi", "The Stranger Lady")
album_cover_url = get_deezer_album("Super Preachers", "Stereophonic Sometimes")
print(album_cover_url)

import urllib.parse
import requests
import logging, os
import configparser

# Spotify credentials
config = configparser.ConfigParser()
config_file_path = "/opt/bonnezic/pwd/spotify"

if os.path.exists(config_file_path):
    config.read(config_file_path)
    client_id = config.get("SPOTIFY", "client_id")
    client_secret = config.get("SPOTIFY", "client_secret")

else:
    raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

if not client_id or not client_secret:
    raise ValueError(
        "Spotify client ID and secret must be set in the configuration file."
    )


def get_spotify_access_token(client_id, client_secret):
    """Obtient un jeton d'accès Spotify."""
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        auth_url,
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=10,
    )

    if auth_response.status_code != 200:
        logging.error("Failed to get Spotify access token: %s", auth_response.json())
        return None

    auth_response_data = auth_response.json()
    return auth_response_data["access_token"]


def search_spotify_track(access_token, artist_name, track_name):
    """Effectue une recherche de piste sur Spotify."""
    base_url = "https://api.spotify.com/v1/search"
    query = f"artist:{artist_name} track:{track_name}"
    logging.info("Spotify query: %s", query)
    encoded_query = urllib.parse.quote(query)

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "q": encoded_query,
        "type": "track",
    }

    response = requests.get(base_url, headers=headers, params=params, timeout=10)

    if response.status_code == 200:
        logging.info("Requête envoyée : %s", response.url)
        logging.info("Statut de la réponse : %s", response.status_code)
        return response.json()
    else:
        logging.error(
            "Erreur lors de la requête Spotify: %s - %s",
            response.status_code,
            response.text,
        )
        return None


def search_spotify_album(access_token, artist_name, album_name):
    """Effectue une recherche de piste sur Spotify."""
    base_url = "https://api.spotify.com/v1/search"
    query = f"artist:{artist_name} album:{album_name}"
    logging.info("Spotify query: %s", query)
    encoded_query = urllib.parse.quote(query)

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {"q": encoded_query, "type": "album"}

    response = requests.get(base_url, headers=headers, params=params, timeout=10)

    if response.status_code == 200:
        logging.info("Requête envoyée : %s", response.url)
        logging.info("Statut de la réponse : %s", response.status_code)
        return response.json()
    else:
        logging.error(
            "Erreur lors de la requête Spotify: %s - %s",
            response.status_code,
            response.text,
        )
        return None


def main():
    # Obtenir le jeton d'accès Spotify
    access_token = get_spotify_access_token(client_id, client_secret)
    if not access_token:
        logging.error("Spotify access token could not be retrieved. Exiting.")
        return

    # Effectuer la recherche
    artist_name = "Thelonious Monk"
    track_name = "Tea For Two - Bonus"
    album_name = "Criss-Cross"

    # response_data = search_spotify_track(access_token, artist_name, track_name)
    response_data = search_spotify_album(access_token, artist_name, album_name)

    if response_data:
        logging.info("Réponse Spotify : %s", response_data)
        # Examiner la réponse pour voir ce que l'API a renvoyé
        if response_data["albums"]["items"]:
            album_info = response_data["albums"]["items"][0]
            try:
                album_cover = album_info["images"][0]["url"]
                logging.info("Spotify album url : %s", album_cover)
                print(album_cover)
            except Exception as e:
                logging.error(
                    "Erreur lors de la récupération du nom de l'album avec Spotify. %s",
                    e,
                )
                return None
        else:
            logging.info("Aucun résultat trouvé sur Spotify.")
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

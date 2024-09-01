import requests
import logging
import urllib.parse


class SpotifySearch:
    def __init__(self, artist_name, album_name, title_name, mp3_file, access_token):
        self.artist_name = artist_name
        self.album_name = album_name
        self.title_name = title_name
        self.mp3_file = mp3_file
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1/search"

    def search_album(self):
        """Recherche par album sur Spotify."""
        query = f"artist:{self.artist_name} album:{self.album_name}"
        logging.info("Spotify - Requête envoyée : %s", query)
        encoded_query = urllib.parse.quote(query)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {
            "q": encoded_query,
            "type": "album",
        }

        response = requests.get(
            self.base_url, headers=headers, params=params, timeout=10
        )
        logging.debug("Spotify - Requête envoyée : %s", response.url)
        logging.debug("Spotify - Statut de la réponse : %s", response.status_code)

        return self.handle_response(response)

    def search_title(self):
        """Recherche par titre sur Spotify."""
        query = f"artist:{self.artist_name} track:{self.title_name}"
        logging.debug("Spotify query %s", query)
        encoded_query = urllib.parse.quote(query)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {
            "q": encoded_query,
            "type": "track",
        }

        response = requests.get(
            self.base_url, headers=headers, params=params, timeout=10
        )
        logging.debug("Spotify - Requête envoyée : %s", response.url)
        logging.debug("Spotify - Statut de la réponse : %s", response.status_code)

        return self.handle_response(response)

    def handle_response(self, response):
        """Gérer la réponse de l'API Spotify."""
        try:
            if response.status_code == 200:
                data = response.json()
                # Vérification si 'albums' ou 'tracks' existe dans la réponse
                if "albums" in data and data["albums"]["items"]:
                    album_info = data["albums"]["items"][0]
                    try:
                        album_cover = album_info["images"][0]["url"]
                        logging.info("Spotify album url : %s", album_cover)
                        return album_cover
                    except (IndexError, KeyError) as e:
                        logging.error(
                            "Spotify - Erreur lors de la récupération de l'image de l'album avec Spotify. %s",
                            e,
                        )
                        return False
                elif "tracks" in data and data["tracks"]["items"]:
                    track_info = data["tracks"]["items"][0]
                    try:
                        album_cover = track_info["album"]["images"][0]["url"]
                        logging.info("Spotify track album url : %s", album_cover)
                        return album_cover
                    except (IndexError, KeyError) as e:
                        logging.error(
                            "Spotify - Erreur lors de la récupération de l'image de l'album avec Spotify. %s",
                            e,
                        )
                        return False
                else:
                    logging.warning("Spotify - Aucun résultat trouvé.")
                    return False
            else:
                logging.error(
                    "Spotify - Erreur de requête: Status Code %s", response.status_code
                )
                return False
        except Exception as e:
            logging.error(
                "Spotify - Erreur inattendue lors du traitement de la réponse: %s", e
            )
            return False

    def search(self):
        """Effectue les recherches par album et par titre sur Spotify."""
        logging.info(
            "Spotify - Début de la recherche pour l'artiste: %s, album: %s",
            self.artist_name,
            self.album_name,
        )

        # Recherche par album
        album_cover = self.search_album()
        if album_cover:
            logging.info("Spotify - Album trouvé, URL de l'image : %s", album_cover)
            logging.info("Spotify - Téléchargement de l'image depuis : %s", album_cover)
            return album_cover

        # Si la recherche par album échoue, on tente la recherche par titre
        logging.info(
            "Spotify - Recherche par album échouée, tentative de recherche par titre."
        )
        album_cover = self.search_title()

        if album_cover:
            logging.info("Spotify - Titre trouvé, URL de l'image : %s", album_cover)
            logging.info("Spotify - Téléchargement de l'image depuis : %s", album_cover)
        else:
            logging.warning(
                "Spotify - Aucun résultat trouvé pour l'artiste : %s, titre : %s",
                self.artist_name,
                self.title_name,
            )

        return album_cover

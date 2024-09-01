import urllib.parse
import requests
import logging
from pathlib import Path


class DeezerSearch:
    def __init__(self, artist_name, album_name, title_name, mp3_file):
        self.artist_name = artist_name
        self.album_name = album_name
        self.title_name = title_name
        self.mp3_file = mp3_file
        self.base_url = "https://api.deezer.com/search"
        self.timeout = 10

    def encode_query(self, query):
        """Double encodage du query pour correspondre au format attendu par l'API."""
        return (
            urllib.parse.quote(query)
            .replace("%3A", "%253A")
            .replace("%22", "%2522")
            .replace("%20", "%2520")
        )

    def search_album(self, modified_query=False):
        """Recherche par album."""
        if modified_query:
            query = f'artist:"{self.artist_name}" album:"{self.album_name}"'
        else:
            query = f'artist:"{self.artist_name}" album:"{self.album_name}"'  # Correction ici

        logging.debug("Deezer - query %s", query)
        encoded_query = self.encode_query(query)
        url = f"{self.base_url}/album?q={encoded_query}"
        response = requests.get(url, timeout=self.timeout)
        logging.debug("Deezer - Requête envoyée : %s", response.url)
        logging.debug("Deezer - Statut de la réponse : %s", response.status_code)

        return self.handle_response(response)

    def search_title(self):
        """Recherche par titre."""
        query = f'artist:"{self.artist_name}" track:"{self.title_name}"'
        logging.debug("Deezer - query %s", query)
        encoded_query = self.encode_query(query)
        url = f"{self.base_url}?q={encoded_query}"
        timeout = 10
        response = requests.get(url, timeout=self.timeout)
        logging.debug("Deezer - Requête envoyée : %s", response.url)
        logging.debug("Deezer - Statut de la réponse : %s", response.status_code)

        return self.handle_response(response)

    def search_by_filename(self):
        """Recherche par nom de fichier MP3."""
        mp3_name = Path(self.mp3_file).stem
        if mp3_name.count("-") != 1:
            return None

        artist_name, title_name = [part.strip() for part in mp3_name.split("-", 1)]
        query = f'artist:"{artist_name}" track:"{title_name}"'
        logging.debug("Deezer - query %s", query)
        encoded_query = self.encode_query(query)
        url = f"{self.base_url}?q={encoded_query}"
        timeout = 10
        response = requests.get(url, timeout=self.timeout)
        logging.debug("Deezer - Requête envoyée : %s", response.url)
        logging.debug("Deezer - Statut de la réponse : %s", response.status_code)

        return self.handle_response(response)

    def handle_response(self, response):
        """Gérer la réponse de l'API Deezer."""
        try:
            if response.status_code == 200:
                data = response.json()
                # logging.info("Deezer - data : %s", data)
                if "data" in data and data["data"]:
                    # Prendre le premier résultat
                    album_info = data["data"][0]
                    try:
                        album_cover = (
                            album_info["album"]["cover_xl"]
                            if "album" in album_info
                            else album_info["cover_xl"]
                        )
                        logging.info("Deezer - album url : %s", album_cover)
                        return album_cover
                    except (IndexError, KeyError) as e:
                        logging.error(
                            "Deezer - Erreur lors de la récupération de l'image de l'album avec Deezer. %s",
                            e,
                        )
                        return False
                else:
                    logging.warning("Deezer - Aucun résultat trouvé.")
                    return False
            else:
                logging.error(
                    "Deezer - Erreur de requête: Status Code %s", response.status_code
                )
                return False
        except Exception as e:
            logging.error(
                "Deezer - Erreur inattendue lors du traitement de la réponse: %s", e
            )
            return False

    def search(self):
        """Effectue les recherches par album, titre, et nom de fichier MP3."""
        # Recherche par album
        album_cover = self.search_album()
        if album_cover:
            return album_cover

        # Si aucun résultat, essayer avec la requête modifiée
        album_cover = self.search_album(modified_query=True)
        if album_cover:
            return album_cover

        # Recherche par titre
        album_cover = self.search_title()
        if album_cover:
            return album_cover

        # Recherche par nom de fichier
        return self.search_by_filename()

import os
import eyed3
import requests
import logging
from pathlib import Path
from deezer_search import DeezerSearch
from spotify_search import SpotifySearch
from PIL import Image
import datetime
from colorlog import ColoredFormatter
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler
from resize_download_img import ResizeDownloadImg


class Tools:
    request_count = 0
    max_requests = 100
    spotify_access_token = None

    @staticmethod
    def configure_logging():
        """Configure le système de logging pour l'application."""
        absolute_path = os.path.abspath(__file__)
        current_path = os.path.dirname(absolute_path)
        parent_dir_name = os.path.basename(current_path)  # Nom du répertoire parent
        now = datetime.datetime.now()
        yyyymmdd_hhmmss = now.strftime("%Y%m%d_%H%M%S")
        log_file_name = f"{parent_dir_name}_{yyyymmdd_hhmmss}.log"  # Fichier de log courant avec horodatage
        log_file_path = os.path.join(current_path, log_file_name)

        # Configurer le répertoire des logs archivés
        log_dir = os.path.join(current_path, "logs")
        os.makedirs(
            log_dir, exist_ok=True
        )  # Créer le répertoire ./logs s'il n'existe pas

        # Déplacer l'ancien fichier de log courant dans le répertoire ./logs/*
        previous_logs = [
            f
            for f in os.listdir(current_path)
            if f.startswith(parent_dir_name) and f.endswith(".log")
        ]
        for prev_log in previous_logs:
            os.rename(
                os.path.join(current_path, prev_log), os.path.join(log_dir, prev_log)
            )

        # Configure logging to file in the current directory with timestamped filename
        file_handler = logging.FileHandler(log_file_path, mode="w")
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)

        # Configure RotatingFileHandler for archived logs in ./logs
        archive_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, f"{parent_dir_name}.log"),
            mode="a",
            maxBytes=5 * 1024 * 1024,  # Taille maximale de 5 MB par fichier de log
            backupCount=10,  # Nombre maximum de fichiers de log à conserver
            encoding=None,
            delay=0,
        )
        archive_handler.setLevel(logging.INFO)
        archive_handler.setFormatter(file_formatter)

        # Configure logging to console with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        color_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "blue",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(color_formatter)

        # Attacher les handlers au logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)  # Log courant dans le répertoire courant
        logger.addHandler(console_handler)  # Logs vers la console
        logger.addHandler(archive_handler)  # Archive dans ./logs/

        # Supprimer les logs verbeux des bibliothèques tierces
        logging.getLogger("eyed3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)

        logger.info("Started")

    @staticmethod
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
        auth_response_data = auth_response.json()

        if auth_response.status_code != 200:
            logging.error("Failed to get Spotify access token: %s", auth_response_data)
            return None

        logging.info("Spotify access token retrieved successfully.")
        Tools.spotify_access_token = auth_response_data["access_token"]
        Tools.request_count = 0  # Reset the request count
        return Tools.spotify_access_token

    @staticmethod
    def extract_image_from_mp3(mp3_file, img_file_full):
        """Extrait l'image de la balise ID3 du fichier MP3."""
        try:
            audio_file = eyed3.load(mp3_file)
            if audio_file.tag and audio_file.tag.images:
                image = audio_file.tag.images[0].image_data
                with open(img_file_full, "wb") as img_file:
                    img_file.write(image)
                logging.info(
                    "Image extraite depuis %s vers %s", mp3_file, img_file_full
                )
                return img_file_full
        except Exception as e:
            logging.error(
                "Erreur lors de l'extraction de l'image depuis %s: %s", mp3_file, e
            )
        return None

    @staticmethod
    def check_and_renew_token(client_id, client_secret):
        """Vérifie si le jeton doit être régénéré et le régénère si nécessaire."""
        if (
            Tools.request_count >= Tools.max_requests
            or Tools.spotify_access_token is None
        ):
            logging.info("Spotify access token needs to be renewed.")
            return Tools.get_spotify_access_token(client_id, client_secret)
        Tools.request_count += 1
        return Tools.spotify_access_token

    @staticmethod
    def get_tags(mp3_file):
        """Récupère les tags ID3 d'un fichier MP3."""
        mp3_file = mp3_file.encode("utf-8").decode("utf-8")
        logging.debug("getmp3Tags mp3_file : %s", mp3_file)

        if os.path.isfile(mp3_file):
            logging.debug("%s exists", mp3_file)
            audio_file = eyed3.load(mp3_file)
            if audio_file is None:
                logging.error(
                    "Erreur : Impossible de charger le fichier MP3 %s", mp3_file
                )
                return "no artist", "no title", "no album"

            if audio_file.tag is None:
                logging.error(
                    "Erreur : Aucune balise ID3 trouvée dans le fichier MP3 %s",
                    mp3_file,
                )
                return "no artist", "no title", "no album"

            artist = (
                audio_file.tag.artist.strip() if audio_file.tag.artist else "no artist"
            )
            title = audio_file.tag.title.strip() if audio_file.tag.title else "no title"
            album = audio_file.tag.album.strip() if audio_file.tag.album else "no album"

            logging.debug("Artist: %s", artist)
            logging.debug("Album: %s", album)
            logging.debug("Track: %s", title)
            return artist, title, album
        else:
            logging.error("File %s does not exist", mp3_file)
            logging.error("Absolute path: %s", os.path.abspath(mp3_file))
            return "no artist", "no title", "no album"

    @staticmethod
    def process_no_cover(my_txt):
        """Écrit l'information dans le fichier no_cover.txt."""
        try:
            with open("no_cover.txt", "a") as opfile:
                opfile.write(my_txt + "\n")
            logging.info("Added to no_cover.txt: %s", my_txt)
        except Exception as e:
            logging.error("Error writing to no_cover.txt: %s", e)

    @staticmethod
    def verify_image_size(img_path, min_width, min_height):
        logging.debug("verify_image_size %s %s %s", img_path, min_width, min_height)
        """Vérifie que l'image respecte les dimensions minimales."""
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                if width >= min_width and height >= min_height:
                    logging.debug("%s size ok", img_path)
                    return True
                else:
                    logging.info(
                        "Image %s trop petite (%dx%d)", img_path, width, height
                    )
                    os.remove(img_path)
                    return False
        except Exception as e:
            logging.error(
                "Erreur lors de la vérification de la taille de l'image %s: %s",
                img_path,
                e,
            )
            return False

    @staticmethod
    def process_image_search(
        artist_name,
        album_name,
        title_name,
        mp3_file,
        img_file_full,
        index,
        total_files,
        resize_download_img,
        spotify_access_token,
        spotify_folder,
        deezer_folder,
    ):
        """Effectue la recherche d'image via Spotify et Deezer."""
        logging.info(
            "%s/%s Traitement de %s - artist : %s title : %s album : %s",
            index,
            total_files,
            mp3_file,
            artist_name,
            title_name,
            album_name,
        )

        # Vérification de l'existence et de la taille de l'image
        if os.path.exists(img_file_full):
            if Tools.verify_image_size(img_file_full, 400, 400):
                logging.info(
                    "L'image existe déjà et est de taille adéquate : %s", img_file_full
                )
                return True
            else:
                logging.info(
                    "L'image existe déjà mais est trop petite, tentative de téléchargement via Spotify et Deezer."
                )
                os.remove(img_file_full)

        # Extraction de l'image à partir du fichier MP3
        if Tools.extract_image_from_mp3(mp3_file, img_file_full):
            if Tools.verify_image_size(img_file_full, 400, 400):
                logging.info("Image extraite du fichier MP3 : %s", img_file_full)
                logging.info(
                    "Start ResizeDownloadImg.verify_and_resize_image img_file_full : %s",
                    img_file_full,
                )
                resize_img_instance = ResizeDownloadImg()
                resize_img_instance.verify_and_resize_image(img_file_full)
                return True
            else:
                logging.info(
                    "Image extraite du fichier MP3 mais trop petite, tentative de téléchargement via Spotify et Deezer."
                )

        # Recherche sur Spotify
        album_cover_spotify = None
        spotify_search = SpotifySearch(
            artist_name, album_name, title_name, mp3_file, spotify_access_token
        )
        album_cover_spotify = spotify_search.search()
        if album_cover_spotify:
            spotify_img_path = os.path.join(
                spotify_folder, os.path.basename(img_file_full)
            )
            if not os.path.exists(spotify_img_path):
                logging.info("Image trouvée sur Spotify : %s", album_cover_spotify)
                spotify_img_path = resize_download_img.download_image(
                    album_cover_spotify, spotify_folder, os.path.basename(img_file_full)
                )
                if Tools.verify_image_size(spotify_img_path, 400, 400):
                    logging.info(
                        "L'image Spotify est valide et a été sauvegardée : %s",
                        spotify_img_path,
                    )

            else:
                logging.info("L'image Spotify existe déjà : %s", spotify_img_path)

        # Recherche sur Deezer
        album_cover_deezer = None
        deezer_search = DeezerSearch(artist_name, album_name, title_name, mp3_file)
        album_cover_deezer = deezer_search.search()
        if album_cover_deezer:
            deezer_img_path = os.path.join(
                deezer_folder, os.path.basename(img_file_full)
            )
            if not os.path.exists(deezer_img_path):
                logging.info("Image trouvée sur Deezer : %s", album_cover_deezer)
                deezer_img_path = resize_download_img.download_image(
                    album_cover_deezer, deezer_folder, os.path.basename(img_file_full)
                )
                if Tools.verify_image_size(deezer_img_path, 400, 400):
                    logging.info(
                        "L'image Deezer est valide et a été sauvegardée : %s",
                        deezer_img_path,
                    )
            else:
                logging.info("L'image Deezer existe déjà : %s", deezer_img_path)

        # Si aucune image valide n'est trouvée, ajouter à no_cover.txt
        if not album_cover_spotify and not album_cover_deezer:
            no_cover_entry = f"{mp3_file};{artist_name};{title_name};{album_name}"
            Tools.process_no_cover(no_cover_entry)
            logging.error("%s No Cover", mp3_file)
            return False

        return True

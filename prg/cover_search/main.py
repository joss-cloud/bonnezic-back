import logging
import os
import glob
from pathlib import Path
from tools import Tools  # Importer la classe Tools après la modification
from resize_download_img import ResizeDownloadImg
import configparser


def main():
    # Configurer les logs
    Tools.configure_logging()

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

    # Obtenir le jeton d'accès Spotify
    spotify_access_token = Tools.get_spotify_access_token(client_id, client_secret)
    if not spotify_access_token:
        logging.error("Spotify access token could not be retrieved. Exiting.")
        exit(1)
    logging.info("Spotify access token retrieved: %s", spotify_access_token)

    # Charger les fichiers de suivi
    with open("no_cover.txt", "r") as file:
        covered_files = {
            os.path.normpath(line.split(";")[0].strip()) for line in file.readlines()
        }

    # Configurer le chemin du dossier MP3
    mp3_folder = "/home/zic"  # Remplacez par le chemin réel
    glob_path = f"{mp3_folder}/**/*.*"
    album_folder = "/home/web/bonnezic.com/album"
    deezer_folder = "/home/web/bonnezic.com/deezer"
    spotify_folder = "/home/web/bonnezic.com/spotify"

    # Récupérer la liste de tous les fichiers correspondant au glob_path
    all_files = glob.glob(glob_path, recursive=True)
    total_files = len(all_files)

    no_tag = []
    no_album = []
    no_cover = []

    resize_download_img = ResizeDownloadImg()

    for index, mp3_file in enumerate(all_files, start=1):
        spotify_access_token = Tools.check_and_renew_token(client_id, client_secret)
        normalized_mp3_file = os.path.normpath(os.path.abspath(mp3_file))
        mp3_name = Path(mp3_file).stem
        logging.debug("")
        logging.debug("**************************************************")
        logging.debug("Traitement %s/%s : %s", index, total_files, mp3_name)

        # Définir les chemins vers les images potentielles dans chaque répertoire
        img_file_album = os.path.join(album_folder, mp3_name + ".jpg")
        img_file_spotify = os.path.join(spotify_folder, mp3_name + ".jpg")
        img_file_deezer = os.path.join(deezer_folder, mp3_name + ".jpg")

        # Vérification si l'image existe dans un des répertoires
        if (
            os.path.isfile(img_file_album)
            or os.path.isfile(img_file_spotify)
            or os.path.isfile(img_file_deezer)
        ):
            logging.debug("L'image existe déjà dans l'un des répertoires, skipping...")
            continue

        if normalized_mp3_file in covered_files:
            logging.debug("%s est déjà dans no_cover.txt, skipping...", mp3_file)
            continue

        logging.debug("%s not in no_cover.txt", mp3_file)

        artist_mp3, title_mp3, album_mp3 = Tools.get_tags(mp3_file)
        logging.debug("End get_tags %s", mp3_file)

        if artist_mp3 in [None, "no artist", "None"]:
            no_tag.append(mp3_file)
            logging.error("%s No Tag Artist", mp3_file)
            continue

        if title_mp3 in [None, "no title", "None"]:
            logging.error("%s No Tag Title", mp3_file)
            no_tag.append(mp3_file)
            continue

        if album_mp3 in [None, "no album", "None"]:
            logging.info("%s No Tag Album", mp3_file)
            no_album.append(mp3_file)
            album_mp3 = "None"

        logging.debug("Appel à process_image_search pour %s", mp3_file)
        if not Tools.process_image_search(
            artist_mp3,
            album_mp3,
            title_mp3,
            mp3_file,
            img_file_album,
            index,
            total_files,
            resize_download_img,
            spotify_access_token,
            spotify_folder,
            deezer_folder,
        ):
            # Si aucune image valide n'est trouvée, seulement alors ajouter à no_cover.txt
            logging.error("%s No Cover", mp3_file)
            my_txt = f"{mp3_file};{artist_mp3};{title_mp3};{album_mp3}"
            Tools.process_no_cover(my_txt)
            no_cover.append(mp3_file)
        else:
            # Si une image est trouvée, ne pas faire d'ajout dans no_cover.txt
            logging.info("Cover found for %s, not adding to no_cover.txt", mp3_file)

    with open("no_tag.txt", "w") as opfile:
        opfile.write("\n".join(no_tag))


if __name__ == "__main__":
    main()

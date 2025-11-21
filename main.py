import os
import logging
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from wcs_scraper import fetch_courses_html
from test_generator import generate_test_from_html
from discord_client import send_test_to_discord

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()
REVISION_FILE = "Revision_WCS.xlsx"


def get_courses_for_today():
    # Lis le fichier Excel de révisions et renvoie une liste de cours à réviser aujourd'hui.
    if not os.path.exists(REVISION_FILE):
        logging.error(f"{REVISION_FILE} introuvable dans le dossier courant.")
        raise FileNotFoundError(
            f"{REVISION_FILE} introuvable dans le dossier courant.")

    try:
        df = pd.read_excel(REVISION_FILE)
    except Exception as e:
        logging.error(f"Erreur lors de la lecture du fichier Excel: {e}")
        raise

    expected_cols = ["cours", "url_wcs"]
    for col in expected_cols:
        if col not in df.columns:
            logging.error(f"Colonne '{col}' manquante dans {REVISION_FILE}.")
            raise ValueError(
                f"Colonne '{col}' manquante dans {REVISION_FILE}. "
                f"Colonnes présentes : {list(df.columns)}"
            )

    # Toutes les autres colonnes sont censées être des dates de révision
    # On exclut "Date" pour ne pas déclencher de révision le jour même
    date_cols = [
        c for c in df.columns if c not in expected_cols and c != "Date"]
    if not date_cols:
        logging.error("Aucune colonne de dates de révision trouvée.")
        raise ValueError(
            "Aucune colonne de dates de révision trouvée "
            f"(attendait au moins J0/J+1/J+3...). Colonnes : {list(df.columns)}"
        )

    # Conversion en date
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    today = datetime.today().date()
    # Mask = au moins une des colonnes de dates = aujourd'hui
    mask = df[date_cols].eq(today).any(axis=1)
    today_df = df[mask].copy()

    courses = []
    for _, row in today_df.iterrows():
        courses.append(
            {
                "name": row["cours"],
                "url": row["url_wcs"],
            }
        )
    return courses


def main():
    logging.info("Démarrage du script de révision WCS.")

    try:
        courses = get_courses_for_today()
    except Exception as e:
        logging.critical(f"Impossible de récupérer les cours : {e}")
        return

    if not courses:
        logging.info(
            "Aucune révision prévue aujourd'hui (ou Excel pas à jour).")
        return

    logging.info(f"{len(courses)} cours à réviser aujourd'hui.")

    email = os.getenv("WCS_EMAIL")
    password = os.getenv("WCS_PASSWORD")

    if not email or not password:
        logging.critical(
            "Variables d'environnement WCS_EMAIL et/ou WCS_PASSWORD manquantes.")
        raise RuntimeError(
            "Variables d'environnement WCS_EMAIL et/ou WCS_PASSWORD manquantes "
            "(fichier .env ?)."
        )

    # On récupère le contenu de chaque cours WCS (login une seule fois)
    try:
        courses_data = fetch_courses_html(courses, email, password)
    except Exception as e:
        logging.critical(f"Erreur critique lors du scraping : {e}")
        return

    # Pour chaque cours : récupérer le contenu
    all_courses_content = []
    all_attachments = []
    all_images = []
    course_names = []

    for course in courses_data:
        name = course["name"]
        url = course["url"]
        content_text = course.get("content_text", "")
        images = course.get("images", [])
        attachments = course.get("attachments", [])

        if not content_text:
            logging.warning(
                f"Contenu vide pour le cours {name}, passage au suivant.")
            continue

        course_names.append(name)
        all_courses_content.append(f"### {name}\n\n{content_text}")
        all_attachments.extend(attachments)
        all_images.extend(images)

    if not all_courses_content:
        logging.error("Aucun contenu valide trouvé dans les cours.")
        return

    # Combiner tous les cours en un seul contenu
    combined_content = "\n\n---\n\n".join(all_courses_content)
    combined_name = "Révision du jour - " + ", ".join(course_names)

    logging.info(
        f"Génération d'UN SEUL test combiné pour {len(course_names)} cours")
    try:
        test_md = generate_test_from_html(
            combined_content, combined_name, all_attachments)

        logging.info(f"Envoi du test combiné sur Discord")
        send_test_to_discord(
            combined_name, courses[0]["url"], test_md, all_images, all_attachments)
    except Exception as e:
        logging.error(f"Erreur lors de la génération du test combiné : {e}")
        return

    logging.info("Test combiné généré et envoyé avec succès !")


if __name__ == "__main__":
    main()

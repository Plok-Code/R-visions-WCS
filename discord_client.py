import os
import textwrap
import requests
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Marge sous la limite des 2000 caractères Discord
MAX_LEN = 1900


def _post_chunk(chunk: str) -> None:
    """Envoie un morceau de texte au webhook Discord."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        load_dotenv()
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        raise RuntimeError(
            "ERREUR CRITIQUE : DISCORD_WEBHOOK_URL est introuvable. "
            "Vérifie que ton fichier .env est bien à la racine du projet."
        )

    resp = requests.post(webhook_url, json={"content": chunk})

    if resp.status_code >= 400:
        logging.error(f"Erreur envoi Discord {resp.status_code}: {resp.text}")


def send_test_to_discord(
    course_name: str,
    course_url: str,
    test_markdown: str,
    images: List[str] = None,
    attachments: List[Dict[str, str]] = None,
) -> None:
    """
    Envoie le test sur Discord via le webhook, en plusieurs messages si nécessaire.
    Préserve la mise en forme (paragraphes, sauts de ligne).
    """
    # Construction du header (sans URL)
    header = (
        f"**Révision du jour : {course_name}**\n"
        "Voici ton test généré automatiquement :\n\n"
    )

    # Si le header dépasse la marge, on l'envoie séparément
    if len(header) > MAX_LEN:
        _post_chunk(header)
        full = test_markdown
    else:
        full = header + test_markdown

    # Découpage en respectant les paragraphes (double saut de ligne)
    paragraphs = full.split("\n\n")
    buffer = ""

    for para in paragraphs:
        # Tenter d'ajouter le paragraphe au buffer
        if buffer:
            candidate = buffer + "\n\n" + para
        else:
            candidate = para

        # Si ça dépasse la limite
        if len(candidate) > MAX_LEN:
            # Envoyer le buffer actuel s'il existe
            if buffer:
                _post_chunk(buffer)
                buffer = para
            else:
                # Le paragraphe seul est trop long, on le découpe par lignes
                lines = para.split("\n")
                for line in lines:
                    if buffer and len(buffer + "\n" + line) > MAX_LEN:
                        _post_chunk(buffer)
                        buffer = line
                    else:
                        buffer = buffer + "\n" + line if buffer else line
        else:
            buffer = candidate

    # Envoyer le dernier buffer
    if buffer:
        _post_chunk(buffer)

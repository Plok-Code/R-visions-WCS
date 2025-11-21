from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

LOGIN_URL = "https://odyssey.wildcodeschool.com/users/sign_in"


def fetch_courses_html(courses: List[Dict[str, str]], email: str, password: str) -> List[Dict[str, Any]]:
    enriched_courses = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Login Robuste
        try:
            print(f"Connexion à {LOGIN_URL}...")
            page.goto(LOGIN_URL)
            page.wait_for_load_state("domcontentloaded")

            page.fill("input[type='email']", email)
            page.fill("input[type='password']", password)

            sign_in_button = page.locator("button:has-text('Sign in')")
            sign_in_button.wait_for(state="visible")
            page.wait_for_timeout(1000)

            sign_in_button.click()

            # Attente validation login
            try:
                page.wait_for_url(lambda u: "sign_in" not in u, timeout=15000)
                print("Login réussi.")
            except Exception:
                print("Attention: Timeout redirection login.")

            page.wait_for_load_state("networkidle")

        except Exception as e:
            print(f"Erreur critique login : {e}")
            browser.close()
            return []

        # Scraping
        for course in courses:
            url = course["url"]
            print(f"Traitement : {course['name']}")

            try:
                page.goto(url)
                # Attente du conteneur spécifique Odyssey
                try:
                    page.wait_for_selector(
                        "div.mui-1l4ku3b-questContent", timeout=10000)

                    # --- INTERACTION : Déplier les contenus cachés ---
                    expanders = page.locator(
                        "div.mui-1l4ku3b-questContent button[aria-expanded='false'], div.mui-1l4ku3b-questContent button:has-text('Solution'), div.mui-1l4ku3b-questContent button:has-text('Indice')")

                    count = expanders.count()
                    if count > 0:
                        print(
                            f"  -> {count} éléments interactifs détectés. Tentative d'ouverture...")
                        for i in range(count):
                            try:
                                if expanders.nth(i).is_visible():
                                    expanders.nth(i).click()
                                    page.wait_for_timeout(300)
                            except Exception as e:
                                print(
                                    f"  -> Impossible de cliquer sur l'élément {i}: {e}")

                    page.wait_for_timeout(1000)
                    # -------------------------------------------------

                    content_html = page.inner_html(
                        "div.mui-1l4ku3b-questContent")
                except:
                    print("Conteneur standard non trouvé, fallback sur body.")
                    content_html = page.content()

                soup = BeautifulSoup(content_html, 'html.parser')

                # Nettoyage
                for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                    tag.decompose()

                content_text = soup.get_text(separator="\n", strip=True)

                # Images
                images = [urljoin(url, img.get('src'))
                          for img in soup.find_all('img') if img.get('src')]

                # Pièces jointes & Liens Quêtes & Google Drive
                attachments = []
                for a in soup.find_all('a'):
                    href = a.get('href')
                    if href:
                        abs_url = urljoin(url, href)
                        text = a.get_text(strip=True)

                        # On ignore les ancres internes de la même page
                        if abs_url.split('#')[0] == url.split('#')[0]:
                            continue

                        is_file = any(abs_url.lower().endswith(ext) for ext in [
                                      '.zip', '.pdf', '.docx', '.xlsx', '.csv'])
                        is_quest = "/quests/" in abs_url or "/projects/" in abs_url
                        is_google = any(domain in abs_url for domain in [
                            'drive.google.com',
                            'colab.research.google.com',
                            'docs.google.com',
                            'sheets.google.com'
                        ])

                        if is_file or is_quest or is_google:
                            attachment_type = "file" if is_file else (
                                "google" if is_google else "quest")
                            attachments.append({
                                "text": text if text else "Lien",
                                "url": abs_url,
                                "type": attachment_type
                            })

                enriched_courses.append({
                    **course,
                    "content_text": content_text,
                    "images": list(set(images)),
                    "attachments": attachments
                })

            except Exception as e:
                print(f"Erreur scraping {course['name']}: {e}")
                enriched_courses.append(
                    {**course, "content_text": "", "images": [], "attachments": []})

        browser.close()

    return enriched_courses

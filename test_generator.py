from groq import Groq
import os

# --- PROMPT SYSTÈME ---
SYSTEM_PROMPT = """
Tu es un professeur de Data Science depuis plus de 20 ans. Tu as une reconnaissance internationale et un QI de 152.
Tu conçois des évaluations d'une efficacité exceptionnelle, centrées sur la compréhension réelle de l'élève.

Objectif :
- Le test doit être faisable seul par l'élève, sans accès au cours pendant la réalisation.
- Construire UN SEUL test de révision de 15 à 20 minutes. Chaque cours (variable selon leur longueur) doivent contenir environ 2 ou 3 questions.
- IMPORTANT : Couvrir TOUS les cours fournis de manière équilibrée.
- Privilégie des questions qui relient les concepts.
- Cela doit etre des questions ouvertes
- Tu ne cherches pas à piéger mais à maximiser l'apprentissage par la pratique.

Contraintes de sortie :
- Format Markdown clair.
- Numérote toutes les questions.
- À la fin du document, NE FAIS JAMAIS de corrigé
"""


def generate_test_from_html(course_content: str, course_name: str, attachments: list = None) -> str:
    """
    Utilise l'API Groq avec Llama 3.3 70B pour générer un test.
    C'est actuellement l'un des meilleurs modèles open-source gratuits et rapides.
    """

    # 1. Configuration API Key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERREUR : Variable GROQ_API_KEY manquante.")
        return "Erreur : Clé API Groq non définie."

    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        return f"Erreur init Groq : {str(e)}"

    # 2. Gestion des pièces jointes
    google_links = [att for att in (
        attachments or []) if att.get('type') == 'google']
    resources_section = ""
    if google_links:
        resources_section = "\n\nRessources :\n" + \
            "\n".join([f"- {l['text']}: {l['url']}" for l in google_links])

    # 3. Prompt
    full_prompt = f"""{SYSTEM_PROMPT}

    Cours : {course_name}
    
    CONTENU :
    {course_content}
    
    {resources_section}

    Génère le test maintenant en prenant le temps d'analyser les liens entre les concepts.
    """

    # 4. APPEL API GROQ (Llama 3.3 70B Versatile)
    model_name = "llama-3.3-70b-versatile"

    print(f"Lancement de {model_name} sur Groq...")

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model=model_name,
            temperature=0.6,
            max_tokens=20000,  # Large context window support
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Erreur critique Groq : {str(e)}\nVérifie ta clé API Groq."


# Test rapide
if __name__ == "__main__":
    print(generate_test_from_html(
        "Le Deep Learning utilise des réseaux de neurones...", "Intro DL"))

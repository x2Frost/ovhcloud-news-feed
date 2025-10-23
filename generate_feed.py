import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ==============================
# 🔗 Flux RSS OVHcloud à agréger
# ==============================
SOURCES = [
    "https://www.ovhcloud.com/fr/blog/feed/",
    "https://press.ovhcloud.com/feed/",
    "https://www.ovhcloud.com/fr/blog/tag/telecom/feed/"
]

# ==============================
# ⚙️ Fonctions utilitaires
# ==============================

def clean_html(text: str) -> str:
    """Nettoie le HTML pour ne garder que le texte brut."""
    return BeautifulSoup(text or "", "html.parser").get_text()


def safe_parse(url: str):
    """Récupère un flux RSS en toute sécurité."""
    try:
        print(f"🔄 Récupération du flux : {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        if not feed.entries:
            print(f"⚠️ Aucun article trouvé dans {url}")
        return feed
    except Exception as e:
        print(f"❌ Erreur sur {url} : {e}")
        return None


# ==============================
# 🧩 Création du flux fusionné
# ==============================

fg = FeedGenerator()
fg.title("Actualités OVHcloud (blog + presse + télécom)")
fg.link(href="https://www.ovhcloud.com/fr/", rel="alternate")
fg.description(f"Flux RSS regroupant toutes les actualités OVHcloud — mis à jour le {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
fg.language("fr")

# ==============================
# 📡 Lecture et fusion des flux
# ==============================

entries = []

for url in SOURCES:
    feed = safe_parse(url)
    if not feed:
        continue
    entries.extend(feed.entries)

# ==============================
# 🕒 Tri chronologique décroissant
# ==============================

entries.sort(
    key=lambda e: getattr(e, "published_parsed", None) or datetime.utcnow(),
    reverse=True
)

# ==============================
# 📰 Ajout des entrées dans le flux
# ==============================

for entry in entries:
    fe = fg.add_entry()
    fe.title(entry.title)
    fe.link(href=entry.link)
    fe.description(clean_html(getattr(entry, "summary", "")))
    fe.published(getattr(entry, "published", datetime.utcnow().isoformat()))

# ==============================
# 💾 Génération du fichier RSS
# ==============================

fg.rss_file("rss.xml")
print("✅ Flux RSS généré avec succès : rss.xml")
import json

# ==============================
# 💾 Génération du fichier JSON
# ==============================
json_feed = {
    "title": "Actualités OVHcloud (blog + presse + télécom)",
    "updated": datetime.utcnow().isoformat(),
    "source_count": len(SOURCES),
    "entries": []
}

for entry in entries:
    json_feed["entries"].append({
        "title": entry.title,
        "link": entry.link,
        "published": getattr(entry, "published", ""),
        "summary": clean_html(getattr(entry, "summary", ""))
    })

with open("feed.json", "w", encoding="utf-8") as f:
    json.dump(json_feed, f, ensure_ascii=False, indent=2)

print("✅ Flux JSON généré avec succès : feed.json")

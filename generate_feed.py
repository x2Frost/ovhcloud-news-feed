import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json

# ==============================
# 🔗 Flux RSS OVHcloud à agréger
# ==============================
SOURCES = [
    "https://www.ovhcloud.com/fr/blog/feed/",
    "https://press.ovhcloud.com/feed/",
    "https://www.ovhcloud.com/fr/blog/tag/telecom/feed/",
    "https://www.ovh.com/fr/blog/tag/security/feed/"
]

# ==============================
# ⚙️ Fonctions utilitaires
# ==============================
def clean_html(text: str) -> str:
    """Nettoie le HTML pour ne garder que le texte brut."""
    return BeautifulSoup(text or "", "html.parser").get_text()

def safe_parse(url: str):
    """Récupère un flux RSS en toute sécurité, ignore 404 ou erreurs."""
    try:
        print(f"🔄 Tentative de récupération du flux : {url}")
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Flux inaccessible ({response.status_code}) : {url}")
            return None
        feed = feedparser.parse(response.text)
        if not feed.entries:
            print(f"⚠️ Aucun article trouvé dans {url}")
        return feed
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau sur {url} : {e}")
        return None

# ==============================
# 🧩 Création du flux RSS fusionné
# ==============================
fg = FeedGenerator()
fg.title("Actualités OVHcloud (blog + presse + télécom)")
fg.link(href="https://www.ovhcloud.com/fr/", rel="alternate")
fg.description(f"Flux RSS regroupant toutes les actualités OVHcloud — mis à jour le {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
fg.language("fr")

entries = []
failed_sources = []

for url in SOURCES:
    feed = safe_parse(url)
    if feed:
        entries.extend(feed.entries)
    else:
        failed_sources.append(url)

# Tri par date décroissante
entries.sort(key=lambda e: getattr(e, "published_parsed", None) or datetime.utcnow(), reverse=True)

# Ajout au flux RSS
for entry in entries:
    fe = fg.add_entry()
    fe.title(entry.title)
    fe.link(href=entry.link)
    fe.description(clean_html(getattr(entry, "summary", "")))
    fe.published(getattr(entry, "published", datetime.utcnow().isoformat()))

# Génération du fichier RSS
fg.rss_file("rss.xml")
print("✅ Flux RSS généré : rss.xml")

# ==============================
# 💾 Génération du fichier JSON
# ==============================
json_feed = {
    "title": "Actualités OVHcloud (blog + presse + télécom)",
    "updated": datetime.utcnow().isoformat(),
    "source_count": len(SOURCES),
    "failed_sources": failed_sources,
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

print("✅ Flux JSON généré : feed.json")

# 🔹 Message résumé des flux HS
if failed_sources:
    print(f"⚠️ Flux HS détectés ({len(failed_sources)}):")
    for f in failed_sources:
        print(f" - {f}")
else:
    print("✅ Tous les flux ont été récupérés avec succès")


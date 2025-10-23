
import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime

# Liste des flux OVHcloud
sources = [
    "https://www.ovhcloud.com/fr/blog/feed/",
    "https://press.ovhcloud.com/feed/",
    "https://www.ovhcloud.com/fr/blog/tag/telecom/feed/"
]

# Création du flux fusionné
fg = FeedGenerator()
fg.title('Actualités OVHcloud (blog + presse + télécom)')
fg.link(href='https://ovhcloud.com', rel='alternate')
fg.description('Flux RSS regroupant toutes les actualités OVHcloud')
fg.language('fr')

# Parcourir et fusionner les flux
for url in sources:
    feed = safe_parse(url)
if not feed:
    continue
    for entry in feed.entries:
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.published(getattr(entry, 'published', datetime.utcnow().isoformat()))
        fe.description(getattr(entry, 'summary', ''))

# Génération du fichier RSS
fg.rss_file('rss.xml')

print("✅ Flux RSS généré : rss.xml")

# Récupération et fusion
entries = []
for url in sources:
    feed = feedparser.parse(url)
    entries.extend(feed.entries)

# Tri par date (si dispo)
entries.sort(key=lambda e: getattr(e, 'published_parsed', None) or datetime.utcnow(), reverse=True)

for entry in entries:
    fe = fg.add_entry()
    fe.title(entry.title)
    fe.link(href=entry.link)
    fe.published(getattr(entry, 'published', datetime.utcnow().isoformat()))
    fe.description(getattr(entry, 'summary', ''))

import requests

def safe_parse(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return feedparser.parse(response.text)
    except Exception as e:
        print(f"⚠️ Erreur sur {url}: {e}")
        return None

fg.description(f"Flux RSS regroupant les actualités OVHcloud — mis à jour le {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
from bs4 import BeautifulSoup

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

# puis :
fe.description(clean_html(getattr(entry, 'summary', '')))

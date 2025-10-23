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
    feed = feedparser.parse(url)
    for entry in feed.entries:
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.published(getattr(entry, 'published', datetime.utcnow().isoformat()))
        fe.description(getattr(entry, 'summary', ''))

# Génération du fichier RSS
fg.rss_file('rss.xml')

print("✅ Flux RSS généré : rss.xml")

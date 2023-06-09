""" Podcast downloader app. Search and download podcasts to your library

Usage:
    pod.py search <regex>
    pod.py list
    pod.py import <rss>
    pod.py add <iTunes>
    pod.py delete <id>
    pod.py fetch
    pod.py fetch <id>
    pod.py download
    pod.py podcast <id> suspend
    pod.py podcast <id> continue
    pod.py podcast <id> download

Options:
  -h --help     Show this screen.
"""
from jaraco.docker import is_docker
from docopt import docopt
from datetime import datetime
from urllib.parse import urlsplit
from urllib import request
from time import time
from rich.console import Console
from rich.table import Table
import requests
import feedparser
import sqlite3
import os
import shutil
import re
import unidecode
import eyed3

console = Console()


def createDatabase(conn):
    cur = conn.cursor()

    cur.execute("""
      CREATE TABLE podcasts (id INTEGER PRIMARY KEY AUTOINCREMENT, title text, artist text, genre text, rss_url text, image_url text, itunes_id int, date int, suspended int);
    """)

    cur.execute("""
        CREATE TABLE podcasts_items (id INTEGER PRIMARY KEY AUTOINCREMENT, podcast_id int, guid text, title text, desc text, keywords text, author text, media_url text, image_url text, publish_date int, filename text, downloaded int);
    """)

    pass


def normalize(text):
    valid_chars = "-_.() "
    out = ""
    for c in text:
        if str.isalpha(c) or str.isdigit(c) or (c in valid_chars):
            out += c
        else:
            out += "_"
    return out


def getCategories(tags):
    cat = []
    for tag in tags:
        cat.append(tag.term)
    return ', '.join(cat)


def searchTunes(text: str):
    url = f"https://itunes.apple.com/search?term={text}&entity=podcast"
    response = requests.get(url)

    with response as r:
        if r.status_code == 200:
            request = r.json()

            if int(request['resultCount']) == 0:
                console.print("[yellow]Important:[/yellow] Nothing to show.")
            else:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Id", style="dim", width=10)
                table.add_column("Title")
                table.add_column("Artist")
                table.add_column("Genre")

                for result in request['results']:
                    table.add_row(str(result['collectionId']),
                                  str(result['collectionName']),
                                  str(result['artistName']),
                                  str(result['primaryGenreName']))

                console.print(table)
    pass


def isRssImported(conn, rss, itunes_id=None):
    cur = conn.cursor()
    if itunes_id is None:
        cur.execute("""
            SELECT COUNT(id) AS Total FROM podcasts WHERE rss_url = ? AND itunes_id = 0
        """, (rss,))
    else:
        cur.execute("""
            SELECT COUNT(id) AS Total FROM podcasts WHERE rss_url = ? AND itunes_id = ?
        """, (rss, itunes_id))

    return False if int(cur.fetchone()[0]) == 0 else True


def importRssFeed(conn, rss):
    if not isRssImported(conn, rss):
        if not rss.startswith("http"):
            if not os.path.exists(rss):
                console.print(f"[red]Error:[/red] File '{rss}' not exists.")
                return

        feed = feedparser.parse(rss).feed
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO podcasts (title, artist, genre, rss_url, image_url, itunes_id, date, suspended) VALUES (?, ?, ?, ?, ?, ?, ?, 0);
        """, (feed.title, feed.author_detail.name, getCategories(feed.tags), rss, feed.image.url, 0, time()))

        inserted_id = cur.lastrowid
        fetchPodcastItems(conn, inserted_id)

        try:
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            console.print("[red]Error:[/red] Can't create podcast entry in queue.")

    pass


def addPodcast(conn, id):
    url = f"https://itunes.apple.com/lookup?id={id}"
    response = requests.get(url)

    with response as r:
        if r.status_code == 200:
            request = r.json()

            if int(request['resultCount']) == 1:
                podcast = request['results'][0]

                if not isRssImported(conn, podcast["feedUrl"], id):
                    cur = conn.cursor()
                    cur.execute("""
                      INSERT INTO podcasts (title, artist, genre, rss_url, image_url, itunes_id, date, suspended) VALUES (?, ?, ?, ?, ?, ?, ?, 0);
                    """, (podcast["collectionName"],
                          podcast["artistName"],
                          podcast["primaryGenreName"],
                          podcast["feedUrl"],
                          podcast["artworkUrl600"],
                          id, time()))

                    inserted_id = cur.lastrowid
                    fetchPodcastItems(conn, inserted_id)

                    try:
                        conn.commit()
                    except sqlite3.Error as e:
                        conn.rollback()
                        console.print("[red]Error:[/red] Can't create podcast entry in queue.")

                    return inserted_id
    return 0


def listPodcasts(conn):
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT id, title, artist, genre, date, itunes_id FROM podcasts ORDER BY title
    """)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Id", style="dim", width=10)
    table.add_column("Date", width=10)
    table.add_column("Title")
    table.add_column("Artist")
    table.add_column("Genre")

    for row in rows:
        inserted_date = datetime.utcfromtimestamp(int(row[4])).strftime('%Y-%m-%d')
        table.add_row(str(row[0]), inserted_date, str(row[1]), str(row[2]), str(row[3]))

    console.print(table)
    pass


def suspendPodcast(conn, id, suspend):
    cur = conn.cursor()
    cur.execute("""
        UPDATE podcasts SET suspended = ? WHERE id = ?
   """, (0 if suspend is False else 1, id,))

    try:
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        console.print("[red]Error:[/red] Can't update podcast entry.")

    pass


def deletePodcast(conn, id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM podcasts_items WHERE podcast_id = ?
    """, (id,))

    cur.execute("""
        DELETE FROM podcasts WHERE id = ?
    """, (id,))

    try:
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        console.print("[red]Error:[/red] Can't delete podcast entries.")

    pass


def fetchAllItems(conn):
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT id FROM podcasts
    """)

    for row in rows:
        fetchPodcastItems(conn, str(row[0]))

    pass


def fetchPodcastItems(conn, podcastId):
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT id, title, rss_url, artist, genre, image_url FROM podcasts WHERE id = ?
    """, (podcastId,))

    for row in rows:
        rss_url = row[2]
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            if not itemIsFetched(conn, entry.guid):
                author = str(row[3]) if not hasattr(entry, "author") else entry.author
                tags = str(row[4]) if not hasattr(entry, 'tags') else getCategories(entry.tags)
                image = str(row[5]) if not hasattr(entry, 'image') else entry.image.href
                media_url = "" if len(entry.enclosures) == 0 else entry.enclosures[0].href
                published_date = entry.published_parsed
                _time = datetime(published_date.tm_year, published_date.tm_mon, published_date.tm_mday).timestamp()

                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO podcasts_items (podcast_id, guid, title, desc, keywords, author, media_url, image_url, publish_date, filename, downloaded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '', 0)
                """, (podcastId, entry.guid, entry.title, entry.description, tags, author, media_url, image, _time))

                console.print("[green]Founded:[/green] Podcast '{podcast}' have a new episode '{episode}'.".format(
                    episode=entry.title, podcast=str(row[1])))

    try:
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        console.print("[red]Error:[/red] Can't fetch podcast entries from feed.")

    pass


def itemIsFetched(conn, guid: str):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(guid) as total FROM podcasts_items WHERE guid = '{guid}'".format(guid=guid))
    return False if int(cur.fetchone()[0]) == 0 else True


def downloadPodcastEpisodeImage(url):
    try:
        response = request.urlopen(url)
        imagedata = response.read()
    except:
        imagedata = None

    return imagedata


def dowloadAllPodcasts(conn):
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT id FROM podcasts
    """)

    for row in rows:
        downloadPodcasts(conn, str(row[0]))

    pass


def downloadPodcasts(conn, id):
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT podcasts.title as podcast_title, podcasts.artist, podcasts.image_url, 
               podcasts_items.guid, podcasts_items.title, podcasts_items.media_url, 
               podcasts_items.image_url, podcasts_items.publish_date
        FROM podcasts_items
            INNER JOIN podcasts ON podcasts.id = podcasts_items.podcast_id
        WHERE podcasts_items.downloaded = 0 AND podcasts.suspended = 0 AND podcasts.id = {id}
        ORDER BY podcasts_items.id DESC
    """.format(id=id))

    for row in rows:
        folderName = createPodcastDir(str(row[1]), str(row[0]))
        createPoster(folderName, str(row[2]))

        try:
            media_url = str(row[5])

            if len(media_url) == 0:
                continue

            date = datetime.fromtimestamp(int(row[7])).strftime("%Y-%m-%d")
            title_slug = re.sub(r'[\W_]+', '-', unidecode.unidecode(str(row[4])))
            image_url = str(row[6])

            path = urlsplit(media_url).path
            extension = os.path.splitext(path)[-1]
            filename = os.path.join(folderName, f"{date}-{title_slug}{extension}")

            if not os.path.exists(filename):
                response = requests.get(media_url, stream=True)

                with response as r:
                    if r.status_code == 200:
                        r.raw.decode_content = True
                        try:
                            with open(filename, 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                                audiofile = eyed3.load(filename)

                                if audiofile is not None:
                                    audiofile.initTag()
                                    audiofile.tag.clear()

                                    audiofile.tag.artist = str(row[1])
                                    audiofile.tag.album = str(row[0])
                                    audiofile.tag.title = str(row[4])
                                    audiofile.tag.release_date = date

                                    episodeImage = downloadPodcastEpisodeImage(image_url)
                                    if episodeImage is not None:
                                        audiofile.tag.images.set(3, episodeImage, "image/jpeg", u"cover")

                                    audiofile.tag.save()

                            updateDownloadedState(conn, str(row[3]), filename)
                            console.print(f"[green]Success:[/green] {filename} file downloaded.")
                        except:
                            pass
        except:
            pass

    pass


def updateDownloadedState(conn, guid: str, filename: str):
    cur = conn.cursor()
    cur.execute("""
        UPDATE podcasts_items SET filename = ?, downloaded = 1 WHERE guid = ?
    """, (filename, guid,))

    try:
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        console.print(f"[red]Error:[/red] Can't update podcast entry {guid} to downloaded state.")

    pass


def createPodcastDir(artist, title):
    if artist == title or title.startswith(artist):
        folderName = title
    else:
        folderName = f"{artist} - {title}"

    # normalize folder
    folderName = normalize(folderName)

    folderName = "/podcasts" if is_docker() else os.path.join(os.getenv('PODCASTS_PATH', 'podcasts'), folderName)
    if not os.path.exists(folderName):
        os.makedirs(folderName)

    return folderName


def createPoster(folderName, image_url):
    path = urlsplit(image_url).path
    extension = os.path.splitext(path)[-1]
    filename = os.path.join(folderName, "poster{ext}".format(ext=extension))

    if not os.path.exists(filename):
        response = requests.get(image_url, stream=True)

        with response as r:
            if r.status_code == 200:
                r.raw.decode_content = True
                try:
                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                        console.print(f"[green]Success:[/green] {filename} file downloaded.")
                except:
                    pass

    pass


if __name__ == "__main__":
    arguments = docopt(__doc__, argv=None, help=True, version="1.0", options_first=False)

    configFolder = "/config" if is_docker() else os.getenv("CONFIG_PATH", "config")
    if not os.path.exists(configFolder):
        os.makedirs(configFolder)

    dbFilename = os.path.join(configFolder, "podcasts.db")
    firstTime = False if os.path.exists(dbFilename) else True
    conn = sqlite3.connect(dbFilename)

    if firstTime:
        createDatabase(conn)

    if arguments["search"]:
        regex = str(arguments["<regex>"])
        searchTunes(regex)

    if arguments["list"]:
        listPodcasts(conn)

    if arguments["add"]:
        _id = str(arguments["<iTunes>"])
        addPodcast(conn, _id)

    if arguments["import"]:
        rss = str(arguments["<rss>"])
        importRssFeed(conn, rss)

    if arguments["delete"]:
        _id = str(arguments["<id>"])
        deletePodcast(conn, _id)

    if arguments["fetch"]:
        _id = arguments["<id>"]
        if _id is None:
            fetchAllItems(conn)
        else:
            fetchPodcastItems(conn, str(_id))

    if arguments["download"]:
        dowloadAllPodcasts(conn)

    if arguments["podcast"]:
        _id = arguments["<id>"]
        if arguments["suspend"]:
            suspendPodcast(conn, str(_id), True)
        elif arguments["continue"]:
            suspendPodcast(conn, str(_id), False)
        elif arguments["download"]:
            downloadPodcasts(conn, str(id))

    conn.close()

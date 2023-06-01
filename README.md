
# pod.py podcastsDownloader
  
Download any podcast from iTunes and save it in folders. Periodically.  
  
### Usage examples  
This show some examples of commands you can use
  
#### Search in iTunes for a podcast series  
Search parameter can be used to search podcasts in iTunes api.
   
    python3 pod.py search "irritacoes"  
  
#### Add podcast by number  
To add a new podcast to database you must choose iTunes collection id from console table presented in search results

    python3 pod.py add 1238347934  
  
#### List added podcasts  
This parameter can list all inserted podcasts to follow in your database

    python3 pod.py list

#### Fetch podcasts
This parameter permit update all podcasts entries from RSS to database, looking for new podcasts periodically if added to an cronjob or scheduler task

	python3 pod.py fetch

#### Download podcasts
Use this command periodically to get poster image and all non-downloaded podcasts episodes.

	python3 pod.py download
You can use this command with fetch to update database and download all next episodes in this way.

	python3 pod.py fetch && python3 pod.py download

#### Import podcasts from rss
Import a rss feed directly without iTunes API search 

    python3 pod.py import "https://www.omnycontent.com/d/playlist/58028bcf-e01f-4274-aca7-ad3300f67928/93818198-74f6-4158-8c20-ad7f009ff4a7/0db2396f-b8cc-4933-b9b7-ad7f009ff57a/podcast.rss"

Or from local storage

    python3 pod.py import "/podcasts/feeds/my-podcast-feed.rss"

## Running
![pod.py running in command line](https://raw.githubusercontent.com/pmcfernandes/podcastsDownloader/master/screenshot.png)
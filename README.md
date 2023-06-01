
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

## Running
![enter image description here](https://raw.githubusercontent.com/pmcfernandes/podcastsDownloader/master/screenshot.png)
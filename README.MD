# Daemon

This program runs on startup and performs certain functions:

- Periodically scrape data from websites
- Send alerts to fishlicka.alerts@gmail.com

and maybe:
- Moderate JG communities / help answer comments
- Play music? Have it navigate soundcloud or a list of youtube videos
- Tell me to exercise / drink water / take a break

for now it just scrapes.

# Usage
```shell
pipenv shell
python start.py # runs the scraper

python analysis/swipe.py # swipe through newest jobs
```
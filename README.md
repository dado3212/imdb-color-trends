# Movie Color Trends

https://stephenfollows.com/p/when-did-colour-films-eclipse-black-and-white-films tries to answer the question "When did colour films eclipse black-and-white films?". To do this he pulled from a dataset of 377,967 feature films, released between 1900 and 2023. I couldn't find the data that he used for it, so this recreates a version of it using public (ish) data. It uses IMDb's undocumented GraphQL endpoint to get color information, and then fetches that by cross-referencing with `title.basics.tsv` and `title.ratings.tsv` from IMDb's Non-Commercial Datasets site (https://datasets.imdbws.com/) to get up to 1k movies from each year as sorted by IMDb vote totals, resulting in 101,104 total feature films between 1894 and 2025.

This gets a slightly different answer (1966 vs 1967) and a slightly different graph (no 1903 spike for [The Life and Passion of Jesus Christ (1903)](https://www.imdb.com/title/tt0127962/)).

<img src="/coloration.png?raw=true" height="500px" alt="Graph showing the proportion of movies in color over time"/>

## Installation
```
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Download title.basics.tsv and title.ratings.tsv from IMDb's Non-Commercial Datasets site - https://datasets.imdbws.com/.

The current run is based on data retrieved August 12, 2025.

## Running Scripts

This will build the `imdb_top100_per_year_with_colors.csv` file.
```
source venv/bin/activate
python main.py
```

This will render it into an image.
```
python plot.py
```

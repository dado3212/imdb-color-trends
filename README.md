# Movie Color Trends

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
import requests, duckdb, time, json, signal, sys

def get_info_for_id(id):
  url = "https://caching.graphql.imdb.com/"
  params = {
    # Extracted from mitmproxy
    "extensions": '{"persistedQuery":{"sha256Hash":"24390aa55847f64ca3b9889f64fa0b51fbbb2ca33b91bb0ea09b928754ea3002","version":1}}',
    "operationName": "titleTechnicalSpecifications",
    "variables": '{"tconst":"' + id + '"}'
  }

  headers = {
    "content-type": "application/json,application/json",
  }

  resp = requests.get(url, headers=headers, params=params).json()
  colors = [x['displayableProperty']['value']['plainText'] for x in resp['data']['title']['technicalSpecifications']['colorations']['items']]
  return colors

ratings_path = "title.ratings.tsv"
basics_path = "title.basics.tsv"

# Create a local cache of color information
con = duckdb.connect("imdb_cache.duckdb")

con.execute("""
CREATE TABLE IF NOT EXISTS imdb_tech (
  tconst TEXT PRIMARY KEY,
  year   INTEGER,
  primaryTitle TEXT,
  numVotes INTEGER,
  colors_json TEXT
)
""")

num_cap = 1000 # Max number of movies per year, sorted by number of votes

# All movies meeting the threshold, with year/title/rating/votes
df = con.execute(f"""
  SELECT
    CAST(b.startYear AS INTEGER) AS year,
    row_number() OVER (
      PARTITION BY CAST(b.startYear AS INTEGER)
      ORDER BY r.numVotes DESC
    ) AS rn,
    r.numVotes,
    b.primaryTitle,
    r.tconst
  FROM read_csv_auto('{ratings_path}', delim='\t', header=TRUE) AS r
  JOIN read_csv_auto('{basics_path}',  delim='\t', header=TRUE) AS b
    ON r.tconst = b.tconst
  WHERE b.titleType = 'movie'
    AND b.startYear != '\\N'
  QUALIFY rn <= {num_cap}
  ORDER BY year, r.numVotes DESC
""").df()

con.register("df_candidates", df)
to_fetch = con.execute("""
  SELECT d.year, d.primaryTitle, d.tconst, d.numVotes
  FROM df_candidates d
  LEFT JOIN imdb_tech c ON d.tconst = c.tconst
  WHERE c.tconst IS NULL
  ORDER BY d.year, d.numVotes DESC
""").df()

def handle_sigint(sig, frame):
    con.execute("""
    COPY (
      SELECT year, primaryTitle, tconst, numVotes, colors_json
      FROM imdb_tech
      ORDER BY year, numVotes DESC
    ) TO 'imdb_top_per_year_with_colors.csv' (HEADER, DELIMITER ',')
    """)
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

for i, row in enumerate(to_fetch.itertuples(index=False), 1):
  tconst = row.tconst
  try:
    colors = get_info_for_id(tconst)
    print(tconst, int(row.year), row.primaryTitle, int(row.numVotes), json.dumps(colors))
    con.execute(
      "INSERT INTO imdb_tech VALUES (?, ?, ?, ?, ?)",
      [tconst, int(row.year), row.primaryTitle, int(row.numVotes), json.dumps(colors)]
    )
  except Exception as e:
    # optional: keep a simple error log table
    con.execute("CREATE TABLE IF NOT EXISTS imdb_errors (tconst TEXT, msg TEXT)")
    con.execute("INSERT INTO imdb_errors VALUES (?, ?)", [tconst, str(e)])
  if i % 25 == 0:
    time.sleep(0.2)  # sleep every so often

# fresh export each run (no duplicates)
con.execute("""
COPY (
  SELECT year, primaryTitle, tconst, numVotes, colors_json
  FROM imdb_tech
  ORDER BY year, numVotes DESC
) TO 'imdb_top_per_year_with_colors.csv' (HEADER, DELIMITER ',')
""")
print("Wrote imdb_top_per_year_with_colors.csv")
import pandas as pd
import matplotlib.pyplot as plt
import ast

df = pd.read_csv("imdb_top_per_year_with_colors.csv")
df["colors"] = df["colors_json"].apply(ast.literal_eval)
# Only movies with color info (newer 2025 movies can be lacking)
df = df[df["colors"].apply(bool)]

df["is_bw"] = df["colors"].apply(lambda c: any("Black and White" in x for x in c))
df["is_color"] = df["colors"].apply(lambda c: any("Color" in x for x in c))
bw_ratio = df.groupby("year")["is_bw"].mean()
color_ratio = df.groupby("year")["is_color"].mean()

plt.figure(figsize=(12,6))
plt.plot(bw_ratio.index, bw_ratio.values, label="Have Black & White", marker="o", markersize=3)
plt.plot(color_ratio.index, color_ratio.values, label="Have Color", marker="o", markersize=3)
plt.title("Percentage of Top Movies by Coloration")
plt.xlabel("Year")
plt.ylabel("Proportion of Top Movies")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("coloration.png", dpi=300)
plt.show()

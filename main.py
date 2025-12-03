import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

df = pd.read_csv("epl_final.csv")



df_copy = df.copy()

df_copy["HomeWin"] = df_copy["FullTimeResult"] == "H"
df_copy["AwayWin"] = df_copy["FullTimeResult"] == "A"
df_copy["Draw"] = df_copy["FullTimeResult"] == "D"





away_win_team = df_copy.groupby("AwayTeam")[["AwayWin"]].sum()
home_win_team = df_copy.groupby("HomeTeam")[["HomeWin"]].sum()

away_game_team = df_copy.groupby("AwayTeam").size()
home_game_team = df_copy.groupby("HomeTeam").size()


#################################
# show the impact of Away/Home 
#################################
winrate = pd.DataFrame()
winrate["HomeWins"] = home_win_team["HomeWin"]
winrate["AwayWins"] = away_win_team["AwayWin"]
winrate["HomeGames"] = home_game_team
winrate["AwayGames"] = away_game_team


winrate["HomeWinRate"] = (winrate["HomeWins"] / winrate["HomeGames"]) * 100
winrate["AwayWinRate"] = (winrate["AwayWins"] / winrate["AwayGames"] ) * 100

ten_teams = winrate.sort_values("HomeGames", ascending=False)[["HomeWinRate", "AwayWinRate"]].head(10)

ten_teams.plot(kind="bar", figsize=(12, 6), colormap="seismic")
plt.title("Les 10 équipes ayant le plus participé à la Premier League entre 2000 et 2025")
plt.ylabel("Taux de victoire")
plt.xlabel("Équipe")
plt.xticks(rotation=45)
plt.legend(["Taux de victoires à domicile", "Taux de victoires à l'extérieur"])
plt.tight_layout()
plt.show()


########################################################
# show the impact of Away/Home and the first half result
########################################################
home_probs = (
    df_copy.groupby("HalfTimeResult")["HomeWin"]
      .mean()
      .rename("HomeWinProbability")
)

away_probs = (
    df_copy.groupby("HalfTimeResult")["AwayWin"]
      .mean()
      .rename("AwayWinProbability")
)

probabilities = pd.concat([home_probs, away_probs], axis=1)

print(probabilities)



########################################################
# Physical trend (fouls / yellow cards / red cards)
########################################################


df_copy = df.copy()

df_copy["TotalFouls"] = df_copy["HomeFouls"] + df_copy["AwayFouls"]
df_copy["TotalYellowCards"] = df_copy["HomeYellowCards"] + df_copy["AwayYellowCards"]
df_copy["TotalRedCards"] = df_copy["HomeRedCards"] + df_copy["AwayRedCards"]

physical_trends = df_copy.groupby("Season")[
    ["TotalFouls", "TotalYellowCards", "TotalRedCards"]
].mean()

fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True)

metrics = ["TotalFouls", "TotalYellowCards", "TotalRedCards"]
colors = ["#1f77b4", "#ff7f0e", "#d62728"]
titles = ["Fautes par match", "Cartons jaunes par match", "Cartons rouges par match"]

for i, ax in enumerate(axes):
    ax.plot(
        physical_trends.index, physical_trends[metrics[i]], marker="o", color=colors[i]
    )
    ax.set_title(titles[i], fontsize=12)
    ax.set_ylabel("Moyenne par match")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xticks(range(len(physical_trends.index)))
    ax.set_xticklabels(physical_trends.index, rotation=45, ha="right", fontsize=9)

fig.suptitle("Le niveau d’agressivité au fil des saisons", fontsize=16, fontweight="bold")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()






import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import calendar
import seaborn as sns
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
plt.savefig("taux_victoire.png")
#plt.show()


########################################################
# show the impact of Away/Home and the first half result
########################################################


home_probs = df_copy.groupby("HalfTimeResult")["HomeWin"].mean()
away_probs = df_copy.groupby("HalfTimeResult")["AwayWin"].mean()

half_time_impact = pd.DataFrame({
    'HomeWin': home_probs,
    'AwayWin': away_probs
})

half_time_impact.plot(kind="bar", figsize=(12,6), colormap="seismic")
plt.title("Probabilité de victoire à domicile/à l’extérieur en fonction du score à la mi-temps")
plt.ylabel("Taux de victoire")
plt.xlabel("Score de Mi-temps (H=Domicile devant, D=Egalité, A=Exterieur devant)")
plt.xticks(rotation=0)
plt.legend(["Domicile", "Exterieur"])
plt.tight_layout()
plt.savefig("basic.png")
#plt.show()



########################################################
# Conversion rate from half-time lead to full-time win
########################################################
df_copy["LeadHeld"] = (
    ((df_copy["HalfTimeResult"] == "H") & (df_copy["FullTimeResult"] == "H")) |
    ((df_copy["HalfTimeResult"] == "A") & (df_copy["FullTimeResult"] == "A"))
).astype(int)


def get_leading_team(row):
    if row["HalfTimeResult"] == "H":
        return row["HomeTeam"]
    elif row["HalfTimeResult"] == "A":
        return row["AwayTeam"]
    return None

df_copy["LeadingTeam"] = df_copy.apply(get_leading_team, axis=1)

# ==========================================================
# 1. TABLEAU GLOBAL : Capacité à maintenir l'avantage (H & A)
# ==========================================================

team_conversion = df_copy[df_copy["HalfTimeResult"] != "D"].groupby("LeadingTeam")["LeadHeld"].agg(["sum", "count"])
team_conversion["ConversionRate"] = (team_conversion["sum"] / team_conversion["count"] * 100)
top_10_global = team_conversion.sort_values("ConversionRate", ascending=False).head(10)

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.axis('off')

table_data_global = top_10_global.reset_index()
table_data_global.columns = ['Équipe', 'Victoires confirmées', 'Avances mi-temps', 'Taux de Conversion (%)']
table_data_global['Taux de Conversion (%)'] = table_data_global['Taux de Conversion (%)'].round(2)

table1 = ax1.table(cellText=table_data_global.values, 
                   colLabels=table_data_global.columns, 
                   cellLoc='center', loc='center',
                   colColours=["#f2f2f2"] * 4)

table1.auto_set_font_size(False)
table1.set_fontsize(10)
table1.scale(1.2, 1.8) 

plt.title("Top 10 Global : Maintenir l'avantage jusqu'à la victoire", pad=20)
plt.savefig("conversion_global.png")

# ==========================================================
# 2. TABLEAU DOMICILE : Solidité à domicile après avance
# ==========================================================

# On filtre uniquement les cas où le score à la mi-temps est 'H'
home_leading = df_copy[df_copy["HalfTimeResult"] == "H"].copy()

team_home_conv = home_leading.groupby("HomeTeam")["LeadHeld"].agg(["sum", "count"])
team_home_conv["ConversionRate"] = (team_home_conv["sum"] / team_home_conv["count"] * 100)
top_10_home = team_home_conv.sort_values("ConversionRate", ascending=False).head(10)

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.axis('off')

table_data_home = top_10_home.reset_index()
table_data_home.columns = ['Équipe (Domicile)', 'Victoires confirmées', 'Avances mi-temps', 'Taux de Conversion (%)']
table_data_home['Taux de Conversion (%)'] = table_data_home['Taux de Conversion (%)'].round(2)

# On utilise une couleur bleue pour différencier le graphique "Domicile"
table2 = ax2.table(cellText=table_data_home.values, 
                   colLabels=table_data_home.columns, 
                   cellLoc='center', loc='center',
                   colColours=["#d1e5f0"] * 4)

table2.auto_set_font_size(False)
table2.set_fontsize(10)
table2.scale(1.2, 1.8) 

plt.title("Top 10 Domicile : Maintenir l'avantage jusqu'à la victoire", pad=20)
plt.savefig("conversion_home.png")

plt.show()
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
plt.savefig("agressivite.png")
#plt.show()


########################################################
# Physical trend (fouls / yellow cards / red cards)
########################################################



df_copy["MatchDate"] = pd.to_datetime(df_copy["MatchDate"])
df_copy["Month"] = df_copy["MatchDate"].dt.month
monthly_stats = df_copy.groupby("Month")[["TotalFouls", "TotalYellowCards", "TotalRedCards"]].mean()




monthly_stats.index = monthly_stats.index.map(lambda x: calendar.month_name[x])

months_order = list(calendar.month_name[8:13]) + list(calendar.month_name[1:8])
monthly_stats = monthly_stats.reindex(months_order)

fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True)

metrics = ["TotalFouls", "TotalYellowCards", "TotalRedCards"]
colors = ["#1f77b4", "#ff7f0e", "#d62728"]
titles = [
    "Fautes par mois et match", 
    "Cartons jaunes par mois et par match", 
    "Cartons rouges par mois et par match"
]

for i, ax in enumerate(axes):
    ax.plot(
        monthly_stats.index, monthly_stats[metrics[i]], marker="o", color=colors[i]
    )
    ax.set_title(titles[i], fontsize=12)
    ax.set_ylabel("Moyenne par mois et par match")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xticks(range(len(monthly_stats.index)))
    ax.set_xticklabels(monthly_stats.index, rotation=45, ha="right", fontsize=9)

fig.suptitle("Le niveau d’agressivité dans chaque mois", fontsize=16, fontweight="bold")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("monthly_agressivity.png")
#plt.show()

########################################################
#Nombre de but par match et par season
########################################################
df_copy = df.copy()
df_copy['TotalGoals'] = df_copy['FullTimeHomeGoals'] + df_copy['FullTimeAwayGoals']
season_goals = df_copy.groupby('Season')['TotalGoals'].mean().reset_index()

plt.figure(figsize=(10, 5))
sns.lineplot(data=season_goals, x='Season', y='TotalGoals', marker='o', color='green')
plt.title('Moyenne de buts par match par saison')
plt.xlabel('Saison')
plt.ylabel('Moyenne de buts par match')
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("goals_per_season_per_match.png")
#plt.show()

########################################################
# Influence du classement et de la forme récente
########################################################

################# calcul de classement ##################
df_copy = df.copy()
df_copy["MatchDate"] = pd.to_datetime(df_copy["MatchDate"])

def team_points(season, date):
    points = {}
    #c = 0
    date = pd.to_datetime(date)

    season_data = df_copy[
        (df_copy["Season"] == season) &
        (df_copy["MatchDate"] <= date)
    ]

    for _, match in season_data.iterrows():

        home = match["HomeTeam"]
        away = match["AwayTeam"]
        result = match["FullTimeResult"]

        if result == "H":
            points[home] = points.get(home, 0) + 3

        elif result == "A":
            points[away] = points.get(away, 0) + 3

        else:  # Draw
            points[home] = points.get(home, 0) + 1
            points[away] = points.get(away, 0) + 1

    return points



def classement(season, date):
    points = team_points(season, date)

    classement_trie = dict(
        sorted(points.items(), key=lambda item: item[1], reverse=True)
    )
    c = 1
    for key,value in classement_trie.items():
        classement_trie[key] = [c,classement_trie[key]]
        c+=1
    return classement_trie

print(classement("2023/24","2024-05-04"))

############################ les résultats des 5 derniers match ################################


def recent_form(df, team, date, season, n=3):
    matches = df[
        (df["Season"] == season) &
        (df["MatchDate"] < date) &
        ((df["HomeTeam"] == team) | (df["AwayTeam"] == team))
    ].sort_values("MatchDate", ascending=False).head(n)

    points = 0
    for _, m in matches.iterrows():
        if m["FullTimeResult"] == "D":
            points += 1
        elif (m["HomeTeam"] == team and m["FullTimeResult"] == "H") or \
             (m["AwayTeam"] == team and m["FullTimeResult"] == "A"):
            points += 3

    return points



analysis_data = []

for _, match in df_copy.iterrows():

    season = match["Season"]
    date = match["MatchDate"]
    home = match["HomeTeam"]
    away = match["AwayTeam"]

    # Classement avant le match
    table = classement(season, date)

    # Si une équipe n’a pas encore de classement (début de saison)
    if home not in table or away not in table:
        continue

    home_rank = table[home][0]
    away_rank = table[away][0]

    # Forme récente (3 derniers matchs)
    home_form = recent_form(df_copy, home, date, season, n=3)
    away_form = recent_form(df_copy, away, date, season, n=3)

    analysis_data.append({
        "FormDiff": home_form - away_form,
        "RankDiff": away_rank - home_rank,
        "HomeWin": 1 if match["FullTimeResult"] == "H" else 0
    })

analysis_df = pd.DataFrame(analysis_data)
form_prob = analysis_df.groupby("FormDiff")["HomeWin"].mean()

plt.figure(figsize=(10,5))

form_prob.plot(kind="bar")

plt.title("Influence de la forme récente (3 matchs)")
plt.xlabel("Différence de forme (Home − Away)")
plt.ylabel("Probabilité de victoire à domicile")
plt.grid(True, alpha=0.3)

plt.savefig("form.png")
#plt.show()

rank_prob = analysis_df.groupby("RankDiff")["HomeWin"].mean()

rank_prob.plot(kind="bar", figsize=(10,5))
plt.title("Influence de la différence de classement")
plt.xlabel("Différence de classement (Away − Home)")
plt.ylabel("Probabilité de victoire à domicile")
plt.grid(True, alpha=0.3)
plt.savefig("classement.png")
#plt.show()



analysis_df["FormDiff_bin"] = pd.cut(
    analysis_df["FormDiff"],
    bins=[-9, -6, -3, 0, 3, 6, 9],
    labels=["-9:-6", "-6:-3", "-3:0", "0:3", "3:6", "6:9"]
)

analysis_df["RankDiff_bin"] = pd.cut(
    analysis_df["RankDiff"],
    bins=[-20, -10, -5, 0, 5, 10, 20],
    labels=["-20:-10", "-10:-5", "-5:0", "0:5", "5:10", "10:20"]
)

heatmap_data = (
    analysis_df
    .groupby(["FormDiff_bin", "RankDiff_bin"])["HomeWin"]
    .mean()
    .unstack()
)

heatmap_data = heatmap_data.iloc[::-1]


plt.figure(figsize=(12, 8))

sns.heatmap(
    heatmap_data,
    cmap="RdYlGn",
    annot=True,
    fmt=".2f",
    linewidths=0.5,
    cbar_kws={"label": "Probabilité de victoire à domicile"},
    mask=heatmap_data.isna()
)

plt.title(
    "Influence combinée de la forme récente et du classement\n"
    "sur la probabilité de victoire à domicile",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Différence de classement (Away − Home)")
plt.ylabel("Différence de forme (Home − Away)")

plt.tight_layout()
plt.savefig("heatmap_forme_classement.png")
plt.show()




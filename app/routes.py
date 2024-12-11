# app/routes.py
from flask import Blueprint, render_template, request, jsonify
from .models import ShotChart
import plotly.express as px
import pandas as pd

main = Blueprint("main", __name__)


@main.route("/get_seasons/<player_name>")
def get_seasons(player_name):
    seasons = ShotChart.get_player_seasons(player_name)
    return jsonify({"seasons": seasons})


@main.route("/get_games/<player_name>/<season>")
def get_games(player_name, season):
    games = ShotChart.get_player_games(player_name, season)
    return jsonify({"games": games})


@main.route("/")
def home():
    player_name = request.args.get("player", "Stephen Curry")
    season = request.args.get("season", "2023-24")
    game_id = request.args.get("game", None)  # None means all games

    active_players = ShotChart.get_active_players()
    available_seasons = ShotChart.get_player_seasons(player_name)
    available_games = ShotChart.get_player_games(player_name, season)
    shots_df = ShotChart.get_player_shots(player_name, season, game_id)

    # Check if we have valid shot data
    if shots_df.empty:
        # Create empty plot with message
        fig = px.scatter(title=f"No shot data available for {player_name} ({season})")
        fig.update_layout(
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                showline=False,
                title="",
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                showline=False,
                title="",
            ),
        )
        return render_template(
            "index.html",
            plot=fig.to_html(),
            stats="<p>No statistics available</p>",
            players=active_players,
            selected_player=player_name,
            seasons=available_seasons,
            selected_season=season,
            games=available_games,
            selected_game=game_id,
        )

    # Create hover text with shot distance
    shots_df["SHOT_RESULT"] = shots_df["SHOT_MADE_FLAG"].map({1: "Made", 0: "Missed"})
    shots_df["HOVER_TEXT"] = shots_df.apply(
        lambda row: f"Distance: {row['SHOT_DISTANCE']}ft<br>{row['SHOT_RESULT']} Shot",
        axis=1,
    )

    # Update title to include game info if selected
    title = f"{player_name}'s Shot Chart ({season})"
    if game_id:
        game = next((g for g in available_games if g["id"] == game_id), None)
        if game:
            title += f" - {game['display']}"

    fig = px.scatter(
        shots_df,
        x="LOC_X",
        y="LOC_Y",
        color="SHOT_RESULT",
        color_discrete_map={"Made": "#2ecc71", "Missed": "#e74c3c"},  # Green  # Red
        title=title,
        custom_data=["HOVER_TEXT"],
    )

    # Update markers
    fig.update_traces(
        marker=dict(
            symbol=[
                "circle" if made == 1 else "x" for made in shots_df["SHOT_MADE_FLAG"]
            ],
            size=10,
            line=dict(width=1, color="white"),
        ),
        hovertemplate="%{customdata[0]}<extra></extra>",
    )

    # Clean up layout
    fig.update_layout(
        showlegend=True,
        legend_title_text="Shot Outcome",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            showline=False,
            title="",
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            showline=False,
            title="",
        ),
    )

    # Calculate zone statistics with better column names
    zone_stats = (
        shots_df[shots_df["SHOT_ZONE_BASIC"] != "Backcourt"]
        .groupby("SHOT_ZONE_BASIC")
        .agg(
            Attempts=("SHOT_MADE_FLAG", "count"),
            FGPercent=("SHOT_MADE_FLAG", lambda x: f"{(x.mean() * 100):.1f}"),
        )
    )

    # Calculate 2PT and 3PT totals
    two_pt_shots = shots_df[shots_df["SHOT_TYPE"] == "2PT Field Goal"]
    three_pt_shots = shots_df[shots_df["SHOT_TYPE"] == "3PT Field Goal"]

    # Create summary rows for 2PT and 3PT
    summary_stats = pd.DataFrame(
        {
            "Attempts": [len(two_pt_shots), len(three_pt_shots)],
            "FGPercent": [
                f"{(two_pt_shots['SHOT_MADE_FLAG'].mean() * 100):.1f}",
                f"{(three_pt_shots['SHOT_MADE_FLAG'].mean() * 100):.1f}",  # Fixed double colon
            ],
        },
        index=["2PT Field Goals", "3PT Field Goals"],
    )

    # Combine zone stats with summary stats
    zone_stats = pd.concat([zone_stats, summary_stats])

    # Reset index to make the zone names a column and rename columns
    zone_stats = zone_stats.reset_index()
    zone_stats.columns = ["Zone", "Attempts", "FG%"]

    return render_template(
        "index.html",
        plot=fig.to_html(),
        stats=zone_stats.to_html(classes="stats-table", index=False),
        players=active_players,
        selected_player=player_name,
        seasons=available_seasons,
        selected_season=season,
        games=available_games,
        selected_game=game_id,
    )

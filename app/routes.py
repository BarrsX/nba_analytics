# app/routes.py
from flask import Blueprint, render_template, request, jsonify, url_for
from .models import ShotChart
from .utils import draw_court  # Add this import
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
    season = request.args.get("season", "2015-16")
    game_id = request.args.get("game", None)

    # Get data availability status and players/seasons lists
    data_available = ShotChart.is_data_available(season)
    active_players = ShotChart.get_active_players()
    available_seasons = ShotChart.get_player_seasons(player_name)
    available_games = ShotChart.get_player_games(player_name, season)

    # First try to get shot location data
    shots_df, basic_stats = ShotChart.get_player_shots(player_name, season, game_id)

    # If we have basic stats but no shot locations (pre-1996 season)
    if shots_df.empty and basic_stats:
        fig = px.scatter(title=f"{player_name}'s Shot Chart ({season})")
        fig.update_layout(
            showlegend=False,
            xaxis=dict(
                showgrid=False, zeroline=False, showticklabels=False, showline=False
            ),
            yaxis=dict(
                showgrid=False, zeroline=False, showticklabels=False, showline=False
            ),
            paper_bgcolor="#1e1e1e",
            plot_bgcolor="rgba(0,0,0,0)",
            height=700,
            width=800,
        )

        # Create basic stats table
        stats_data = {
            "Zone": ["2PT Field Goals", "3PT Field Goals", "Free Throws"],
            "Made": [basic_stats["fg2m"], basic_stats["fg3m"], basic_stats["ftm"]],
            "Attempts": [basic_stats["fg2a"], basic_stats["fg3a"], basic_stats["fta"]],
            "FG%": [
                (
                    f"{(basic_stats['fg2m']/basic_stats['fg2a']*100):.1f}"
                    if basic_stats["fg2a"] > 0
                    else "0.0"
                ),
                (
                    f"{(basic_stats['fg3m']/basic_stats['fg3a']*100):.1f}"
                    if basic_stats["fg3a"] > 0
                    else "0.0"
                ),
                (
                    f"{(basic_stats['ftm']/basic_stats['fta']*100)::.1f}"
                    if basic_stats["fta"] > 0
                    else "0.0"
                ),
            ],
        }
        zone_stats = pd.DataFrame(stats_data)

        # Calculate totals for pre-1996 seasons
        total_shots = basic_stats["fg2a"] + basic_stats["fg3a"]
        total_points = (
            (basic_stats["fg2m"] * 2) + (basic_stats["fg3m"] * 3) + basic_stats["ftm"]
        )
        ts_percent = (
            (total_points / (2 * (total_shots + 0.44 * basic_stats["fta"]))) * 100
            if (total_shots + basic_stats["fta"]) > 0
            else 0
        )

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
            ts_percent=f"{ts_percent:.1f}",
            total_points=total_points,
            total_shots=total_shots,
            error_message="Shot location data is not available, showing basic statistics only.",
        )

    # Add data availability check
    data_available = ShotChart.is_data_available(season)
    error_message = (
        None
        if data_available
        else "Shot location data is only available from the 1996-97 season onwards."
    )

    active_players = ShotChart.get_active_players()
    available_seasons = ShotChart.get_player_seasons(player_name)
    available_games = ShotChart.get_player_games(player_name, season)
    shots_df, basic_stats = ShotChart.get_player_shots(player_name, season, game_id)

    # Handle pre-1996 seasons with basic stats
    if shots_df.empty and basic_stats:
        # Create empty plot with message
        fig = px.scatter(title=f"{player_name}'s Basic Stats ({season})")
        fig.update_layout(
            showlegend=False,
            xaxis=dict(
                showgrid=False, zeroline=False, showticklabels=False, showline=False
            ),
            yaxis=dict(
                showgrid=False, zeroline=False, showticklabels=False, showline=False
            ),
        )

        # Create basic stats table
        stats_data = {
            "Zone": ["2PT Field Goals", "3PT Field Goals", "Free Throws"],
            "Made": [basic_stats["fg2m"], basic_stats["fg3m"], basic_stats["ftm"]],
            "Attempts": [basic_stats["fg2a"], basic_stats["fg3a"], basic_stats["fta"]],
            "FG%": [
                (
                    f"{(basic_stats['fg2m']/basic_stats['fg2a']*100):.1f}"
                    if basic_stats["fg2a"] > 0
                    else "0.0"
                ),
                (
                    f"{(basic_stats['fg3m']/basic_stats['fg3a']*100):.1f}"
                    if basic_stats["fg3a"] > 0
                    else "0.0"
                ),
                (
                    f"{(basic_stats['ftm']/basic_stats['fta']*100):.1f}"
                    if basic_stats["fta"] > 0
                    else "0.0"
                ),
            ],
        }

        zone_stats = pd.DataFrame(stats_data)

        # Calculate totals
        total_shots = basic_stats["fg2a"] + basic_stats["fg3a"]
        total_points = (
            (basic_stats["fg2m"] * 2) + (basic_stats["fg3m"] * 3) + basic_stats["ftm"]
        )
        ts_percent = (
            (total_points / (2 * (total_shots + 0.44 * basic_stats["fta"]))) * 100
            if (total_shots + basic_stats["fta"]) > 0
            else 0
        )

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
            ts_percent=f"{ts_percent:.1f}",
            total_points=total_points,
            total_shots=total_shots,
            error_message="Shot location data is not available, showing basic statistics only.",
        )

    # Check if we have valid shot data
    if shots_df.empty:
        # Create empty plot with message
        message = (
            error_message
            if error_message
            else f"No shot data available for {player_name} ({season})"
        )
        fig = px.scatter(title=message)
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
            error_message=error_message,
        )

    # Create hover text with shot distance
    shots_df["SHOT_RESULT"] = shots_df["SHOT_MADE_FLAG"].map({1: "Made", 0: "Missed"})
    shots_df["HOVER_TEXT"] = (
        shots_df["SHOT_DISTANCE"].astype(str) + "ft - " + shots_df["SHOT_RESULT"]
    )

    # Update title to include game info if selected
    title = f"{player_name}'s Shot Chart ({season})"
    if game_id:
        game = next((g for g in available_games if g["id"] == game_id), None)
        if game:
            title += f" - {game['display']}"

    # Create scatter plot
    fig = px.scatter(
        shots_df,
        x="LOC_X",
        y="LOC_Y",
        color="SHOT_RESULT",
        color_discrete_map={
            "Made": "#2ecc71",  # Green for made shots
            "Missed": "#e74c3c",  # Red for missed shots
        },
        title=title,
        custom_data=["HOVER_TEXT"],
        hover_data=None,  # Disable default hover data
        labels={"LOC_X": "", "LOC_Y": ""},  # Remove axis labels
    )

    # Generate filename for downloads
    filename = f"{player_name.replace(' ', '_')}_{season}"
    if game_id:
        game = next((g for g in available_games if g["id"] == game_id), None)
        if game:
            filename += f"_{game['date']}"
    filename += "_shot_chart"

    # Add court image as background
    fig.add_layout_image(
        dict(
            source=url_for("static", filename="images/shot_chart.png"),
            xref="x",
            yref="y",
            x=-250,
            y=422.5,
            sizex=500,
            sizey=470,
            sizing="stretch",
            opacity=1,
            layer="below",
        )
    )

    # Update layout with proper dimensions (remove toImageButtonOptions)
    fig.update_layout(
        showlegend=True,
        legend_title_text="Shot Outcome",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            showline=False,
            range=[-250, 250],  # NBA coordinates are in tenths of feet
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            showline=False,
            range=[-47.5, 422.5],  # NBA coordinates are in tenths of feet
        ),
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        margin=dict(l=0, r=0, t=30, b=0),
        height=700,  # Fixed height
        width=800,  # Fixed width
    )

    # Create custom configuration for downloads
    config = {
        "toImageButtonOptions": {
            "filename": filename,
            "height": 700,
            "width": 800,
            "scale": 2,  # Higher quality image
        }
    }

    # Update markers and hover template
    fig.update_traces(
        selector=dict(name="Made"),
        marker=dict(symbol="circle", size=10, line=dict(width=1, color="white")),
        hovertemplate="%{customdata[0]}<extra></extra>",  # Show only custom hover text
    )

    fig.update_traces(
        selector=dict(name="Missed"),
        marker=dict(symbol="x", size=10, line=dict(width=1, color="white")),
        hovertemplate="%{customdata[0]}<extra></extra>",  # Show only custom hover text
    )

    # Get number of games for per-game calculations
    num_games = len(set(shots_df["GAME_ID"])) if not game_id else 1

    # Calculate shot types first
    two_pt_shots = shots_df[shots_df["SHOT_TYPE"] == "2PT Field Goal"]
    three_pt_shots = shots_df[shots_df["SHOT_TYPE"] == "3PT Field Goal"]

    # Calculate zone statistics with better column names
    zone_stats = (
        shots_df[shots_df["SHOT_ZONE_BASIC"] != "Backcourt"]
        .groupby("SHOT_ZONE_BASIC")
        .agg(
            Made=("SHOT_MADE_FLAG", "sum"),
            Attempts=("SHOT_MADE_FLAG", "count"),
            FGPercent=("SHOT_MADE_FLAG", lambda x: f"{(x.mean() * 100):.1f}"),
        )
    ).reset_index()
    zone_stats.columns = ["Zone", "Made", "Attempts", "FG%"]

    # Add per-game stats if showing all games
    if not game_id:
        zone_stats["Made"] = zone_stats.apply(
            lambda row: f"{row['Made']} ({(row['Made']/num_games):.1f}/game)", axis=1
        )
        zone_stats["Attempts"] = zone_stats.apply(
            lambda row: f"{row['Attempts']} ({(row['Attempts']/num_games):.1f}/game)",
            axis=1,
        )

    # Create summary rows for 2PT and 3PT
    if not game_id:
        summary_stats = pd.DataFrame(
            {
                "Zone": ["2PT Field Goals", "3PT Field Goals"],
                "Made": [
                    f"{two_pt_shots['SHOT_MADE_FLAG'].sum()} ({(two_pt_shots['SHOT_MADE_FLAG'].sum()/num_games):.1f}/game)",
                    f"{three_pt_shots['SHOT_MADE_FLAG'].sum()} ({(three_pt_shots['SHOT_MADE_FLAG'].sum()/num_games):.1f}/game)",
                ],
                "Attempts": [
                    f"{len(two_pt_shots)} ({(len(two_pt_shots)/num_games):.1f}/game)",
                    f"{len(three_pt_shots)} ({(len(three_pt_shots)/num_games):.1f}/game)",
                ],
                "FG%": [
                    f"{(two_pt_shots['SHOT_MADE_FLAG'].mean() * 100):.1f}",
                    f"{(three_pt_shots['SHOT_MADE_FLAG'].mean() * 100):.1f}",
                ],
            }
        )
    else:
        summary_stats = pd.DataFrame(
            {
                "Zone": ["2PT Field Goals", "3PT Field Goals"],
                "Made": [
                    two_pt_shots["SHOT_MADE_FLAG"].sum(),
                    three_pt_shots["SHOT_MADE_FLAG"].sum(),
                ],
                "Attempts": [
                    len(two_pt_shots),
                    len(three_pt_shots),
                ],
                "FG%": [
                    f"{(two_pt_shots['SHOT_MADE_FLAG'].mean() * 100):.1f}",
                    f"{(three_pt_shots['SHOT_MADE_FLAG'].mean() * 100)::.1f}",
                ],
            }
        )

    # Get free throw data
    fta, ftm = ShotChart.get_player_free_throws(player_name, season, game_id)

    # Create free throw row with swapped column order
    if not game_id:
        ft_stats = pd.DataFrame(
            {
                "Zone": ["Free Throws"],
                "Made": [f"{ftm} ({(ftm/num_games):.1f}/game)"],
                "Attempts": [f"{fta} ({(fta/num_games):.1f}/game)"],
                "FG%": [f"{(ftm/fta * 100):.1f}" if fta > 0 else "0.0"],
            }
        )
    else:
        ft_stats = pd.DataFrame(
            {
                "Zone": ["Free Throws"],
                "Made": [ftm],
                "Attempts": [fta],
                "FG%": [f"{(ftm/fta * 100):.1f}" if fta > 0 else "0.0"],
            }
        )

    # Combine all stats
    zone_stats = pd.concat([zone_stats, summary_stats, ft_stats], ignore_index=True)

    # Calculate final totals
    total_shots = len(shots_df)
    made_shots = shots_df["SHOT_MADE_FLAG"].sum()
    total_points = (
        (two_pt_shots["SHOT_MADE_FLAG"].sum() * 2)
        + (three_pt_shots["SHOT_MADE_FLAG"].sum() * 3)
        + ftm
    )

    # Calculate True Shooting %
    ts_percent = (
        (total_points / (2 * (total_shots + 0.44 * fta))) * 100
        if (total_shots + fta) > 0
        else 0
    )

    # Pass the config when converting to HTML
    return render_template(
        "index.html",
        plot=fig.to_html(config=config),  # Add config here
        stats=zone_stats.to_html(classes="stats-table", index=False),
        players=active_players,
        selected_player=player_name,
        seasons=available_seasons,
        selected_season=season,
        games=available_games,
        selected_game=game_id,
        ts_percent=f"{ts_percent:.1f}",
        total_points=total_points,
        total_shots=total_shots,
    )

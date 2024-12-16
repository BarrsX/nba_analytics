# app/models.py
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players
import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import playerdashptshots
from nba_api.stats.endpoints import playercareerstats  # Add this import


class ShotChart:
    # League-wide shot tracking start dates
    SHOT_TRACKING_START = {
        "detailed": "1996-97",  # Detailed shot location data
        "basic": "1983-84",  # Basic shot data without locations
    }

    @staticmethod
    def get_player_shots(player_name, season="2023-24", game_id=None):
        try:
            # Get basic stats if before shot tracking era
            season_year = int(season.split("-")[0])
            if season_year < 1996:
                return pd.DataFrame(), ShotChart.get_basic_stats(
                    player_name, season, game_id
                )

            players_list = players.find_players_by_full_name(player_name)
            if not players_list:
                raise ValueError(f"Player {player_name} not found")

            player_dict = players_list[0]
            player_id = player_dict["id"]

            shot_chart = shotchartdetail.ShotChartDetail(
                team_id=0,
                player_id=player_id,
                season_nullable=season,
                context_measure_simple="FGA",
                game_id_nullable=game_id,
            )
            return shot_chart.get_data_frames()[0], None

        except Exception as e:
            print(f"Error getting shot chart: {e}")
            return (
                pd.DataFrame(),
                None,
            )  # Return empty DataFrame and no basic stats on error

    @staticmethod
    def get_basic_stats(player_name, season, game_id=None):
        """Get basic shooting stats without shot locations for older seasons"""
        try:
            players_list = players.find_players_by_full_name(player_name)
            if not players_list:
                return None

            player_dict = players_list[0]
            player_id = player_dict["id"]

            # Get career stats
            career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
            season_stats = career_stats.get_data_frames()[0]

            # Filter for requested season
            season_data = season_stats[
                season_stats["SEASON_ID"] == f"2{season.replace('-', '')}"
            ]

            if season_data.empty:
                return None

            stats = {
                "fg2m": int(season_data["FGM"].iloc[0] - season_data["FG3M"].iloc[0]),
                "fg2a": int(season_data["FGA"].iloc[0] - season_data["FG3A"].iloc[0]),
                "fg3m": int(season_data["FG3M"].iloc[0]),
                "fg3a": int(season_data["FG3A"].iloc[0]),
                "ftm": int(season_data["FTM"].iloc[0]),
                "fta": int(season_data["FTA"].iloc[0]),
                "games": int(season_data["GP"].iloc[0]),
            }

            return stats

        except Exception as e:
            print(f"Error getting basic stats: {e}")
            return None

    @staticmethod
    def is_data_available(season):
        """Check if detailed shot data is available for given season"""
        try:
            season_year = int(season.split("-")[0])
            return season_year >= 1996
        except:
            return False

    @staticmethod
    def get_active_players():
        try:
            # Get all players from NBA API
            all_players = players.get_players()
            # Sort by name, include all players
            return sorted(all_players, key=lambda x: x["full_name"])
        except Exception as e:
            print(f"Error fetching players: {e}")
            return []

    @staticmethod
    def get_player_seasons(player_name):
        try:
            players_list = players.find_players_by_full_name(player_name)
            if not players_list:
                return []

            player_dict = players_list[0]
            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_dict["id"])
            headers = player_info.get_data_frames()[0]

            from_year = int(headers["FROM_YEAR"].iloc[0])
            to_year = int(headers["TO_YEAR"].iloc[0])

            seasons = []
            for year in range(from_year, to_year + 1):
                season = f"{year}-{str(year + 1)[-2:]}"
                seasons.append(season)

            return list(reversed(seasons))  # Most recent first
        except Exception as e:
            print(f"Error getting player seasons: {e}")
            return []

    @staticmethod
    def get_player_games(player_name, season):
        try:
            players_list = players.find_players_by_full_name(player_name)
            if not players_list:
                return []

            player_dict = players_list[0]
            game_log = playergamelog.PlayerGameLog(
                player_id=player_dict["id"], season=season
            )
            games_df = game_log.get_data_frames()[0]

            # Format games for dropdown with points
            games = []
            for _, game in games_df.iterrows():
                game_info = {
                    "id": game["Game_ID"],
                    "date": game["GAME_DATE"],
                    "matchup": game["MATCHUP"],
                    "display": f"{game['GAME_DATE']} - {game['MATCHUP']} ({game['PTS']} pts)",
                }
                games.append(game_info)

            return games

        except Exception as e:
            print(f"Error getting player games: {e}")
            return []

    @staticmethod
    def get_player_free_throws(player_name, season, game_id=None):
        try:
            players_list = players.find_players_by_full_name(player_name)
            if not players_list:
                return 0, 0  # FTA, FTM

            player_dict = players_list[0]
            player_id = player_dict["id"]

            # Get game log data
            game_log = playergamelog.PlayerGameLog(
                player_id=player_dict["id"], season=season
            )
            games_df = game_log.get_data_frames()[0]

            if game_id:
                # Get specific game stats
                game_stats = games_df[games_df["Game_ID"] == game_id]
                if game_stats.empty:
                    return 0, 0
                return game_stats["FTA"].iloc[0], game_stats["FTM"].iloc[0]
            else:
                # Get season totals
                return games_df["FTA"].sum(), games_df["FTM"].sum()

        except Exception as e:
            print(f"Error getting free throws: {e}")
            return 0, 0

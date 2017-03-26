import os

import numpy as np
import pandas as pd


def load_season(season):
    fname = (
        os.path.dirname(__file__) +
        'data/match_probabilities/{}.csv'.format(season)
    )
    return pd.read_csv(fname)


def get_away_points(simulated_home_points):
    points_mapping = {
        # home: away points
        3: 0,
        1: 1,
        0: 3
    }

    simulated_away_points = np.copy(simulated_home_points)
    for h, a in points_mapping.items():
        simulated_away_points[simulated_home_points == h] = a

    return simulated_away_points


def simulate_games(games, n_sims=int(1e4)):
    n_games = len(games)

    simulated_home_points = np.zeros([n_games, n_sims])

    for ix, game in games.iterrows():
        points = (3, 1, 0)
        probabilites = (
            game['home_win_prob'],
            game['draw_prob'],
            game['away_win_prob']
        )

        simulated_home_points[ix, :] = np.random.choice(
            points,
            n_sims,
            True,
            probabilites
        )

    simulated_away_points = get_away_points(simulated_home_points)

    return simulated_home_points, simulated_away_points


def rank(a):
    len_x = a.shape[0]

    # Break ties randomly
    tiebreak = np.random.random(a.shape)

    a_ranked = len_x - np.lexsort([tiebreak, a], axis=0).argsort(axis=0)
    return np.where(a_ranked > 20, 0, a_ranked)


def season_rank(
    games,
    simulated_home_points,
    simulated_away_points,
    team_id_list
):
    n_sims = simulated_home_points.shape[1]
    season_points = np.zeros([max(team_id_list) + 1, n_sims])

    for t in team_id_list:
        home_games = (
            games
            .loc[lambda df: df['home_team_id'] == t]
            ['row_ix']
        )

        away_games = (
            games
            .loc[lambda df: df['away_team_id'] == t]
            ['row_ix']
        )

        team_home_points = simulated_home_points[home_games, :].sum(axis=0)
        team_away_points = simulated_away_points[away_games, :].sum(axis=0)
        team_points = team_home_points + team_away_points

        season_points[t, :] = team_points

    season_position = rank(season_points)

    return season_position


def gen_position_probabilities(season_position, team_id_list):
    for team_id in team_id_list:
        position_counts = np.bincount(season_position[team_id, :])
        for p, cnt in enumerate(position_counts):
            yield {
                'team_id': team_id,
                'position': p,
                'percent': cnt / sum(position_counts)
            }

def melt_simarray(simarray, value_name):
    return pd.melt(
        pd.DataFrame(simarray)
        .assign(team_id=lambda df: df.index),
        id_vars='team_id',
        var_name='simulation_id',
        value_name='position'
    )


def simulate_season(games, n_sim, team_id_list, season):
    season_name = str(season) + '/' + str(season + 1)[-2:]

    home_points, away_points = simulate_games(
        games,
        n_sim
    )

    season_positions = season_rank(
        games,
        home_points,
        away_points,
        team_id_list
    )

    raw_simulations = melt_simarray(season_positions, 'points')
    raw_simulations['season_id'] = season
    raw_simulations['season'] = season_name

    positions_df = pd.DataFrame(
        gen_position_probabilities(season_positions, team_id_list)
    )
    positions_df['season_id'] = season
    positions_df['season'] = season_name

    return positions_df, raw_simulations


def run():
    min_season = 2004
    max_season = 2015

    # Load data from files
    team_names = pd.read_csv(os.path.dirname(__file__) + 'data/teams.csv')
    data = {s: load_season(s) for s in range(min_season, max_season + 1)}
    team_ids = tuple(
        pd.concat([df['home_team_id'] for df in data.values()]).unique()
    )

    # Run the simulations
    n = int(1e4)
    simulations = [simulate_season(g, n, team_ids, s) for s, g in data.items()]

    # Write positions output to csv
    all_positions = pd.concat(
        positions for positions, __ in simulations
    )
    positions_fname = os.path.dirname(__file__) + 'data/positions.csv'
    all_positions.merge(team_names).to_csv(positions_fname, index=False)

    # Write raw simulation output to csv
    all_simulations = pd.concat(
        sim for __, sim in simulations
    )
    simulations_fname = os.path.dirname(__file__) + 'data/simulations.csv'
    all_simulations.merge(team_names).to_csv(simulations_fname, index=False)

if __name__ == '__main__':
    run()

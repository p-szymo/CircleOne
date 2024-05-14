# HELPER DICTIONARIES

def event_table_dict():
    return {
        'EventID': 'bigint',
        'PlayerID': 'bigint',
        'Place': 'int',
        'Score': 'varchar(10)'
    }


def player_table_dict():
    return {
        'PlayerID': 'bigint',
        'PlayerName': 'varchar(200)',
        'PlayerRating': 'int',
        'PlayerURL': 'varchar(500)',
        'IsActive': 'boolean',
        'IsOnTeam': 'boolean'
    }


def league_table_dict():
    return {
        'Team Name': 'varchar(100)',
        'Team Owner': 'varchar(100)',
        'Number of Players': 'int',
        'Number of Active Players': 'int',
        'Wins': 'int',
        'Losses': 'int',
        'Ties': 'int',
        'First Place': 'int',
        'Second Place': 'int',
        'Third Place': 'int',
    }
# HELPER DICTIONARIES

def event_table_dict():
    return {
        'Place': 'int',
        'Player': 'varchar(200)',
        'PDGA Number': 'bigint',
        'Player Rating': 'int',
        'Score': 'varchar(10)'
    }


def player_table_dict():
    return {
        'Name': 'varchar(200)',
        'PDGA Number': 'bigint',
        'Event Name': 'varchar(500)',
        'Place': 'int',
        'Event Year': 'int',
        'Event Status': 'varchar(50)'
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
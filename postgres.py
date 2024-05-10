import psycopg2
import creds

def connect_to_sql():

    connection = psycopg2.connect(
        host='localhost',
        database='dg_fantasy',
        port=5432,
        # user='postgres',
        # password=creds.pg_pass()
    )

    executor = connection.cursor()

    return connection, executor


def close_connection(connection, executor):

    executor.close()
    connection.commit()
    connection.close()

    return None


def insert_event(event, to_print=False):

    connection, postgres = connect_to_sql()

    postgres.execute(event.table_exists_query)

    if not postgres.fetchone():
        if to_print:
            print(f'Table named "{event.table_name}" does not exist.')
        postgres.execute(event.create_table_query)

    else:
        if to_print:
            print(f'Table named "{event.table_name}" already exists.')
        pass

    postgres.execute(event.insert_values_query)

    if to_print:
        print(f'Values inserted into "{event.table_name}" table.')

    close_connection(connection, postgres)

    return None

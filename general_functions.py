import requests
from bs4 import BeautifulSoup as bs
import pandas as pd


def soupify(url, _type="html.parser"):
    page = requests.get(url)
    soup = bs(page.content, _type)
    return soup


def type_check(item, _type):
    if type(item) != _type:
        raise TypeError(f'{item} must be type {_type}')
    else:
        pass


def table_exists(table_name):
    table_name = table_name.replace("'", "''")

    table_exists_query = f"""SELECT 1
FROM information_schema.tables
WHERE table_name='{table_name}'"""

    return table_exists_query


def create_table(table_name, table_columns):
    columns_list = [f'"{column}" {datatype}' for column, datatype in table_columns.items()]
    columns_query = ',\n\t'.join(columns_list)

    create_table_query = f'''CREATE TABLE "{table_name}" (
    {columns_query}
);'''

    return create_table_query


def insert_data(table_name, table_columns, data, truncate=True):
    column_names = table_columns.keys()

    insert_list = []

    for i, _dict in enumerate(data):

        data_to_insert = []

        for column_name, datum in _dict.items():
            if "varchar" in table_columns[column_name]:
                datum = "'" + datum.replace("'", "''") + "'"

            data_to_insert.append(str(datum))

        insert_list.append('(' + ','.join(data_to_insert) + ')')

    insert_values = '\n\t,'.join(insert_list) + '\n;'

    if truncate:

        insert_query = f'''TRUNCATE TABLE "{table_name}";

'''

    else:
        insert_query = ''

    columns_for_query = [f'"{c}"' for c in column_names]

    insert_query += f'''INSERT INTO "{table_name}" ({",".join(columns_for_query)})
VALUES {insert_values}'''

    return insert_query


def second_tuesdays(start_date='2024-01-01', end_date='2029-12-31'):

    df = pd.DataFrame(
        {'Date': pd.date_range(start=start_date, end=end_date, freq='d')}
    )

    df['is_second_tuesday'] = (
            (df['Date'].dt.weekday == 1) &  # select Tuesday
            (df['Date'].dt.day > 7) &  # exclude first
            (df['Date'].dt.day <= 14)  # exclude third etc.
    )

    return list(df['Date'][df['is_second_tuesday']].values)


print(second_tuesdays())
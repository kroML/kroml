import pandas as pd
import cx_Oracle
import psycopg2
import mysql.connector
from iostrategies.input_db.loader_pd import Loader
from utils.logger import Logger
import io


logger = Logger(__name__)
@logger.for_all_methods(in_args=True)
class DBLoader(Loader):

    def load(self, input_database: dict) -> None:
        """
        Function connects to chosen type of the database with data from input dictionary. Afterwards function prepares
        select query and read data from database. Requested columns and rows are stored as dataframe in variables.

        :param dict input_database: Dictionary that contains data necessary for establishing connection to database.
        :return None: No return value
        """
        if input_database.get('type').lower() == 'postgresql':
            connection = psycopg2.connect(database=input_database['db_name'], user=input_database['user'],
                                          password=input_database['password'], host=input_database['url'],
                                          port=input_database['port'])
        elif input_database.get('type').lower() == 'mysql':
            connection = mysql.connector.connect(database=input_database['db_name'], user=input_database['user'],
                                                 password=input_database['password'], host=input_database['url'],
                                                 port=input_database['port'])
        elif input_database.get('type').lower() == 'oracle':
            connection = cx_Oracle.connect(user=input_database['user'],
                                           password=input_database['password'],
                                           dsn='{}:{}/{}'.format(input_database['url'],
                                                                 input_database['port'],
                                                                 input_database['sid']))
        else:
            logger.warning('Database type "{}" not recognized.'.format(input_database.get('type')), created_by='system')
            return

        for query_name in input_database.get('query'):
            query_values = self.config.get_attr('queries').get(query_name)
            if query_values.get('format_strategy') in self.config.get_attr('input_strategies'):
                original_names, rename_names = self.get_columns_names(query_values.get('format_strategy'))
                query = 'select {} from {} where {}'.format(','.join(original_names), query_values.get('table'),
                                                            query_values.get('condition', 'True'))
                df = DBLoader.read_sql_iostream(query=query, con=connection)
                df.rename(columns=rename_names, inplace=True)
            else:
                query = 'select {} from {} where {}'.format('*', query_values.get('table'),
                                                            query_values.get('condition', 'True'))
                df = DBLoader.read_sql_iostream(query=query, con=connection)
            self.variables.set_object(key=query_values['variable_name'], obj=df)
        connection.close()

    @staticmethod
    def read_sql_iostream(query: str,
                          con: cx_Oracle.connect or psycopg2.connect or  mysql.connector.connect) -> pd.DataFrame:
        """
        More effective way of loading content of database table to dataframe using io stream - StringIO.

        :param str query: Query select for accessing data in table.
        :param con: Connection to concrete database.
        :return pd.Dataframe: Output dataframe loaded from database.
        """
        copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
            query=query, head="HEADER"
        )
        cur = con.cursor()
        store = io.StringIO()
        cur.copy_expert(copy_sql, store)
        store.seek(0)
        df = pd.read_csv(store)
        return df

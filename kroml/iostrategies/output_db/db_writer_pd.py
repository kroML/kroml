import pandas as pd
from iostrategies.output_db.writer_pd import Writer
from utils.logger import Logger
import sqlalchemy
import io

logger = Logger(__name__)


@logger.for_all_methods(in_args=True)
class DBWriter(Writer):

    def write(self, output_database: dict) -> None:
        """
        Function that provides recognition of output database, connection and writing content of dataframe into it.
         It also renames names of column if format strategy is available and writing only visible columns.

        :param dict output_database: Dictionary where are stored details about output database like its name, type,
        parameters for connecting to database and format strategy for column mapping.
        :return None: no return value
        """

        db_name = str(output_database.get('type')).lower()

        if db_name not in ['postgresql', 'mysql', 'oracle']:
            logger.warning('Database type "{}" not recognized.'.format(output_database.get('type')),
                           created_by='system')
            return None

        # establishing database connection with SQLAlchemy Engine
        engine = sqlalchemy.create_engine(
            '{}://{}:{}@{}:{}/{}'.format(db_name, output_database['user'], output_database['password'],
                                         output_database['url'], output_database['port'],
                                         output_database['db_name']))

        # writing dataframe to sql database
        for query_name in output_database.get('query'):
            if query_name in self.config.query:
                query_values = self.config.get_attr('queries').get(query_name)
                if self.variables.get_object(key=query_values['variable_name']) is not None:

                    if query_values.get('format_strategy') in self.config.get_attr('output_strategies'):
                        final_names, rename_names = super().get_columns_names(query_values.get('format_strategy'))
                        df = self.variables.get_object(key=query_values.get('variable_name')).rename(
                            columns=rename_names)
                        df = df[df.columns.intersection(final_names)]
                        # replace Nan with None so SQL can convert it to Null
                        df = df.replace({pd.np.nan: None})
                    else:
                        df = self.variables.get_object(key=query_values.get('variable_name'))
                    DBWriter.write_iostream_to_database(engine=engine, tablename=query_values['table'],
                                                        dataframe=df)

    @staticmethod
    def write_iostream_to_database(engine: sqlalchemy.engine.Engine, tablename: str,
                                   dataframe: pd.DataFrame) -> None:
        """
        More effective way of saving dataframe into database using io stream - StringIO.

        :param sqlalchemy.engine.Engine engine: SQL Alchemy engine for connection to databse.
        :param str tablename: Name of the table in database, where will be content of dataframe appended.
        :param pd.Datafram dataframe: Dataframe, whose content will be appended to databse.
        :return None: No return value.
        """

        store = io.StringIO()

        dataframe.to_csv(store, index=False, header=False)
        store.seek(0)

        conn = engine.connect().connection
        cursor = conn.cursor()
        cursor.copy_from(store, tablename, columns=dataframe.columns, sep=',', null='null')
        conn.commit()
        conn.close()

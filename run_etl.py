import pandas as pd
import os
import tqdm
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from metrics import *

class Base(DeclarativeBase):
    pass

class Country(Base):
    """Class that models the countries table in the database"""
    __tablename__ = 'countries'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    flag: Mapped[str] = mapped_column(nullable=False, unique=True)
    population: Mapped[int] = mapped_column(nullable=False)
    currencies: Mapped[str] = mapped_column(nullable=False)
    languages: Mapped[str] = mapped_column(nullable=False)
    continents: Mapped[str] = mapped_column(nullable=False)
    capitals: Mapped[str] = mapped_column(nullable=False)

# Creates all tables in the database if they don't already exist
def create_tables(engine):
    """Creates the postgresql tables if they don't exist
    Args:
        engine (sqlalchemy.engine.base.Engine): The sqlalchemy engine
    """
    db_connection = engine.connect()
    if not engine.dialect.has_table(db_connection, "countries"):
        print("Creating tables...")
        """Using sqlalchemy to create the tables. 
        This takes all the classes that inherit from Base and creates the tables"""
        Base.metadata.create_all(engine)

def api_to_df(json_response):
    """Creates a pandas df from the api response only taking 
    the columns we need (name, flag, population, currencies, languages, continents, capitals)
    Args:
        json_response (dict): The response from the api
    Returns:
        pandas.DataFrame: The dataframe with the data we need
    """
    data_to_insert = []
    for entry in json_response:
        """The columns that have multiple values are joined with a comma 
        so that they can be inserted into the database as a string"""
        data = {
            "name": entry["name"]["common"],
            "capitals": ",".join(entry.get("capital", [])),
            "currencies": ",".join(entry.get("currencies", {})),
            "languages": ",".join(entry.get("languages", {}).values()),
            "flag": entry["flags"]["png"],
            "population": entry.get("population", None),
            "continents": ",".join(entry.get("continents", []))
        }
        data_to_insert.append(data)
    return pd.DataFrame(data_to_insert)

def fill_database(engine, df):
    """Inserts the data into the database
    Args:
        engine (sqlalchemy.engine.base.Engine): The sqlalchemy engine
        df (pandas.DataFrame): The dataframe with the data to insert
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    progress_bar = tqdm.tqdm(total=len(df), desc="Filling database")
    failed_inserts = 0

    for idx, row in df.iterrows():
        country = {
            "name":row["name"].lower(),
            "flag":row["flag"],
            "population":row["population"],
            "currencies":row["currencies"].lower(),
            "languages":row["languages"].lower(),
            "continents":row["continents"].lower(),
            "capitals":row["capitals"].lower()
        }
        """Checks if the row is already in the database, if it is, it skips it"""
        query = session.query(Country).filter(Country.name == country["name"])
        if query.first() is not None:
            progress_bar.update(1)
            continue
        """Tries to insert the row into the database. 
        If it fails, it rolls back the transaction and increments the failed_inserts counter"""
        try: 
            session.add(Country(**country))
            session.commit()
        except:
            session.rollback()
            failed_inserts += 1
            continue
        progress_bar.update(1)

    session.close()

    if failed_inserts > 0:
        print(f"Failed to insert {failed_inserts} rows")

if __name__ == "__main__":
    """Loads the environment variables from the .env file. 
    This is so that the api_url and postgresql_url can be changed without having to change the code"""
    load_dotenv()
    api_url = os.getenv("API_URL")
    postgresql_url = os.getenv("POSTGRESQL_URL")

    response = requests.get(api_url)
    df = api_to_df(response.json())
    
    engine = create_engine(postgresql_url)
    create_tables(engine)

    #TODO: Check if the data is already in the database
    fill_database(engine, df)

    calculate_metrics(df)

    """Writes the rows that were inserted into the database into an excel file"""
    df.to_excel("countries.xlsx", sheet_name="Paises", index=False)


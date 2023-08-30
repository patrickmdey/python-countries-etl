from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
import pandas as pd
import requests
import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Base(DeclarativeBase):
    pass

class Country(Base):
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
    db_connection = engine.connect()
    if not engine.dialect.has_table(db_connection, "countries"):
        print("Creating tables...")
        Base.metadata.create_all(engine)

def api_to_df(json_response):
    # Gets only the needed data from the API response
    data_to_insert = []
    for entry in json_response:
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
    Session = sessionmaker(bind=engine)
    session = Session()
    progress_bar = tqdm.tqdm(total=len(df), desc="Inserting data into challenge_db")
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
    api_url = "https://restcountries.com/v3.1/all"
    postgresql_url = "postgresql://postgres:postgres@127.0.0.1:5432/challenge_db"

    response = requests.get(api_url)
    df = api_to_df(response.json())
    
    engine = create_engine(postgresql_url)
    create_tables(engine)

    #TODO: Check if the data is already in the database
    fill_database(engine, df)

    df.to_excel("countries.xlsx", sheet_name="Paises", index=False)


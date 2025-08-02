from dotenv import load_dotenv
import os
import mysql.connector
import pandas as pd

load_dotenv()

#Database connections
class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        self.cursor = self.connection.cursor()

        db_name = "cricsheet_db"
        query = f"CREATE DATABASE IF NOT EXISTS {db_name}"
        self.cursor.execute(query)
        self.connection.commit()

        self.connection.database = db_name

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()

    
    def executemany(self, query, data): 
        self.cursor.executemany(query, data)
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

#Tables_creation
def create_tables():
    db = Database()
    match_types = ["Test_Match", "ODI_Match", "T20_Match", "IPL_Match"]

    for match_type in match_types:
        query = f'''
            CREATE TABLE IF NOT EXISTS {match_type}(
                id INT AUTO_INCREMENT PRIMARY KEY, 
                match_id VARCHAR(20), season VARCHAR(20), teams VARCHAR(255),
                team_1 VARCHAR(100), team_2 VARCHAR(100), venue VARCHAR(100), city VARCHAR(100),
                toss_winner VARCHAR(100), toss_decision VARCHAR(20), match_winner VARCHAR(100),
                win_by_runs INT, player_of_match VARCHAR(100), match_date DATE, match_number VARCHAR(20),
                inning INT, over_number INT, batsman VARCHAR(100), bowler VARCHAR(100),
                runs_batsman INT, runs_total INT
            )
        '''
        db.execute(query)

    print('tables and database created sucessfully.......')
    db.close_connection()

#Data_insertion
def insert_data():
    db = Database()
    match_types = {
        "test_matches.csv": "Test_Match",
        "odi_matches.csv": "ODI_Match",
        "t20_matches.csv": "T20_Match",
        "ipl_matches.csv": "IPL_Match"
    }

    for file_name, match_type in match_types.items():
        file_path = f"processed_data/{file_name}"

        df = pd.read_csv(file_path, dtype={"season": str}, low_memory=False)

        df["match_id"] = df["match_id"].astype(str)
        df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
        df["player_of_match"] = df["player_of_match"].fillna("Unknown")
        df["city"] = df["city"].fillna("Unknown")

        df = df.replace({pd.NA: None, "nan": None, "NaN": None, float("nan"): None})


        expected_columns = [
            "match_id", "season", "teams", "team_1", "team_2", "venue", "city",
            "toss_winner", "toss_decision", "match_winner", "win_by_runs",
            "player_of_match", "match_date", "match_number", "inning",
            "over_number", "batsman", "bowler", "runs_batsman", "runs_total"
        ]
        df = df[expected_columns]  # Ensure correct column order

        batch_size = 50000
        data = [tuple(row) for row in df.itertuples(index=False, name=None)]

        try:
            for i in range(0, len(data), batch_size):
                batch = data[i : i + batch_size]
                query = f"""
                    INSERT INTO {match_type} ({", ".join(expected_columns)})
                    VALUES ({", ".join(["%s"] * len(expected_columns))})
                """
                db.executemany(query, batch)
            print(f"Successfully inserted {len(df)} rows into {match_type}")

        except mysql.connector.Error as e:
            print(f"Error inserting into {match_type}: {e}")

    db.close_connection()
    print("All data inserted successfully")

if __name__ == "__main__":
    create_tables()
    insert_data()

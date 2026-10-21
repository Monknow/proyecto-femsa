import os 
import logging
import pandas as pd
import pandera as pa
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHnadler('uplaod_history.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST') 
port = os.getenv('DB_PORT')
db = os.getenv('DB_NAME')

# SQLAlchemy connection string for PostgreSQL
connection_string = f'postgresql+psycopg://{user}:{password}@{host}:{port}/{db}?sslmode=require'
engine = create_engine(connection_string)

# Data validation shcema
excel_schema = pd.DataFrame({

})

def upload_excel(file_path, table_name, unique_column):
    if not os.path.exists(file_path):
        logging.error(f"Error: The file '{file_path}' does not exist.")
        return
    
    try:
        logging.info(f"Reading '{file_path}'...")
        df = pd.read_excel(file_path)

        df.dropna(how='all', inplace=True)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        #logging.info('Validating data...')
        #df = excel_schema.validate(df)

        logging.info('Uploading to staging table...')
        temp_table = f"temp_staging_{table_name}"

        # Temporary table
        df.to_sql(temp_table, engine, if_exists='replace', index=False)
        # Dynamic SQL to merge stating into main table 
        columns = ", ".join(df.columns)
        # Update every column except unique ID if a duplicate is found 
        updates = ", ".join([f"{col} = EXCLUDED.{col}" for col in df.columns if col !=  unique_column])

        merge_sql = text(f"""
            INSERT INTO {table_name} ({columns})
            SELECT {columns} FROM {temp_table}
            ON CONFLICT ({unique_column})
            DO UPDATE SET {updates};
            """)

        # Execute the merge and safely clean up the temp table 
        with engine.begin() as conn:
            conn.execute(merge_sql)
            conn.execute(text(f"DROP TABLE {temp_table};"))

        logging.info(f"Data cleanly merged into '{table_name}'. Duplicates updated.")

    except pa.errors.SchemaError as e:
        logging.error(f"Data Validation Error: Check Excel file.\nDetails: {e}")
    except Exception as e:
        logging.error(f"Database Error occurred: {e}")

if __name__ == '__main__':
    target_file = input("Enter the name of the Excel file: ") or 'data.xlsx'
    user_chosen_name = input("Enter the name of the table to save the data: ") or 'data_table'
    if user_chosen_name:
        upload_excel(target_file, user_chosen_name, unique_column='')
    else: 
        logging.error('You must provide a table name')
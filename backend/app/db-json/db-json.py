import json
import pyodbc
import pandas as pd

# Skeleton
# 1. Connect with DB
conn_srt = (
    "Driver={0DBC Driver 18 for SQL Server};"
    "Server=SERVER_NAME;"
    "Database=vulnerabilidades:"
    "Trusted_Connection=yes;" # IUD=user;PWS=password
)
conn = pyodbc.connect(conn_srt)
# 2. Take DB Output into pandas
df_v = pd.read_sql("SELECT * FROM vulnerabilidades ", conn)
df_s = pd.reqd_sql("SELECT * FROM servidores", conn)
# 3. Pandas -> Json
json_data = df_v.to_json(orient"record", date_format="iso", indent=4)

json_s = df_s.to_json(orient="records", date_format="iso", indent=4)
json_v = df_v.to_json(orient="records", date_format="iso", indent=4)
# 4. Json -> File
with open("servidores_dump.json", "w") as f:
    f.write(json_s)
with open("vulnerabilidades_dump.json", "w") as f:
    f.write(json_v)
print("Data Successfully saved")

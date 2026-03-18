import pandas as pd
import requests

url = "https://www.datos.gov.co/resource/hp9r-jxuu.json"
response = requests.get(url, params={"$limit": int(1e13)})
data = pd.DataFrame.from_records(response.json())
# print(data.keys())
print(data)

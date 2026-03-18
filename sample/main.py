import matplotlib.pyplot as plt
import pandas as pd
import requests

url = "http://aquariuswebportal.ideam.gov.co/Data/DatasetGrid"

params = {
    "dataset": 514044,
    "sort": "TimeStamp-desc",
    "page": 1,
    "pageSize": int(1e13),
    "interval": "Latest",
    "timezone": -300,
    "alldata": "true",
    "virtual": "true",
}

r = requests.get(url, params=params)
df = pd.DataFrame(r.json()["Data"])
df["TimeStamp"] = pd.to_datetime(df["TimeStamp"])
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
print(df.info())
print(df)
df.plot(x="TimeStamp", y="Value", figsize=(10, 6), title="Aquarius Data")
plt.show()

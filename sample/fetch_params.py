import pandas as pd
from aquarius_webportal import AquariusWebPortal

wp = AquariusWebPortal("http://aquariuswebportal.ideam.gov.co/")
datasets = []
for param in wp.fetch_params()["param_name"]:
    datasets.append(wp.fetch_datasets(param_name=param))
datasets = pd.concat(datasets, ignore_index=True)
labels = datasets["label"].unique()
pd.DataFrame(labels, columns=["label"]).to_excel("./labels.xlsx", index=False)

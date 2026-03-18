from aquarius_webportal import AquariusWebPortal

wp = AquariusWebPortal("http://aquariuswebportal.ideam.gov.co/")
datasets = wp.fetch_datasets(param_name="NIVEL")
print(datasets)

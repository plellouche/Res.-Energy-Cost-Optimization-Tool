import json
import requests
import statistics
import re

#API Keys
radar_key_live = "prj_live_pk_1cdb13f687f0ddf73767ae5e251b620b5926b877"
radar_key_test = "prj_test_pk_45424750861e28a710cb517d73fc4aa62a631f96"

geocodio_key = "44651e446464a1656153ea6663679ad83d96de9"

nrel_key = "Zh1GOCpKpHkieLo8h8H09M9BAGyWlPJMybj7c9FE"

openei_key = "kW6G96NyWCiRPSzCpUdj8KcQTNInIsta9htnx3yb"


#Test Params

#SCE:"239 E Colorado Blvd, Pasadena, CA 91101"
#PGE:"3500 Deer Creek rd Palo Alto CA"
#SDGE:"2055 Arnold Way, Alpine, CA 91901"

test_address = "3500 Deer Creek rd Palo Alto CA"
test_address = test_address.replace(" ", "+")


test_lat = 35.45
test_long = -82.98

#URLS
nrel_url = "https://developer.nrel.gov/api/utility_rates/v3.json?api_key="
geocodio_url = "https://api.geocod.io/v1.7/geocode?q="


geo_response = requests.get(f"{geocodio_url}{test_address}&api_key={geocodio_key}")
geo_response = geo_response.json()

coords = geo_response["results"][0]["location"]
lattitude = int(coords["lat"])
longitude = int(coords["lng"])

#print(f"{coords}")

nrel_raw = requests.get(f"{nrel_url}{nrel_key}&lat={lattitude}&lon={longitude}")
nrel_response = nrel_raw.json()

utility_name = nrel_response["outputs"]["utility_name"]

if utility_name == "no data":
    utility_name = "San Diego Gas & Electric Co"


utility_name = str(utility_name)

utility_name_encoded = utility_name.replace(" ", "+")

if "&" in utility_name_encoded:
    utility_name_encoded = utility_name.replace("&", "%26")

#print(utility_name_encoded)


#OpenEI API

oei_version = "latest"
oei_format = "json"
oei_ratesforutility = utility_name_encoded
oei_sector = "Residential"
oei_approved = "true"
oei_detail = "full"
oei_url = "https://api.openei.org/utility_rates?"

oei_response = requests.get(f"{oei_url}&version={oei_version}&format={oei_format}&ratesforutility={oei_ratesforutility}&sector={oei_sector}&approved={oei_approved}&detail={oei_detail}&api_key={openei_key}")
oei_response = oei_response.json()

print(f"{oei_url}&version={oei_version}&format={oei_format}&ratesforutility={oei_ratesforutility}&sector={oei_sector}&approved={oei_approved}&detail={oei_detail}&api_key={openei_key}")



oei_rate = oei_response["items"][-1]
print(oei_rate)



#Utility Rate Book Scraping

PGE_rate_url = "https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-6.pdf"
SCE_rate_url = "https://edisonintl.sharepoint.com/teams/Public/TM2/Shared%20Documents/Forms/AllItems.aspx?ga=1&id=%2Fteams%2FPublic%2FTM2%2FShared%20Documents%2FPublic%2FRegulatory%2FTariff%2DSCE%20Tariff%20Books%2FElectric%2FSchedules%2FResidential%20Rates%2FELECTRIC%5FSCHEDULES%5FTOU%2DD%2Epdf&parent=%2Fteams%2FPublic%2FTM2%2FShared%20Documents%2FPublic%2FRegulatory%2FTariff%2DSCE%20Tariff%20Books%2FElectric%2FSchedules%2FResidential%20Rates"
SDGE_rate_url = "https://tariff.sdge.com/tm2/pdf/tariffs/ELEC_ELEC-SCHEDS_TOU-DR2.pdf"

#PGE_response = requests.get(PGE_rate_url)
#SCE_response = requests.get(SCE_rate_url)
#SDGE_response= requests.get(SDGE_rate_url)

#PGE_ratebook = PGE_response.json()
#SCE_ratebook = SCE_response.json()
#SDGE_ratebook= SDGE_response.json()


#print(PGE_ratebook)







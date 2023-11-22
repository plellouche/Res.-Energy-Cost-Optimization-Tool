import json
import requests
import statistics
import re

#API Parameters
radar_key_live = "prj_live_pk_1cdb13f687f0ddf73767ae5e251b620b5926b877"
radar_key_test = "prj_test_pk_45424750861e28a710cb517d73fc4aa62a631f96"

test_address = "502 Thompson st Ann Arbor MI"
test_lat = 35.27
test_long = -82.74

radar_headers ={
'radar_auth': radar_key_live
}

radar_params={
'radar_query': test_address
}

radar_raw = requests.get("https://api.radar.io/v1/geocode/forward", params=radar_params, headers=radar_headers)

#print(radar_raw)

nrel_url = "https://api/utility_rates/v3.json?api_key="
nrel_key = "Zh1GOCpKpHkieLo8h8H09M9BAGyWlPJMybj7c9FE"

test_raw = requests.get(f"{nrel_url}{nrel_key}&lat={test_lat}&lon={test_long}")

print(test_raw)




#Utility Rate Book Scraping

PGE_rate_url = "https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-6.pdf"
SCE_rate_url = "https://edisonintl.sharepoint.com/teams/Public/TM2/Shared%20Documents/Forms/AllItems.aspx?ga=1&id=%2Fteams%2FPublic%2FTM2%2FShared%20Documents%2FPublic%2FRegulatory%2FTariff%2DSCE%20Tariff%20Books%2FElectric%2FSchedules%2FResidential%20Rates%2FELECTRIC%5FSCHEDULES%5FTOU%2DD%2Epdf&parent=%2Fteams%2FPublic%2FTM2%2FShared%20Documents%2FPublic%2FRegulatory%2FTariff%2DSCE%20Tariff%20Books%2FElectric%2FSchedules%2FResidential%20Rates"
SDGE_rate_url = "https://tariff.sdge.com/tm2/pdf/tariffs/ELEC_ELEC-SCHEDS_TOU-DR2.pdf"



def download_ratebook(url):
    response = requests.get(url)

    with open('file.pdf', 'wb') as file:
        file.write(response.content)

    return file










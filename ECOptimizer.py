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



import json
import requests
import statistics
import re
import ECOClasses



#Geo API call - obtain coordinates from address
def getGeoApi(geocodio_url, geocodio_key, address):
    geo_response = requests.get(f"{geocodio_url}{address}&api_key={geocodio_key}")
    geo_response = geo_response.json()
    return geo_response



#NREL API call - obtain utility from coordinates
def getNrelApi(nrel_url, nrel_key, lattitude, longitude):
    nrel_raw = requests.get(f"{nrel_url}{nrel_key}&lat={lattitude}&lon={longitude}")
    nrel_response = nrel_raw.json()
    return nrel_response



#Accounts for localities with different utility names that are still under PGE and SCE rates
def subSubsidiaries(utility_name, subsidiaries_list, main_utility_name):
    for keyword in subsidiaries_list:
        if keyword in utility_name.lower():
            utility_name = main_utility_name

    return utility_name



# Elimitate utilities outside known territories (California)
def elimOutliers(utility_name, lattitude, longitude):
    if utility_name == "no data" and lattitude < 33.6 and longitude < -116:
        utility_name = "San Diego Gas & Electric Co"

    elif ("pacific" not in utility_name.lower()) and ("edison" not in utility_name.lower()) and (utility_name == "no data" and lattitude > 33.6 and longitude > -116):
        print("*****ERROR, ADDRESS OUTSIDE OF KNOWN UTILITY TERRITORIES")
        utility_name = "Error"

    return utility_name



#Encodes utility name to be used in url
def encodeUtility(utility_name):
    utility_name = str(utility_name)
    utility_name_encoded = utility_name.replace(" ", "+")

    if "&" in utility_name_encoded:
        utility_name_encoded = utility_name.replace("&", "%26")

    return utility_name_encoded



def getOeiApi(oei_version, oei_format, oei_ratesforutility, oei_sector, oei_approved, oei_detail, oei_url, openei_key):
    oei_response = requests.get(f"{oei_url}&version={oei_version}&format={oei_format}&ratesforutility={oei_ratesforutility}&sector={oei_sector}&approved={oei_approved}&detail={oei_detail}&api_key={openei_key}")
    oei_response = oei_response.json()
    return oei_response



#For each utility, creates arrays of correct rate types
def extractRate(oei_response, utility_name):
    PGE_E6_Rates = []
    SCE_TOUD_Rates = []
    SDGE_TOUDR2_Rates = []

    for rate in oei_response["items"]:
        if "pacific" in utility_name.lower():
            if "e-6" in rate["name"].lower():
                PGE_E6_Rates.append(rate)

        elif "diego" in utility_name.lower():
            if "tou" in rate["name"].lower() and "ev" not in rate["name"].lower():
                SDGE_TOUDR2_Rates.append(rate)

        elif "edison" in utility_name.lower():
            if "tou-d-1" in rate["name"].lower():
                SCE_TOUD_Rates.append(rate)

    return PGE_E6_Rates, SCE_TOUD_Rates, SDGE_TOUDR2_Rates



#Isolates latest rate (rates will change dynamically as API updates)
def isolateRate(utility_name, PGE_E6_Rates, SCE_TOUD_Rates, SDGE_TOUDR2_Rates):
    if "pacific" in utility_name.lower():
        raw_tariff_rate = PGE_E6_Rates[-1]

    elif "diego" in utility_name.lower():
        raw_tariff_rate = SDGE_TOUDR2_Rates[-1]

    elif "edison" in utility_name.lower():
        raw_tariff_rate = SCE_TOUD_Rates[-1]

    return raw_tariff_rate

















################################################################
###################           MAIN           ###################
################################################################



#API Keys
radar_key_live = "prj_live_pk_1cdb13f687f0ddf73767ae5e251b620b5926b877"
radar_key_test = "prj_test_pk_45424750861e28a710cb517d73fc4aa62a631f96"
geocodio_key = "44651e446464a1656153ea6663679ad83d96de9"
nrel_key = "Zh1GOCpKpHkieLo8h8H09M9BAGyWlPJMybj7c9FE"
openei_key = "kW6G96NyWCiRPSzCpUdj8KcQTNInIsta9htnx3yb"



#Test Params
'''
SCE:"239 E Colorado Blvd, Pasadena, CA 91101"
PGE:"3500 Deer Creek rd Palo Alto CA"
SDGE:"2055 Arnold Way, Alpine, CA 91901"
'''

test_address = "2055 Arnold Way, Alpine, CA 91901"
test_address = test_address.replace(" ", "+")


# Address Inputs

input_address = input("Please enter the address for your California residence (ex: 3500 Deer Creek rd Palo Alto CA): ")

print("\n")
print(f"Address entered: {input_address}")

input_address = input_address.replace(" ", "+")



#URLS
nrel_url = "https://developer.nrel.gov/api/utility_rates/v3.json?api_key="
geocodio_url = "https://api.geocod.io/v1.7/geocode?q="



#Geo API call - obtain coordinates from address
geo_response = getGeoApi(geocodio_url, geocodio_key, input_address)
coords = geo_response["results"][0]["location"]
lattitude = float(coords["lat"])
longitude = float(coords["lng"])



#NREL API call - obtain utility from coordinates
nrel_response = getNrelApi(nrel_url, nrel_key, lattitude, longitude)
utility_name = nrel_response["outputs"]["utility_name"]



#Accounts for localities with different utility names that are still under PGE and SCE rates
PGE_Subsidiaries = ["palo", "francisco", "stockton", "oakland", "sacramento", "silicon", "alameda", "lathrop", "lodi", "modesto"]
SCE_Subsidiaries = ["burbank", "glendale", "angeles", "pasadena", "riverside"]

utility_name = subSubsidiaries(utility_name, PGE_Subsidiaries, "Pacific Gas & Electric Co")
utility_name = subSubsidiaries(utility_name, SCE_Subsidiaries, "Southern California Edison Co")



# Elimitate utilities outside known territories (California)
utility_name = elimOutliers(utility_name, lattitude, longitude)

#Encodes utility name to be used in url for final API call
utility_name_encoded = encodeUtility(utility_name)



#Utility name output

print("\n")

if utility_name == "Error":
    print("Please restart the program and enter a different address.")

else:
    print(f"Based on your address, you are served by {utility_name}")

print("\n")


#Appliance inputs

appliance_ref_list = ["EV", "Washer", "Drier", "Dishwasher", "Toaster", "Blender", "Vacuum", "Oven", "Stove", "Space Heater", "Lighting", "Entertainment", "Microwave", "Hair Drier", "Iron", "Air Conditioning (Portable)", "Air Conditioning (Window)", "Pool Heat Pump"]

input_appliance_list = []
formatStr_default = "Appliance Name (match list examples), N/A, Average daily hours used (ex: 2), Average days per week used (ex: 7)"
formatStr_userdefined = "Appliance Name (match list examples), Consumption in kW (ex: 0.8), Average daily hours used (ex: 2), Average days per week used  (ex: 7), Seasonality (Summer Only, Winter Only, or N/A), Average start time in military time (ex: 14), Average end time in military time (ex: 18)"

initial_input = input(f"Please enter appliances you have in your home. You can chose from the following list: {appliance_ref_list}. \n \nPlease format your input as follows: \n \n  1) If you would like to use default values based on national averages, enter: {formatStr_default} \n \n   2) If you would like to specify custom values, enter: {formatStr_userdefined} \nOnce inputted, please press enter. '")
initial_input = initial_input.split(',')
input_appliance_list.append(initial_input)

while True:
    input_instance = input("Please enter another (enter 'Done!' once finished adding appliances): ")

    if input_instance == "Done!":
        print("\n \nGenerating report.... \n \n")
        break

    input_instance = input_instance.split(",")
    input_appliance_list.append(input_instance)

#OpenEI API - obtain utility rates
oei_version = "latest"
oei_format = "json"
oei_ratesforutility = utility_name_encoded
oei_sector = "Residential"
oei_approved = "true"
oei_detail = "full"
oei_url = "https://api.openei.org/utility_rates?"

oei_response = getOeiApi(oei_version, oei_format, oei_ratesforutility, oei_sector, oei_approved, oei_detail, oei_url, openei_key)
oei_rate = oei_response["items"][-1]
#print(oei_rate)


#For each utility, creates arrays of correct rate types
PGE_E6_Rates, SCE_TOUD_Rates, SDGE_TOUDR2_Rates = extractRate(oei_response, utility_name)

raw_tariff_rate = isolateRate(utility_name, PGE_E6_Rates, SCE_TOUD_Rates, SDGE_TOUDR2_Rates)

#Export rate to seperate JSON file, potential to cache if needed
with open("test_rate.json", 'w') as json_file:
    json.dump(raw_tariff_rate, json_file, indent=4)



# Initializing Override rate dictionaries, used to build rate classes
SDGE_RateDict_Override = {
    "peak_hrs_summer": [16,17,18,19,20,21],
    "peak_hrs_winter": [16,17,18,19,20,21],
    "summer_peak_kwh": 0.84077,
    "summer_offpeak_kwh": 0.44858,
    "winter_peak_kwh": 0.63646,
    "winter_offpeak_kwh": 0.54065,
    "summer_peak_kw": 0,
    "summer_offpeak_kw": 0,
    "winter_peak_kw": 0,
    "winter_offpeak_kw": 0,
}

SCE_RateDict_Override = {
   "peak_hrs_summer": [16,17,18,19,20,21],
    "peak_hrs_winter": [16,17,18,19,20,21],
    "summer_peak_kwh": 0.44806,
    "summer_offpeak_kwh": 0.11414,
    "winter_peak_kwh": 0.32005,
    "winter_offpeak_kwh": 0.11414,
    "summer_peak_kw": 0,
    "summer_offpeak_kw": 0,
    "winter_peak_kw": 0,
    "winter_offpeak_kw": 0,
}

PGE_RateDict_Override = {
    "peak_hrs_summer": [16,17,18,19,20,21],
    "peak_hrs_winter": [16,17,18,19,20,21],
    "summer_peak_kwh": 0.46272,
    "summer_offpeak_kwh": 0.34062,
    "winter_peak_kwh": 0.3418,
    "winter_offpeak_kwh": 0.33095,
    "summer_peak_kw": 0,
    "summer_offpeak_kw": 0,
    "winter_peak_kw": 0,
    "winter_offpeak_kw": 0,
}


#Initialize Appliance Instances for average, optimal, worst case

ev_avg = ECOClasses.Appliance("EV", 11.5, 1.2, 7, usecase="Average Case")
washer_avg = ECOClasses.Appliance("Washer", 0.9, 0.92, 4, usecase="Average Case")
drier_avg = ECOClasses.Appliance("Drier", 3.25, 0.75, 4, usecase="Average Case")
dishwasher_avg = ECOClasses.Appliance("Dishwasher", 1.8, 2, 5, usecase="Average Case")
toaster_avg = ECOClasses.Appliance("Toaster", 1.1, 0.08, 3, usecase="Average Case")
blender_avg = ECOClasses.Appliance("Blender", 0.4, 0.05, 2.5, usecase="Average Case")
vacuum_avg = ECOClasses.Appliance("Vacuum", 1.7, 0.17, 2, usecase="Average Case")
oven_avg = ECOClasses.Appliance("Oven", 3.5, 0.65, 3, usecase="Average Case")
stove_avg = ECOClasses.Appliance("Stove", 2, 0.4, 8, usecase="Average Case")
space_heater_avg = ECOClasses.Appliance("Space Heater", 2, 1, 2, usecase="Average Case")
lighting_avg = ECOClasses.Appliance("Lighting", 1.3, 5, 7, usecase="Average Case")
entertainment_avg = ECOClasses.Appliance("Entertainment", 0.2, 1.5, 5, usecase="Average Case")
microwave_avg = ECOClasses.Appliance("Microwave", 0.8, 0.04, 5, usecase="Average Case")
hair_drier_avg = ECOClasses.Appliance("Hair Drier", 1.3, 0.15, 2, usecase="Average Case")
iron_avg = ECOClasses.Appliance("Iron", 1.1, 0.13, 1, usecase="Average Case")
ac_portable_avg = ECOClasses.Appliance("Air Conditioning (Portable)", 2.7, 2, 3, seasonality="Summer only", usecase="Average Case")
ac_window_avg = ECOClasses.Appliance("Space Heater", 1.5, 2, 3, seasonality="Summer only", usecase="Average Case")
pool_heater_avg = ECOClasses.Appliance("Pool Heat Pump", 3, 3, 3.5, usecase="Average Case")


#Instantiate Optimal, average
#appliance_optimal_list = [ev_optimal, washer_optimal, drier_optimal, dishwasher_optimal, toaster_optimal, blender_optimal, vacuum_optimal, oven_optimal, stove_optimal, space_heater_optimal, lighting_optimal, entertainment_optimal, microwave_optimal, hair_drier_optimal, iron_optimal, ac_portable_optimal, ac_window_optimal, pool_heater_optimal]

#Optimal, worst, average lists and dict
appliance_worst_dict = {}
appliance_optimal_dict = {}

'''
for appliance in appliance_optimal_list:
    appliance_optimal_dict[appliance.name] = appliance

'''



# Reference dict with average appliance power for different appliances:
power_reference_dict = {
    "EV": 11.5,
    "Washer": 0.9,
    "Drier": 3.25,
    "Dishwasher": 1.8,
    "Toaster": 1.1,
    "Blender": 0.4,
    "Vacuum": 1.7,
    "Oven": 3.5,
    "Stove": 2,
    "Space Heater": 2,
    "Lighting": 1.3,
    "Entertainment": 0.2,
    "Microwave": 0.8,
    "Hair Drier": 1.3,
    "Iron": 1.1,
    "Air Conditioning (Portable)": 2.7,
    "Space Heater": 1.5,
    "Pool Heat Pump": 3
}

user_defined_appliances = []
optimal_appliances = []
average_appliances = []

for instance in input_appliance_list:

    if len(instance) == 4:
        for key, val in power_reference_dict.items():
            if str(instance[0]) == key:
                instance[1] = val

        new_ud_instance = ECOClasses.Appliance(instance[0], instance[1], float(instance[2]), float(instance[3]))
        new_optimal_instance = ECOClasses.Appliance(instance[0], instance[1], float(instance[2]), float(instance[3]), usecase="Optimal Case")
        new_average_instance = ECOClasses.Appliance(instance[0], instance[1], float(instance[2]), float(instance[3]), usecase="Average Case")

    elif len(instance) == 7:

        if instance[4].strip() == "N/A":
            instance[4] = None

        instance[2] = int(instance[6]) - int(instance[5])

        new_ud_instance = ECOClasses.Appliance(instance[0], float(instance[1]), instance[2], instance[3], seasonality=instance[4], usecase="User Defined", schedule=f"{instance[5]},{instance[6]}")
        new_optimal_instance = ECOClasses.Appliance(instance[0], float(instance[1]), instance[2], instance[3], seasonality=instance[4], usecase="Optimal Case")
        new_average_instance = ECOClasses.Appliance(instance[0], float(instance[1]), instance[2], instance[3], seasonality=instance[4], usecase="Average Case")

    else:
        print("ERROR, Incorrect input format. Please restart the program and follow input guidelines")
        new_ud_instance = None
        new_optimal_instance = None
        new_average_instance = None

    user_defined_appliances.append(new_ud_instance)
    average_appliances.append(new_average_instance)
    optimal_appliances.append(new_optimal_instance)



SDGE_instance = ECOClasses.Rate(SDGE_RateDict_Override, "San Diego Gas and Electric Co.")
PGE_instance = ECOClasses.Rate(PGE_RateDict_Override, "Pacific Gas and Electric Co.")
SCE_instance = ECOClasses.Rate(SCE_RateDict_Override, "Southern California Edison Co.")

if "pacific" in utility_name.lower():
    tariff_instance = PGE_instance

elif "diego" in utility_name.lower():
    tariff_instance = SDGE_instance

elif "edison" in utility_name.lower():
    tariff_instance = SCE_instance



user_defined_instances = []
optimal_instances = []
average_instances = []

ud_splitvect = []
ud_costvect = []

optimal_splitvect = []
optimal_costvect = []

avg_splitvect = []
avg_costvect = []

for appliance in user_defined_appliances:
    ud_instance = ECOClasses.Instance(tariff_instance, appliance)
    temp_split = ud_instance.splits(usecase=ud_instance.usecase, schedule=ud_instance.schedule)
    temp_cost = ud_instance.calculate_monthly()

    user_defined_instances.append(ud_instance)
    ud_splitvect.append(temp_split)
    ud_costvect.append(ud_costvect)


for appliance in optimal_appliances:
    optimal_instance = ECOClasses.Instance(tariff_instance, appliance)
    temp_split_o = optimal_instance.splits(usecase=optimal_instance.usecase, schedule=optimal_instance.schedule)
    temp_cost_o = optimal_instance.calculate_monthly()

    optimal_instances.append(optimal_instance)
    optimal_splitvect.append(temp_split_o)
    optimal_costvect.append(temp_cost_o)

for appliance in average_appliances:
    avg_instance = ECOClasses.Instance(tariff_instance, appliance)
    temp_split_avg = avg_instance.splits(usecase=avg_instance.usecase, schedule=avg_instance.schedule)
    temp_cost_avg = avg_instance.calculate_monthly()


    average_instances.append(avg_instance)
    avg_splitvect.append(temp_split_avg)
    avg_costvect.append(temp_cost_avg)

summer_total_savings = []
winter_total_savings = []



print("\n***********           Summer Report           ***********\n \n")

summer_counter = 1
for i in range(len(user_defined_instances)):
    print(f"{summer_counter}. {user_defined_instances[i].name}: ")
    print(f"Your monthly cost: ${round(user_defined_instances[i].total_summer_cost, 1)}")
    print(f"Average monthly cost (market research): ${round(average_instances[i].total_summer_cost, 1)}")
    print(f"Optimal monthly cost (minimum): ${round(optimal_instances[i].total_summer_cost, 1)}")
    print(f"Maximum potential savings: ${round(user_defined_instances[i].total_summer_cost - optimal_instances[i].total_summer_cost, 1)}")
    summer_total_savings.append(user_defined_instances[i].total_summer_cost - optimal_instances[i].total_summer_cost)
    print("\n")
    summer_counter += 1

print(f"Total summer month savings across all appliances: ${round(sum(summer_total_savings), 1)} \n")

print("/n")
print("\n***********           Winter Report           ***********\n \n")
winter_counter = 1
for j in range(len(user_defined_instances)):
    print(f"{winter_counter}. {user_defined_instances[j].name}: ")
    print(f"Your monthly cost: ${round(user_defined_instances[j].total_winter_cost, 1)}")
    print(f"Average monthly cost (market research): ${round(average_instances[j].total_winter_cost, 1)}")
    print(f"Optimal monthly cost (minimum): ${round(optimal_instances[j].total_winter_cost, 1)}")
    print(f"Maximum potential savings: ${round((user_defined_instances[j].total_winter_cost - optimal_instances[j].total_winter_cost), 1)}")
    winter_total_savings.append(user_defined_instances[j].total_winter_cost - optimal_instances[j].total_winter_cost)
    print("\n")
    winter_counter += 1

print(f"Total winter month savings across all appliances: ${round(sum(winter_total_savings), 1)} \n \n")







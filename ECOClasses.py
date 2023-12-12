import json
import requests
import statistics
import re


class Rate:
    def __init__(self, RateDict, UtilityName):

        self.backupdict = RateDict

        self.name = UtilityName

        self.peak_hrs_summer = RateDict["peak_hrs_summer"]
        self.peak_hrs_winter = RateDict["peak_hrs_winter"]

        self.summer_peak_kwh = RateDict["summer_peak_kwh"]
        self.summer_offpeak_kwh = RateDict["summer_offpeak_kwh"]
        self.winter_peak_kwh = RateDict["winter_peak_kwh"]
        self.winter_offpeak_kwh = RateDict["winter_offpeak_kwh"]

        self.summer_peak_kw = RateDict["summer_peak_kw"]
        self.summer_offpeak_kw = RateDict["summer_offpeak_kw"]
        self.winter_peak_kw = RateDict["winter_peak_kw"]
        self.winter_offpeak_kw = RateDict["winter_offpeak_kw"]

        if "pacific" in UtilityName.lower():
            self.region = "Northern California"

        elif "diego" in UtilityName.lower():
            self.region = "San Diego County"

        elif "edison" in UtilityName.lower():
            self.region = "Southern California w/o San Diego County"


        day = list(range(1,25))
        offpeak_hrs_summer = []
        offpeak_hrs_winter = []


        for hour in day:
            if hour not in self.peak_hrs_summer:
                offpeak_hrs_summer.append(hour)

            if hour not in self.peak_hrs_winter:
                offpeak_hrs_winter.append(hour)

        self.offpeak_hrs_summer = offpeak_hrs_summer
        self.offpeak_hrs_winter = offpeak_hrs_winter


    def __str__(self):
        return f'Utility Name: {self.name}, Summer On peak $/kWh: {self.summer_peak_kw}, Summer Off peak $/kWh: {self.summer_offpeak_kwh}, Winter On peak $/kWh: {self.winter_peak_kwh}, Winter Off Peak $/kWh: {self.winter_offpeak_kwh}, Summer On peak $/kW: {self.summer_peak_kw}, Summer Off peak $/kW: {self.summer_offpeak_kw}, Winter On peak $/kW: {self.summer_peak_kw}, Winter Off peak $/kW: {self.summer_offpeak_kw},'



class Appliance:
    def __init__(self, applianceName, consumption_power, hours, daysPerWeek, units="Kilo-Watts", seasonality=None, usecase="Average Case", schedule=None):

        self.name = applianceName
        self.power = consumption_power
        self.hours = hours
        self.days = daysPerWeek
        self.units = units
        self.usecase = usecase
        self.schedule = schedule
        self.dailyconsumption = float(self.power) * float(self.hours)
        self.daysPerMonth = float(self.days) * 4.285
        self.hoursPerMonth = float(self.hours) * self.daysPerMonth
        self.monthlyConsumption = self.hoursPerMonth * self.power
        self.seasonality = seasonality

    def conversions(self):
        if self.units == "Watts":
            self.kwh = self.dailyconsumption/1000
            self.kw = self.power/1000
            self.units = "Kilo-Watts"

        else:
            self.kwh = self.dailyconsumption
            self.kw = self.power

    def __str__(self):
        return f'Appliance: {self.name}, Average monthly usage: {self.hoursPerMonth} consuming {self.power} kW. Use Case: {self.usecase}'


class Instance:
    def __init__(self, rate_instance:Rate, appliance_instance:Appliance):

        self.name = appliance_instance.name
        self.appliance_name = appliance_instance.name
        self.appliance_power = appliance_instance.power
        self.appliance_dailyHours = appliance_instance.hours
        self.appliance_daysPerWeek = appliance_instance.days
        self.monthly_kwh = appliance_instance.monthlyConsumption
        self.daysPerMonth = appliance_instance.daysPerMonth
        self.seasonality = appliance_instance.seasonality
        self.schedule = appliance_instance.schedule

        self.usecase = appliance_instance.usecase

        self.utility = rate_instance.name
        self.rate_dict = rate_instance.backupdict
        self.peak_hrs_summer = rate_instance.peak_hrs_summer
        self.peak_hrs_winter = rate_instance.peak_hrs_winter
        self.hoursPerMonth = appliance_instance.hoursPerMonth
        self.offpeak_hrs_summer = rate_instance.offpeak_hrs_summer
        self.offpeak_hrs_winter = rate_instance.offpeak_hrs_winter

        #Determine summer and winter monthly total usage hours, account for seasonality

        if self.seasonality is not None:

            if self.seasonality.strip() == "Summer Only":
                self.dailyHours_winter = 0
                self.appliance_winter_hours = 0
                self.appliance_summer_hours = appliance_instance.hoursPerMonth

            elif self.seasonality.strip() == "Winter Only":
                self.dailyHours_summer = 0
                self.appliance_summer_hours = 0
                self.appliance_winter_hours = appliance_instance.hoursPerMonth

        else:
            self.dailyHours_winter = self.appliance_dailyHours
            self.dailyHours_summer = self.appliance_dailyHours
            self.appliance_winter_hours = appliance_instance.hoursPerMonth
            self.appliance_summer_hours = appliance_instance.hoursPerMonth


    # Calc number of hours appliance instance is on peak and off peak for a given month
    def splits(self, usecase, schedule):
        #Usage can sometimes be longer than entire on peak window - need to adjust
        if usecase == "Worst Case":

            if self.dailyHours_summer > len(self.peak_hrs_summer) and self.dailyHours_winter > len(self.peak_hrs_winter):
                self.total_summer_peak_hrs = float(len(self.peak_hrs_summer))* self.daysPerMonth
                self.total_summer_offpeak_hrs = float(self.appliance_summer_hours - len(self.peak_hrs_summer)) * self.daysPerMonth
                self.total_winter_peak_hrs = float(len(self.peak_hrs_winter)) * self.daysPerMonth
                self.total_winter_offpeak_hrs = float(self.appliance_winter_hours - len(self.peak_hrs_winter)) * self.daysPerMonth

            elif self.dailyHours_winter > len(self.peak_hrs_winter) and self.dailyHours_summer <= len(self.peak_hrs_summer):
                self.total_winter_peak_hrs = float(len(self.peak_hrs_winter)) * self.daysPerMonth
                self.total_winter_offpeak_hrs = float(self.appliance_winter_hours - len(self.peak_hrs_winter)) * self.daysPerMonth
                self.total_summer_peak_hrs = self.appliance_summer_hours
                self.total_summer_offpeak_hrs = 0

            elif self.dailyHours_winter <= len(self.peak_hrs_winter) and self.dailyHours_summer > len(self.peak_hrs_summer):
                self.total_summer_peak_hrs = float(len(self.peak_hrs_summer)) * self.daysPerMonth
                self.total_summer_offpeak_hrs = float(self.appliance_summer_hours - len(self.peak_hrs_summer)) * self.daysPerMonth
                self.total_winter_peak_hrs = self.appliance_winter_hours
                self.total_winter_offpeak_hrs = 0

            else:
                self.total_summer_peak_hrs = self.appliance_summer_hours
                self.total_summer_offpeak_hrs = 0
                self.total_winter_peak_hrs = self.appliance_winter_hours
                self.total_winter_offpeak_hrs = 0



        #Optimal use case - cost assosiated with off peak windows
        if usecase == "Optimal Case":

            self.total_summer_offpeak_hrs = self.appliance_summer_hours
            self.total_summer_peak_hrs = 0

            self.total_winter_offpeak_hrs = self.appliance_winter_hours
            self.total_winter_peak_hrs = 0


        # User Defined use case.

        if usecase == "User Defined":

            if self.schedule == None:
                print("****ERROR: No schedule provided, going off of average usage****")
                self.usecase = "Average Case"

            schedule = str(schedule)
            schedule = schedule.split(",")
            start_time = int(schedule[0])
            end_time = int(schedule[1])
            time_range = list(range(start_time, end_time))

            temp_peak_summer = 0

            for hour in time_range:
                if hour in self.peak_hrs_summer:
                    temp_peak_summer += 1

            self.total_summer_peak_hrs = float(temp_peak_summer) * self.daysPerMonth
            self.total_summer_offpeak_hrs = float(len(time_range) - temp_peak_summer) * self.daysPerMonth


            temp_peak_winter = 0

            for hour in time_range:
                if hour in self.peak_hrs_winter:
                    temp_peak_winter += 1

            self.total_winter_peak_hrs = float(temp_peak_winter) * self.daysPerMonth
            self.total_winter_offpeak_hrs = float(len(time_range) - temp_peak_winter) * self.daysPerMonth


            if self.seasonality is not None:

                if self.seasonality == "Summer Only":
                   self.total_winter_offpeak_hrs = 0
                   self.total_winter_peak_hrs = 0

                elif self.seasonality == "Winter Only":
                    self.total_summer_offpeak_hrs = 0
                    self.total_summer_peak_hrs = 0


        #Average use case. Assume split follows proportions of hours that are on peak (21%)

        if usecase == "Average Case":

            self.total_summer_offpeak_hrs = 0.66 * float(self.appliance_summer_hours)
            self.total_summer_peak_hrs = 0.34 * float(self.appliance_summer_hours)

            self.total_winter_offpeak_hrs = 0.66 * float(self.appliance_winter_hours)
            self.total_winter_peak_hrs = 0.34 * float(self.appliance_winter_hours)

        split_vect = [self.total_summer_peak_hrs, self.total_summer_offpeak_hrs, self.total_winter_peak_hrs, self.total_winter_offpeak_hrs]
        return split_vect


    def calculate_monthly(self):
        self.summer_kwh_cost = self.total_summer_peak_hrs * self.appliance_power * self.rate_dict["summer_peak_kwh"] + self.total_summer_offpeak_hrs * self.appliance_power * self.rate_dict["summer_offpeak_kwh"]
        self.winter_kwh_cost = self.total_winter_peak_hrs * self.appliance_power * self.rate_dict["winter_peak_kwh"] + self.total_winter_offpeak_hrs * self.appliance_power * self.rate_dict["winter_offpeak_kwh"]

        self.summer_kw_cost = self.appliance_power * self.rate_dict["summer_peak_kw"] + self.appliance_power * self.rate_dict["summer_offpeak_kw"]
        self.winter_kw_cost = self.appliance_power * self.rate_dict["winter_peak_kw"] + self.appliance_power * self.rate_dict["winter_offpeak_kw"]

        self.total_summer_cost = self.summer_kw_cost + self.summer_kwh_cost
        self.total_winter_cost = self.winter_kw_cost + self.winter_kwh_cost

        self.cost_summary = [self.total_summer_cost, self.total_winter_cost, [self.summer_kwh_cost, self.summer_kw_cost, self.winter_kwh_cost, self.winter_kw_cost]]

        return self.cost_summary


    def __str__(self):

        return f"Instance: {self.name}, Use Case: {self.usecase}, Utility: {self.utility}, Power: {self.appliance_power}, Daily Hours: {self.appliance_dailyHours}, Summer Total Cost: {self.total_summer_cost}, Winter Total Cost: {self.total_winter_cost}"

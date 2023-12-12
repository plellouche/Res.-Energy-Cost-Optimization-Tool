# Residential Energy Cost Optimization Tool

Over the last decade, residential energy rates have shifted towards so-called “time of use” rates, meaning that energy costs for individual consumers fluctuate throughout the day and across seasons based on fixed schedules prescribed by the utility company which supplies their electricity. Additionally, the popularization of residential renewable energy systems and other challenges to the grid such as electric vehicle charging have added a layer of complexity to electric rates that often make them misunderstood by the general public. Utility schedules are often hard to find by customers, and it seems to many that electricity is both too expensive and that the billing is a black box. There is therefore a need for a tool that, based on simple user inputs, is able to make accurate estimates of the price they are paying for their energy consumption but also allows them to optimize their consumption patterns to reduce energy costs based on their preferences. This tool would have to utilize APIs to determine which utility and rate schedule a customer is being billed under, and scrape the web pages of said utilities to determine rate components and then calculate the savings potential for each customer based on their consumption. For the sake of simplicity of implementation, this tool will focus on the state of California to start, as their overall tariff rate structure is rather uniform and energy costs are comparatively high.
Data Sources:


- https://www.geocod.io/docs/#geocoding
  - API which returns the latitude and longitude of a location from an address
- https://developer.nrel.gov/docs/electricity/utility-rates-v3/#json-output-format
  API which returns basic rate information based on latitude and longitude
- Only returns most basic rate components, therefore will be used to match a utility company to a user based on their location
- Alternatively considering using OpenEI's utility rate API: https://apps.openei.org/services/doc/rest/util_rates/?version=3

From here, appropriate rate schedules will have to be created from OpenEI's API This requires isolating the proper tariff rate, and extracting the latest revision. In some cases, manual adjustments will have to be made to the rate schedules to reflect most accurate numbers, as the API sometimes pulls outdated data.

Once the rate information is obtained, a tariff instance can be built with the following components.
- Fixed charge
- On peak demand charge
- Off peak demand charge
- On peak energy charge
- Off peak energy charge
- On peak time range
- Off peak time range

The tool will prompt the user to input a list of appliances they use regularly in their household based on a list of common appliances that will be presented to the user.
The user will have a choice to solely provide the tool with the appliance name and their usage pattern and let it make calculations based off of defaults, or they will be able to create custom querys by defining appliance name, consumption, typical consumption schedules, and potential seasonality (ex AC only being used in the summer,)


From this list of appliances a daily consumption profile will be generated, and the associated daily and monthly energy cost will be calculated using the appropriate rate instance.
The tool will then calculate the optimal consumption profile to minimize the overall cost of energy by proposing alternate times during which these appliances are used
(off peak hours, avoiding staggered use to reduce demand charges, etc.). It will also calculate an average consumption profile with assumptions backed by research on consumer patterns. The tool will then generategenerate a report with a side by side comparison of the current vs. optimized  and average costs of each appliance, as well as the total savings potential for each season.


Presentation
Tool will generate a report with a side by side comparison of the current vs. optimized cost of each appliance. This will be in the command line, as there was no time to implement a flask presentation.

# Res.-Energy-Cost-Optimization-Tool

Over the last decade, residential energy rates have shifted towards so-called “time of use” rates, meaning that energy costs for individual consumers fluctuate throughout the day and across seasons based on fixed schedules prescribed by the utility company which supplies their electricity. Additionally, the popularization of residential renewable energy systems and other challenges to the grid such as electric vehicle charging have added a layer of complexity to electric rates that often make them misunderstood by the general public. Utility schedules are often hard to find by customers, and it seems to many that electricity is both too expensive and that the billing is a black box. There is therefore a need for a tool that, based on simple user inputs, is able to make accurate estimates of the price they are paying for their energy consumption but also allows them to optimize their consumption patterns to reduce energy costs based on their preferences. This tool would have to utilize APIs to determine which utility and rate schedule a customer is being billed under, and scrape the web pages of said utilities to determine rate components and then calculate the savings potential for each customer based on their consumption. For the sake of simplicity of implementation, this tool will focus on the state of California to start, as their overall tariff rate structure is rather uniform and energy costs are comparatively high.
Data Sources:


- https://radar.com/
  - API which returns the latitude and longitude of a location from an address
- https://developer.nrel.gov/docs/electricity/utility-rates-v3/#json-output-format
  API which returns basic rate information based on latitude and longitude
- Only returns most basic rate components, therefore will be used to match a utility company to a user based on their location
- Scraping rate schedules for the given utility (ex: https://www.pge.com/tariffs/electric.shtml)

From here, appropriate rate schedules will have to be determined based on keywords such as “TOU”, “Residential”, 
and the date (formats differ slightly from one utility to another but key words largely remain consistent). 
More scraping would then have to be done to extract the rate components of interest from the rate schedule.

Once the rate information is obtained, a tariff instance can be built with the following components.
- Fixed charge
- On peak demand charge
- Off peak demand charge
- On peak energy charge
- Off peak energy charge
- On peak time range
- Off peak time range

The tool will prompt the user to input a list of appliances they use regularly in their household based on a list of common appliances that will be presented to the user.
From this list of appliances a daily consumption profile will be generated, and the associated daily and monthly energy cost will be calculated using the appropriate rate instance.
The tool will then calculate the optimal consumption profile to minimize the overall cost of energy by proposing alternate times during which these appliances are used
(off peak hours, avoiding staggered use to reduce demand charges, etc.).
The tool will then present the solution to the user, offering the user the option to remove certain appliances from the calculation if they are unwilling to change their consumption as suggested by the tool.
This will continue until the user is satisfied with the proposed solution,
and will show the user how much they would be able to save on their monthly energy bill if they adopted this consumption behavior.

For each appliance and associated configuration, 
an associated demand and energy cost will be generated. Costs for all utilities and different configurations will then be compiled and returned to the user, 
allowing them to choose a configuration that fits their needs and see how much it will save them compared to their baseline configuration.

Presentation
The presentation for this project could consist of a simple command line interface, or a flask application could be created to represent the data. 
This determination will be made at a later date once the project is better understood.

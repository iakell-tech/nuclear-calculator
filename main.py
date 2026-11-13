
from drafter import *
from dataclasses import dataclass
from bakery import assert_equal


# Global constants
hours_per_year = 9000
default_household_consumption = 10500

reactor_types = [
    "Pressurized Water Reactor (PWR)",
    "Boiling Water Reactor (BWR)",
    "Small Modular Reactor (SMR)",
    "Advanced Reactor"
]


# Dataclasses

@dataclass
class Reactor:
    reactor_type: str
    electrical_power: float
    thermal_power: float
    efficiency: float


@dataclass
class State:
    electrical_power: float
    thermal_power: float
    capacity_factor: float
    efficiency: float
    reactors: list[Reactor]
    annual_energy: float
    homes_powered: float
    household_consumption: float


# Helper functions below

def calculate_efficiency(electrical_power: float, thermal_power: float) -> float:
    """Calculate the reactor's thermal efficiency"""
    return (electrical_power / thermal_power) * 100


def calculate_annual_energy(electrical_power: float, capacity_factor: float) -> float:
    """Calculate annual electrical energy production in MWh"""
    return (electrical_power * capacity_factor / 100 * hours_per_year)


def calculate_homes(annual_energy: float, household_consumption: float) -> float:
    """Estimate the number of homes powered"""
    energy_in_kwh = annual_energy * 1000
    return energy_in_kwh / household_consumption


def navigation() -> list:
    """Create navigation buttons for the website."""
    return [
        Header("Website Navigation"),
        Button("Home", "index"),
        Button("Power Calculator", "power_calculator"),
        Button("Capacity Factor", "capacity_factor"),
        Button("Annual Energy", "annual_energy"),
        Button("Homes Powered", "homes_powered"),
        Button("Reactor Comparison", "reactor_comparison"),
        Button("Scenario Simulator", "scenario_simulator")
    ]


def error_page(state: State, message: str) -> Page:
    """Display an error and allow the user to return."""
    content = [
        Header("Input Error"),
        message,
        Button("Return to Calculator", "power_calculator")
    ]
    content.extend(navigation())
    return Page(state, content)



# Route 1: home page

@route
def index(state: State) -> Page:
    """Display the homepage."""
    content = [
        Header("Nuclear Energy Calculator"),
        "Welcome to the Nuclear Energy Calculator!",
        "This website allows you to explore nuclear power "
        "generation through calculations and reactor comparisons.",
        Header("Explore the Website"),
        "Calculate reactor power, estimate electricity "
        "production, compare reactor types, and experiment "
        "with different reactor operating conditions."
    ]
    content.extend(navigation())
    return Page(state, content)


# Route 2: power calculator

@route
def power_calculator(state: State) -> Page:
    """Display the nuclear power calculator."""
    content = [
        Header("Nuclear Power Calculator"),
        "Enter your reactor specifications below",
        "Electrical Power (MWe):",
        TextBox("electrical_power", state.electrical_power,
                "number"),
        "Thermal Power (MWth):",
        TextBox("thermal_power", state.thermal_power,
                "number"),
        "Capacity Factor (%):",
        TextBox("capacity_factor", state.capacity_factor,
                "number"),
        Button("Calculate Reactor Performance",
               "calculate_power")
    ]
    content.extend(navigation())
    return Page(state, content)


@route
def calculate_power(state: State, electrical_power: float, thermal_power: float, capacity_factor: float) -> Page:
    """this function checks for inputs that are valid for calculations"""
    # Check that power inputs are positive
    if electrical_power <= 0 or thermal_power <= 0:
        return error_page(state, "Electrical and thermal power must be positive numbers.")
    # Check that capacity factor is valid
    if capacity_factor < 0 or capacity_factor > 100:
        return error_page(state, "Capacity factor must be between 0% and 100%.")
    # Calculate efficiency
    efficiency = calculate_efficiency(electrical_power, thermal_power)
    # Check that efficiency is valid
    if efficiency <= 0 or efficiency > 100:
        return error_page(state,"Efficiency must be greater than 0% and no greater than 100%.")
    # Update the State attributes
    state.electrical_power = electrical_power
    state.thermal_power = thermal_power
    state.capacity_factor = capacity_factor
    state.efficiency = efficiency

    state.annual_energy = calculate_annual_energy(electrical_power, capacity_factor)

    content = [
        Header("Calculation Results"),
        "Electrical Power: " + str(state.electrical_power)
        + " MWe",
        "Thermal Power: " + str(state.thermal_power)
        + " MWth",
        "Plant Efficiency: " + str(round(state.efficiency, 2))
        + "%",
        "Capacity Factor: " + str(state.capacity_factor)
        + "%",
        "Annual Energy Production: "
        + str(round(state.annual_energy, 2)) + " MWh",
        Button("Calculate Homes Powered", "homes_powered"),
        Button("View Annual Energy", "annual_energy")
    ]
    content.extend(navigation())
    return Page(state, content)

# Route 3: capactiy factor

@route
def capacity_factor(state: State) -> Page:
    """Display the capacity factor adjustment page."""
    content = [
        Header("Capacity Factor Calculator"),
        "Current Capacity Factor: "
        + str(state.capacity_factor) + "%",
        "Enter a new capacity factor between 0 and 100.",
        TextBox("new_capacity_factor",
                state.capacity_factor, "number"),
        Button("Update Capacity Factor",
               "update_capacity_factor")
    ]
    content.extend(navigation())
    return Page(state, content)


@route
def update_capacity_factor(state: State,
                           new_capacity_factor: float) -> Page:
    """Update capacity factor and annual energy."""

    if new_capacity_factor < 0 or new_capacity_factor > 100:
        return error_page(
            state,
            "Capacity factor must be between 0% and 100%."
        )

    state.capacity_factor = new_capacity_factor

    state.annual_energy = calculate_annual_energy(
        state.electrical_power,
        state.capacity_factor
    )

    return annual_energy(state)

# Route 4: calculate annual energy

@route
def annual_energy(state: State) -> Page:
    """Display annual electricity production."""
    content = [
        Header("Annual Energy Production"),
        "Electrical Power: "
        + str(state.electrical_power) + " MWe",
        "Capacity Factor: "
        + str(state.capacity_factor) + "%",
        "Annual Energy Production: "
        + str(round(state.annual_energy, 2)) + " MWh",
        "Annual Energy Production: "
        + str(round(state.annual_energy / 1000000, 3))
        + " TWh"
    ]
    content.extend(navigation())
    return Page(state, content)

# Route 5: calculate homes powered

@route
def homes_powered(state: State) -> Page:
    """Display the homes-powered calculator."""
    content = [
        Header("Homes Powered Calculator"),
        "Annual Energy Production: "
        + str(round(state.annual_energy, 2)) + " MWh",
        "Average Annual Household Electricity Consumption (kWh):",
        TextBox("household_consumption",
                state.household_consumption, "number"),
        Button("Calculate Homes Powered",
               "calculate_homes_page")
    ]
    content.extend(navigation())
    return Page(state, content)


@route
def calculate_homes_page(state: State,
                          household_consumption: float) -> Page:
    """Calculate how many homes the reactor can power."""

    if household_consumption <= 0:
        return error_page(
            state,
            "Household electricity consumption must be positive."
        )

    state.household_consumption = household_consumption

    if state.annual_energy <= 0:
        state.homes_powered = 0
        message = "The reactor currently produces no electricity."
    else:
        state.homes_powered = calculate_homes(
            state.annual_energy,
            state.household_consumption
        )

        if state.homes_powered < 1:
            message = ("The reactor produces insufficient electricity to power one average household.")
        else:
            message = ("Estimated Homes Powered: " + str(round(state.homes_powered)))

    content = [
        Header("Homes Powered Results"),
        message,
        "Annual Energy Production: "
        + str(round(state.annual_energy, 2)) + " MWh",
        "Annual Household Consumption: "
        + str(state.household_consumption) + " kWh"
    ]
    content.extend(navigation())
    return Page(state, content)


# ROUTE 6: Reactor Comparison

@route
def reactor_comparison(state: State) -> Page:
    """Display and compare saved reactor specifications."""
    content = [
        Header("Reactor Comparison"),
        "Add a reactor to your comparison list.",
        "Select Reactor Type:",
        SelectBox("reactor_type", reactor_types,
                  reactor_types[0]),
        "Electrical Power (MWe):",
        TextBox("reactor_electrical_power", 1000, "number"),
        "Thermal Power (MWth):",
        TextBox("reactor_thermal_power", 3000, "number"),
        Button("Add Reactor", "add_reactor"),
        Header("Saved Reactors")
    ]

    # Iterate through every Reactor instance in State
    if len(state.reactors) == 0:
        content.append("No reactors have been added yet.")
    else:
        for reactor in state.reactors:
            content.append("Reactor Type: " + reactor.reactor_type)
            content.append(
                "Electrical Power: "
                + str(reactor.electrical_power) + " MWe"
            )
            content.append(
                "Thermal Power: "
                + str(reactor.thermal_power) + " MWth"
            )
            content.append(
                "Efficiency: "
                + str(round(reactor.efficiency, 2)) + "%"
            )
            content.append("--------------------")

    content.extend(navigation())
    return Page(state, content)


@route
def add_reactor(state: State,
                reactor_type: str,
                reactor_electrical_power: float,
                reactor_thermal_power: float) -> Page:
    """Validate and add a reactor to the comparison list."""

    if reactor_electrical_power <= 0 or reactor_thermal_power <= 0:
        return error_page(
            state,
            "Reactor power values must be positive numbers."
        )

    reactor_efficiency = calculate_efficiency(
        reactor_electrical_power,
        reactor_thermal_power
    )

    if reactor_efficiency <= 0 or reactor_efficiency > 100:
        return error_page(
            state,
            "The reactor efficiency must be between 0% and 100%"
        )

    new_reactor = Reactor(
        reactor_type,
        reactor_electrical_power,
        reactor_thermal_power,
        reactor_efficiency
    )

    state.reactors.append(new_reactor)

    return reactor_comparison(state)

# Route 7: simulate scenario

@route
def scenario_simulator(state: State) -> Page:
    """Display the what-if scenario simulator"""
    content = [
        Header("What-If Scenario Simulator"),
        "Experiment with different reactor specifications",
        "Electrical Power (MWe):",
        TextBox("scenario_electrical_power",
                state.electrical_power, "number"),
        "Efficiency (%):",
        TextBox("scenario_efficiency",
                state.efficiency, "number"),
        "Capacity Factor (%):",
        TextBox("scenario_capacity_factor",
                state.capacity_factor, "number"),
        Button("Run Scenario", "simulate_scenario")
    ]
    content.extend(navigation())
    return Page(state, content)


@route
def simulate_scenario(state: State,
                      scenario_electrical_power: float,
                      scenario_efficiency: float,
                      scenario_capacity_factor: float) -> Page:
    """Calculate the results of a user-defined scenario"""

    if scenario_electrical_power <= 0:
        return error_page(state,"Electrical power must be a positive number")

    if scenario_efficiency <= 0 or scenario_efficiency > 100:
        return error_page(state,"Efficiency must be greater than 0% and no greater than 100%.")

    if scenario_capacity_factor < 0 or scenario_capacity_factor > 100:
        return error_page(state, "Capacity factor must be between 0% and 100%.")

    # Calculate thermal power from electrical power and efficiency
    state.electrical_power = scenario_electrical_power
    state.efficiency = scenario_efficiency
    state.capacity_factor = scenario_capacity_factor

    state.thermal_power = (
        state.electrical_power / (state.efficiency / 100)
    )

    state.annual_energy = calculate_annual_energy(
        state.electrical_power,
        state.capacity_factor
    )

    content = [
        Header("Scenario Results"),
        "Electrical Power: "
        + str(state.electrical_power) + " MWe",
        "Thermal Power: "
        + str(round(state.thermal_power, 2)) + " MWth",
        "Efficiency: "
        + str(state.efficiency) + "%",
        "Capacity Factor: "
        + str(state.capacity_factor) + "%",
        "Annual Energy Production: "
        + str(round(state.annual_energy, 2)) + " MWh"
    ]
    content.extend(navigation())
    return Page(state, content)

# Website start

start_server(
    State(
        1000,
        3000,
        90,
        33.33333333333333,
        [],
        7884000,
        0,
        default_household_consumption
    )
)


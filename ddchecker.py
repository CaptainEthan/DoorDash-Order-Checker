import sys
from dataclasses import dataclass
from typing import Dict, Optional, Union

FUEL_PRICE_PER_GAL = 2.70  # baseline gas price
AVERAGE_MPG = 20.0  # vehicle fuel efficiency
DEFAULT_ACTIVE_RATIO = 0.80  # default: active time is ~80% of dash time


@dataclass
class Settings:
    fuel_price_per_gal: float = FUEL_PRICE_PER_GAL
    average_mpg: float = AVERAGE_MPG
    active_time_ratio: float = DEFAULT_ACTIVE_RATIO
    daily_goal: Optional[float] = None


def prompt_float(message: str) -> float:
    """Ask for a numeric value until one is provided."""
    while True:
        raw = input(message).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number (you can use decimals).")


def prompt_optional_float(message: str, default: Optional[float] = None) -> Optional[float]:
    """Like prompt_float, but allows empty input to keep the default."""
    while True:
        raw = input(message).strip()
        if raw == "":
            return default
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number, or press Enter to leave it unchanged.")


def prompt_yes_no(message: str, default: Optional[bool] = None) -> bool:
    """Get a yes/no answer; supports defaults on blank input."""
    while True:
        raw = input(message).strip().lower()
        if not raw and default is not None:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please type y or n.")


def choose_pay_mode() -> tuple[str, float]:
    """Pick Earn per Offer (EBO) or Earn by Time (EBT), collecting rate if needed."""
    while True:
        choice = input("Pay type (EBO = Earn per Offer, EBT = Earn by Time): ").strip().lower()
        if choice in ("ebo", "earn per offer", "per offer", "offer"):
            return "ebo", 0.0
        if choice in ("ebt", "earn by time", "by time", "time"):
            rate = prompt_float("Hourly rate without peak pay: $")
            return "ebt", rate
        print("Please type EBO or EBT.")


def prompt_positive_time() -> float:
    """Get a non-zero estimate to avoid division issues."""
    while True:
        est_time = prompt_float("Estimated time (minutes): ")
        if est_time > 0:
            return est_time
        print("Estimated time must be greater than zero.")


def compute_dollars(mode: str, rate: float, est_time: float) -> float:
    """Calculate dollars for the order based on the selected mode."""
    if mode == "ebo":
        return prompt_float("Offer payout: $")
    est_hours = est_time / 60.0  # convert minutes to hours
    return rate * est_hours


def evaluate_order(mode: str, rate: float, settings: Settings) -> Dict[str, Union[float, bool]]:
    miles = prompt_float("Order miles: ")
    est_time = prompt_positive_time()
    dollars = compute_dollars(mode, rate, est_time)
    est_hours = est_time / 60.0
    fuel_cost = (miles / settings.average_mpg) * settings.fuel_price_per_gal
    net_dollars = dollars - fuel_cost

    result: Dict[str, Union[float, bool]] = {
        "miles": miles,
        "est_time": est_time,
        "est_hours": est_hours,
        "dollars": dollars,
        "fuel_cost": fuel_cost,
        "net_dollars": net_dollars,
    }

    if mode == "ebo":
        required_by_miles = miles  # $1 per mile
        required_by_hours = 14 * est_hours  # $14 per hour
        target = max(required_by_miles, required_by_hours)
        worth_it = net_dollars >= target
        result.update(
            {
                "required_by_miles": required_by_miles,
                "required_by_hours": required_by_hours,
                "target": target,
                "worth_it": worth_it,
            }
        )
    else:
        worth_it = net_dollars >= miles
        result.update({"worth_it": worth_it})

    return result


def print_order_summary(mode: str, rate: float, details: Dict[str, Union[float, bool]]) -> None:
    miles = float(details["miles"])
    est_time = float(details["est_time"])
    est_hours = float(details["est_hours"])
    dollars = float(details["dollars"])
    fuel_cost = float(details["fuel_cost"])
    net_dollars = float(details["net_dollars"])
    worth_it = bool(details["worth_it"])
    status = "worth taking" if worth_it else "skip it"

    print()
    if mode == "ebt":
        print(f"Pay type: Earn by Time @ ${rate:.2f}/hr | Estimated time: {est_time} minutes (~{est_hours:.2f} hrs)")
    else:
        required_by_miles = float(details["required_by_miles"])
        required_by_hours = float(details["required_by_hours"])
        target = float(details["target"])
        implied_hourly = dollars / est_hours if est_hours else 0.0
        net_implied_hourly = net_dollars / est_hours if est_hours else 0.0
        print("Pay type: Earn per Offer")
        print(f"Estimated time: {est_time} minutes (~{est_hours:.2f} hrs)")
        print(f"Per-mile target: ${required_by_miles:.2f} | Hourly target: ${required_by_hours:.2f} | Acceptance threshold: ${target:.2f}")
        print(f"Offer payout: ${dollars:.2f} | Fuel cost: ${fuel_cost:.2f} | Net: ${net_dollars:.2f}")
        print(f"Implied hourly (gross/net): ${implied_hourly:.2f} / ${net_implied_hourly:.2f}")

    print(f"Order miles: {miles}")
    print(f"Estimated dollars (gross): ${dollars:.2f}")
    print(f"Fuel cost estimate: ${fuel_cost:.2f}")
    print(f"Net after fuel: ${net_dollars:.2f}")
    print(f"Decision: {status}\n")


def standard_dialog(settings: Settings) -> None:
    print("DoorDash order checker (standard)")
    mode, rate = choose_pay_mode()

    while True:
        order_details = evaluate_order(mode, rate, settings)
        print_order_summary(mode, rate, order_details)

        again = prompt_yes_no("Check another order? (y/n): ", default=True)
        if again:
            continue

        if mode == "ebt":
            switch = prompt_yes_no("Switch to Earn per Offer? (y/n): ", default=False)
            if switch:
                mode = "ebo"
                rate = 0.0
                continue

        print("Good luck out there!")
        return


def dash_active_calc(settings: Settings) -> None:
    print("\nDash + active time payout calculator")
    while True:
        dash_hours = prompt_float("Dash time (hours): ")
        if dash_hours <= 0:
            print("Dash time must be greater than zero.")
            continue

        default_active_hours = dash_hours * settings.active_time_ratio
        active_hours = prompt_optional_float(
            f"Active time in hours (Enter to use ~{settings.active_time_ratio*100:.0f}% = {default_active_hours:.2f} hrs): ",
            default=default_active_hours,
        )
        if active_hours is None or active_hours <= 0:
            print("Active time must be greater than zero.")
            continue

        rate = prompt_float("Earn by Time hourly rate: $")
        payout = rate * active_hours

        hourly_on_dash = payout / dash_hours
        hourly_on_active = payout / active_hours
        active_ratio = (active_hours / dash_hours) * 100.0

        print("\n--- Dash recap ---")
        print(f"Dash time: {dash_hours:.2f} hrs | Active time: {active_hours:.2f} hrs (~{active_ratio:.0f}% active)")
        print(f"EBT rate: ${rate:.2f}/hr | Estimated payout (rate * active): ${payout:.2f}")
        print(f"Effective hourly (based on dash time): ${hourly_on_dash:.2f}")
        print(f"Effective hourly (based on active time): ${hourly_on_active:.2f}\n")

        if not prompt_yes_no("Run another dash calculation? (y/n): ", default=False):
            return


def daily_goal_dialog(settings: Settings) -> None:
    print("\nDaily goal tracker")
    goal = settings.daily_goal
    if goal is not None:
        use_existing = prompt_yes_no(f"Use existing daily goal (${goal:.2f})? (y/n): ", default=True)
        if not use_existing:
            goal = prompt_float("Set a new daily goal: $")
            settings.daily_goal = goal
    else:
        goal = prompt_float("Set a daily goal: $")
        settings.daily_goal = goal

    total_earnings = 0.0
    mode, rate = choose_pay_mode()

    while True:
        order_details = evaluate_order(mode, rate, settings)
        print_order_summary(mode, rate, order_details)

        take_order = prompt_yes_no("Take this order? (y/n): ", default=True)
        if take_order:
            if mode == "ebo":
                total_earnings += float(order_details["dollars"])
            else:
                actual_rate = prompt_float("Actual hourly rate (with incentives): $")
                actual_minutes = prompt_optional_float(
                    "Actual minutes for this order (Enter to use estimate): ", default=float(order_details["est_time"])
                )
                if actual_minutes is None or actual_minutes <= 0:
                    actual_minutes = float(order_details["est_time"])
                tip = prompt_float("Tip received for this order: $")
                total_earnings += (actual_rate * (actual_minutes / 60.0)) + tip

            print(f"Progress: ${total_earnings:.2f} earned / ${goal:.2f} goal")
            if total_earnings >= goal:
                print("Nice work — daily goal met or exceeded!")
        else:
            print("Order skipped; totals unchanged.")

        again = prompt_yes_no("Check another order with goal tracking? (y/n): ", default=True)
        if again:
            continue

        if mode == "ebt":
            switch = prompt_yes_no("Switch to Earn per Offer before ending? (y/n): ", default=False)
            if switch:
                mode = "ebo"
                rate = 0.0
                continue

        print(f"Session total: ${total_earnings:.2f} vs daily goal ${goal:.2f}")
        return


def settings_menu(settings: Settings) -> None:
    while True:
        print(
            "\nSettings:\n"
            f"1) Fuel price per gallon: ${settings.fuel_price_per_gal:.2f}\n"
            f"2) Average MPG: {settings.average_mpg:.2f}\n"
            f"3) Active time ratio (active/dash): {settings.active_time_ratio:.2f}\n"
            f"4) Daily goal (default for goal mode): "
            f"{f'${settings.daily_goal:.2f}' if settings.daily_goal is not None else 'not set'}\n"
            "5) Back to main menu"
        )
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            settings.fuel_price_per_gal = prompt_float("New fuel price per gallon: $")
        elif choice == "2":
            settings.average_mpg = prompt_float("New average MPG: ")
        elif choice == "3":
            while True:
                ratio = prompt_float("Active time ratio (0.10 - 1.00): ")
                if 0 < ratio <= 1:
                    settings.active_time_ratio = ratio
                    break
                print("Please enter a ratio between 0.1 and 1.0.")
        elif choice == "4":
            new_goal = prompt_optional_float("Set default daily goal (Enter to clear): ", default=None)
            settings.daily_goal = new_goal
        elif choice in ("5", "b", "back", "q", "exit"):
            return
        else:
            print("Please choose 1-5.")


def main_menu() -> None:
    settings = Settings()
    while True:
        print(
            "\nDoorDash order helper - main menu\n"
            "1) Standard order checker\n"
            "2) Dash + active time payout calculator\n"
            "3) Daily goal tracker\n"
            "4) Settings\n"
            "5) Quit"
        )
        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            standard_dialog(settings)
        elif choice == "2":
            dash_active_calc(settings)
        elif choice == "3":
            daily_goal_dialog(settings)
        elif choice == "4":
            settings_menu(settings)
        elif choice in ("5", "q", "quit", "exit"):
            print("See you on the next dash!")
            return
        else:
            print("Please choose 1-5.")


def main() -> int:
    main_menu()
    return 0


if __name__ == "__main__":
    sys.exit(main())

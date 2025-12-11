import sys

FUEL_PRICE_PER_GAL = 2.70  # baseline gas price
AVERAGE_MPG = 20.0  # vehicle fuel efficiency


def prompt_float(message: str) -> float:
    """Ask for a numeric value until one is provided."""
    while True:
        raw = input(message).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number (you can use decimals).")


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


def main() -> int:
    print("DoorDash order checker")
    mode, rate = choose_pay_mode()

    while True:
        miles = prompt_float("Order miles: ")
        est_time = prompt_positive_time()
        dollars = compute_dollars(mode, rate, est_time)
        est_hours = est_time / 60.0
        fuel_cost = (miles / AVERAGE_MPG) * FUEL_PRICE_PER_GAL
        net_dollars = dollars - fuel_cost

        if mode == "ebo":
            required_by_miles = miles  # $1 per mile
            required_by_hours = 14 * est_hours  # $14 per hour
            target = max(required_by_miles, required_by_hours)
            worth_it = net_dollars >= target
        else:
            worth_it = net_dollars >= miles

        status = "worth taking" if worth_it else "skip it"

        print()
        if mode == "ebt":
            print(f"Pay type: Earn by Time @ ${rate:.2f}/hr | Estimated time: {est_time} minutes (~{est_hours:.2f} hrs)")
        else:
            print("Pay type: Earn per Offer")
            implied_hourly = dollars / est_hours if est_hours else 0.0
            net_implied_hourly = net_dollars / est_hours if est_hours else 0.0
            print(f"Estimated time: {est_time} minutes (~{est_hours:.2f} hrs)")
            print(f"Per-mile target: ${required_by_miles:.2f} | Hourly target: ${required_by_hours:.2f} | Acceptance threshold: ${target:.2f}")
            print(f"Offer payout: ${dollars:.2f} | Fuel cost: ${fuel_cost:.2f} | Net: ${net_dollars:.2f}")
            print(f"Implied hourly (gross/net): ${implied_hourly:.2f} / ${net_implied_hourly:.2f}")
        print(f"Order miles: {miles}")
        print(f"Estimated dollars (gross): ${dollars:.2f}")
        print(f"Fuel cost estimate: ${fuel_cost:.2f}")
        print(f"Net after fuel: ${net_dollars:.2f}")
        print(f"Decision: {status}\n")

        again = input("Check another order? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("Good luck out there!")
            return 0


if __name__ == "__main__":
    sys.exit(main())

# DoorDash Order Checker

Small CLI helper for DoorDash drivers to sanity-check offers before accepting them. It estimates fuel cost, compares the run to simple targets, tracks daily goals, and includes a dash/active-time calculator.

## Requirements
- Python 3.9+ (no external packages needed)

## Running it
```bash
python ddchecker.py
```

## Main menu
- `1` Standard order checker: original flow with EBO/EBT, fuel cost, and worth-it call. If you end an EBT run, you can switch to EBO without restarting.
- `2` Dash + active time calculator: enter dash hours, active hours (defaults to 80% of dash), and your Earn by Time hourly rate to estimate payout and see effective hourly based on dash vs active time.
- `3` Daily goal tracker:
  - Set a daily goal (or reuse the one saved in Settings).
  - Run the standard EBO/EBT checks.
  - If you take the order:
    - EBO: payout is added to the running total.
    - EBT: enter actual hourly rate and tip to add to the total (actual minutes default to the estimate).
  - Progress is shown after each accepted order.
- `4` Settings: adjust fuel price, MPG, active time ratio, and a default daily goal.

## Standard flow recap
- Choose a pay type:
  - Earn per Offer (EBO): enter the offer payout.
  - Earn by Time (EBT): enter your hourly rate (without peak pay).
- Enter order miles and estimated time (minutes).
- The script estimates fuel cost using your configured fuel price/MPG, then prints the gross pay, fuel cost, net pay, and a decision.
- Decision rules:
  - EBO: must beat both $1 per mile and $14 per estimated hour (after fuel).
  - EBT: must beat $1 per mile (after fuel).

## Dash + active example
```text
DoorDash order helper - main menu
2
Dash time (hours): 8
Active time in hours (Enter to use ~80% = 6.40 hrs):
Earn by Time hourly rate: 18

--- Dash recap ---
Dash time: 8.00 hrs | Active time: 6.40 hrs (~80% active)
EBT rate: $18.00/hr | Estimated payout (rate * active): $115.20
Effective hourly (based on dash time): $14.40
Effective hourly (based on active time): $18.00
```

## Example session
```text
DoorDash order checker
Pay type (EBO = Earn per Offer, EBT = Earn by Time): ebo
Order miles: 8
Estimated time (minutes): 35
Offer payout: 16

Pay type: Earn per Offer
Estimated time: 35 minutes (~0.58 hrs)
Per-mile target: $8.00 | Hourly target: $8.12 | Acceptance threshold: $8.12
Offer payout: $16.00 | Fuel cost: $1.08 | Net: $14.92
Implied hourly (gross/net): $27.72 / $25.83
Order miles: 8
Estimated dollars (gross): $16.00
Fuel cost estimate: $1.08
Net after fuel: $14.92
Decision: worth taking
```

## Adjusting assumptions
- Use the Settings menu to change fuel price, MPG, active/dash ratio default, and a default daily goal.
- You can also edit the defaults directly in `ddchecker.py` (`FUEL_PRICE_PER_GAL`, `AVERAGE_MPG`, `DEFAULT_ACTIVE_RATIO`).

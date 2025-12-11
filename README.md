# DoorDash Order Checker

Small CLI helper for DoorDash drivers to sanity-check offers before accepting them. It estimates fuel cost, compares the run to simple targets, and tells you whether an order looks worth taking.

## Requirements
- Python 3.9+ (no external packages needed)

## Running it
```bash
python ddchecker.py
```

## How it works
- Choose a pay type:
  - Earn per Offer (EBO): enter the offer payout.
  - Earn by Time (EBT): enter your hourly rate (without peak pay).
- Enter order miles and estimated time (minutes).
- The script estimates fuel cost using `FUEL_PRICE_PER_GAL` and `AVERAGE_MPG` from `ddchecker.py`, then prints the gross pay, fuel cost, net pay, and a decision.
- Decision rules:
  - EBO: must beat both $1 per mile and $14 per estimated hour (after fuel).
  - EBT: must beat $1 per mile (after fuel).

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
- Update `FUEL_PRICE_PER_GAL` and `AVERAGE_MPG` near the top of `ddchecker.py` to match your car and local gas prices.

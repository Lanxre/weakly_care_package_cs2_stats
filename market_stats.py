import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, defaultdict
from enum import StrEnum
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from json import load

FILE_NAME = os.path.join(os.path.dirname(__file__), "steam_history_market.json")

class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"

@dataclass(frozen=True)
class MarketItem:
    name: str
    price: float
    currency: str
    listed_on: datetime
    acted_on: datetime

    def __repr__(cls):
        return f"\n<{cls.__class__.__name__}>(name={cls.name}, price={cls.price}, currency={cls.currency}, listed_on={cls.acted_on.date()}, acted_on={cls.acted_on.date()});\n"

def read_file(filepath: str) -> List[MarketItem]:
    with open(filepath, 'r') as file_data:
        res = [MarketItem(
            name=x.get('name', 'No Name'),
            price=x.get('price', 0.0),
            currency=x.get('currency', 'USD'),
            listed_on=datetime.strptime(x.get('listed_on').strip(), "%d %b %Y"),
            acted_on=datetime.strptime(x.get('acted_on').strip(), "%d %b %Y")
        ) for x in load(file_data)]
    
    return res

def get_total_price(items: List[MarketItem]) -> float:
    return sum([x.price for x in items])

def get_total_price_by_name(items: List[MarketItem]) -> Dict[str, Tuple[float, int]]:
    totals = {}

    for item in items:
        if item.name in totals:
            total_price, count = totals[item.name]
            totals[item.name] = (total_price + item.price, count + 1)
        else:
            totals[item.name] = (item.price, 1)
        
    sorted_totals = dict(
        sorted(totals.items(), key=lambda x: x[1][0], reverse=True)
    )
    
    return sorted_totals

def get_total_price_by_month(items: List[MarketItem]) -> Dict[str, Tuple[float, int]]:
    totals = defaultdict(lambda: (0.0, 0))

    for item in items:
        current = item.listed_on.replace(day=1)
        end = item.acted_on.replace(day=1)
        while current <= end:
            month_str = current.strftime("%Y-%b")
            total_price, count = totals[month_str]
            totals[month_str] = (total_price + item.price, count + 1)
            
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
    
    totals_sorted = dict(
        sorted(
            totals.items(), 
            key=lambda x: datetime.strptime(x[0], "%Y-%b")
        )
    )
    return totals_sorted

def print_total_price(total_price: float, total_price_by_name: Dict[str, float]) -> None:
    print(f"{'-'*45}")
    print(f"{'TOTAL PRICE':<15} | {total_price:>8.2f} {Currency.USD}")
    print(f"{'-'*45}\n")
    
    print(f"{'ITEM NAME':<15} | {'PRICE':>10}")
    print(f"{'-'*45}")
    for name, (price, count) in total_price_by_name.items():
        print(f"{name:<25} | {price:>10.2f} {Currency.USD} | {count} кол-во")
    print(f"{'-'*45}")

def print_month_sales(total_price_by_month: Dict[str, Tuple[float, int]]) -> None:
    print(f"{'MONTH':<10} | {'PRICE':>14} | {'COUNT':>5}")
    print(f"{'-'*45}")
    
    for month, (price, count) in total_price_by_month.items():
        print(f"{month:<10} | {price:>10.2f} {Currency.USD} | {count:>5} кол-во")
    
    print(f"{'-'*45}")

def plot_total_price_by_month(total_price_by_month: Dict[str, float]):
    months = list(total_price_by_month.keys())
    prices = [v[0] for v in total_price_by_month.values()]
    counts = [v[1] for v in total_price_by_month.values()]

    fig, ax1 = plt.subplots(figsize=(10,5))

    ax1.bar(months, prices, color='skyblue', label='Total Price', alpha=0.7)
    ax1.set_ylabel('Total Price (USD)', color='blue')
    ax1.set_xlabel('Month')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.plot(months, counts, color='red', marker='o', label='Count')
    ax2.set_ylabel('Count', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    plt.title('Total Price and Count per Month')
    fig.tight_layout()
    
    plt.savefig("total_price_by_month.png", bbox_inches='tight')

def plot_total_price_by_name(total_price: float, total_price_by_name: Dict[str, Tuple[float, int]]) -> None:
    names = list(total_price_by_name.keys())
    prices = [v[0] for v in total_price_by_name.values()]
    counts = [v[1] for v in total_price_by_name.values()]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    bars = ax1.bar(names, prices, color='skyblue', alpha=0.7, label='Total Price')
    ax1.set_ylabel('Total Price (USD)', color='blue')
    ax1.set_xlabel('Item Name')
    ax1.tick_params(axis='y', labelcolor='blue')
    plt.xticks(rotation=45, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(names, counts, color='red', marker='o', linewidth=2, label='Count')
    ax2.set_ylabel('Count', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    plt.title(f'Total Price and Count per Item')
    plt.text(0.95, 0.95, f'Total Price: {total_price:.2f} {Currency.USD}', 
             horizontalalignment='right', verticalalignment='top', 
             transform=ax1.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

    fig.tight_layout()
    plt.savefig("total_price_by_name.png", bbox_inches='tight')

def main() -> None:
    market_items = read_file(FILE_NAME)
    
    total_price = get_total_price(market_items)
    total_price_by_name = get_total_price_by_name(market_items)
    total_month_price = get_total_price_by_month(market_items)

    print(f"{'-'*19} TOTAL {'-'*19}")
    print_total_price(total_price, total_price_by_name)
    print_month_sales(total_month_price)

    plot_total_price_by_name(total_price, total_price_by_name)
    plot_total_price_by_month(total_month_price)

if __name__ == "__main__":
    main()
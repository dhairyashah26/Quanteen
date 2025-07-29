# momentum_strategy.py
# Author: Dhairya Shah

"""
This is a basic momentum strategy.
We assume that if a stock's price has been rising, it'll keep rising short-term.
Same for falling.

It's how FOMO turns into alpha (if you're lucky).
"""

import numpy as np
import matplotlib.pyplot as plt

# Simulate prices with upward/downward trend
np.random.seed(99)
price_changes = np.random.normal(loc=0.5, scale=2, size=100)
prices = np.cumsum(price_changes) + 100

# Calculate momentum (price today - price 5 days ago)
momentum = prices[5:] - prices[:-5]

# Signal: BUY if momentum > 0, SELL otherwise
signals = ['BUY' if m > 0 else 'SELL' for m in momentum]

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(prices, label="Stock Price")
plt.title("Momentum Strategy")
plt.xlabel("Time")
plt.ylabel("Price")
plt.grid(True)
plt.legend()
plt.show()

# Print sample output
print("Momentum signals (first 10):", signals[:10])

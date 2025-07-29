# mean_reversion_strategy.py
# Author: Dhairya Shah

"""
This is a basic mean reversion strategy simulation.
The idea: If a stock price falls far below its average, it's likely to bounce back — so we BUY.
If it rises far above average, we SELL.

This is the Gen Z way to bully the market.
"""

import numpy as np
import matplotlib.pyplot as plt

# Simulate 100 stock prices around 100
np.random.seed(42)
prices = np.random.normal(loc=100, scale=5, size=100)

# Calculate the mean
mean_price = np.mean(prices)

# Generate buy/sell signals
signals = ['BUY' if p < mean_price else 'SELL' for p in prices]

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(prices, label="Stock Price")
plt.axhline(mean_price, color='red', linestyle='--', label='Mean Price')
plt.title("Mean Reversion Strategy")
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()

# Print example signals
print(f"Mean Price: {mean_price:.2f}")
print("First 10 signals:", signals[:10])

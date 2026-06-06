import matplotlib.pyplot as plt

plt.figure(figsize=(10,4))
plt.scatter(df_regimes["timestamp"], df_regimes["atm_iv"],
            c=df_regimes["regime"], cmap="viridis")
plt.title("KO – Volatility Regimes")
plt.xlabel("Time")
plt.ylabel("ATM IV")
plt.grid(True)
plt.tight_layout()
plt.show()


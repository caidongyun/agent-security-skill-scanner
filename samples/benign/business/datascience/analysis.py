# Business: DataScience
# Collected: 2026-04-02 11:36:08.249701

#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('data.csv')
df.plot()
plt.savefig('chart.png')

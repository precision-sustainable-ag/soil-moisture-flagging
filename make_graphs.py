import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
import os
import json
import http.client
from flagit.src.flagit import flagit
from datetime import datetime, timedelta

cara_data = pd.read_csv("test_cara.csv")
aurelie_data = pd.read_csv("test_aurelie.csv")
both_data = pd.read_csv("test_both.csv")

# cara_subset = pd.DataFrame().assign(percent_human_bad=cara_data['percent_human_bad'], percent_flagit_bad=cara_data['percent_flagit_bad'])
# cara_subset.plot(style=['o','rx'])

plt.scatter(cara_data['percent_human_bad'], cara_data['percent_flagit_bad'])
plt.title("%Cara Flagged vs %Flagit Flagged")
plt.xlabel("%Human")
plt.ylabel("%%Flagit")
plt.savefig('cara_scatter.png')
plt.show() # Depending on whether you use IPython or interactive mode, etc.

plt.scatter(aurelie_data['percent_human_bad'], aurelie_data['percent_flagit_bad'])
plt.title("%Aurelie Flagged vs %Flagit Flagged")
plt.xlabel("%Human")
plt.ylabel("%%Flagit")
plt.savefig('aurelie_scatter.png')
plt.show() # Depending on whether you use IPython or interactive mode, etc.

plt.scatter(both_data['percent_human_bad'], both_data['percent_flagit_bad'])
plt.title("%Both Flagged vs %Flagit Flagged")
plt.xlabel("%Human")
plt.ylabel("%%Flagit")
plt.savefig('both_scatter.png')
plt.show() # Depending on whether you use IPython or interactive mode, etc.
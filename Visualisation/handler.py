import requests
import json
import datetime 
import sys,os
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import numpy as np

matplotlib.use('TkAgg')

# This let you download the data and save them on the disk for further use
# In order to charge the data you have to execute the code in the Vizualisation folder

# https://stackoverflow.com/questions/3160699/python-progress-bar
# quick and dirty progress bar
def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

# load the key from a json
with open("credential.json", "r") as file:
    KEY = json.load(file)['KEY']

# function to get the activity 
def get_activity(key,  end_date, begin_date = '2020-01-22', resolution='hour'):
    # date in format YYYY-MM-DD
    try:    
        activities = pandas.read_csv('data/rescuetime-' + begin_date + '-to-' + end_date + '.csv')
        activities = activities.drop("Unnamed: 0", 1) # remove the index created during the saving
    except:
        print("Unable to find local data on csv, fetching through the API (internet is required)")

        d1 = datetime.date.fromisoformat(begin_date)
        d2 = datetime.date.fromisoformat(end_date)
        delta_time = d2 - d1

        parameters = {
            'key': key,
            'perspective':'interval',
            'resolution_time': resolution,
            'restrict_begin': begin_date,
            'restrict_end': end_date,
            'format':'json', # JSON or csv
        }
        columns = ['Date','Seconds','NumberOfPeople','Activity','Category','Productivity']
        activities_list = []
        # get one day after another
        for i in progressbar(range(delta_time.days + 1), "Fetching", 100):
            current_day = d1 + datetime.timedelta(days=i)
            parameters['restrict_begin'] = str(current_day)
            parameters['restrict_end'] = str(current_day)
            try:
                # directly convert the response in json
                response = requests.get("https://www.rescuetime.com/anapi/data", parameters).json()
            except:
                print("Error collecting the data for " + current_day)
            if len(response) != 0 :
                for i in response['rows']:
                    activities_list.append(i)
            else: 
                print("There is no data for " + current_day)
        activities = pandas.DataFrame.from_dict(activities_list)
        activities.columns = columns
        try:
            if not(os.path.exists(os.path.join(os.getcwd(),'data'))):
                os.mkdir('data')
            activities.to_csv('data/rescuetime-' + begin_date + '-to-' + end_date + '.csv')
        except :
            print("Unable to write data on csv")

    return activities

activities = get_activity(key= KEY, begin_date = '2020-01-22', end_date = '2020-02-02', resolution='hour')

#activities.info()
#activities.describe()
#activities.tail()

activities['Productive'] = activities['Productivity']
# print(activities['Productive'].unique())

activities['Productive'] = activities['Productive'].map({-2: 'très distrayant', 
                                                        -1: 'distrayant',
                                                       0: 'Neutre',
                                                       1: 'Productif',
                                                       2: 'très productif'})


# print(activities.tail())

activities['Date'] = pandas.to_datetime(activities['Date'])

activities = activities.sort_values(by='Date').reset_index(drop=True)

activities['DateTime'] = activities['Date']
activities['Year'] = activities['Date'].apply(lambda x: x.strftime('%Y'))
activities['Month'] = activities['Date'].apply(lambda x: x.strftime('%m'))
activities['Hour'] = activities['Date'].apply(lambda x: x.strftime('%H'))
activities['Minutes'] = activities['Date'].apply(lambda x: x.strftime('%M'))
activities['Date'] = activities['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

# print(activities.tail())

###Total time per Day

total_computer_time_by_date = activities.groupby(['Date'])['Seconds'].sum().reset_index(name='Seconds')
total_computer_time_by_date['Minutes'] = round(total_computer_time_by_date['Seconds'] / 60, 2)
total_computer_time_by_date['Hours'] = round(total_computer_time_by_date['Seconds'] / 60 / 60, 2)
total_computer_time_by_date.tail()

total_computer_time_by_date = total_computer_time_by_date.drop(['Seconds', 'Minutes'], axis=1)
total_computer_time_by_date = total_computer_time_by_date.set_index(['Date'])

chart_title = 'Daily Computer Time in Hours for Last 30 Days'
# plt.style.use('seaborn-darkgrid')
ax = total_computer_time_by_date.tail(30).plot.bar(stacked=True, rot=90, figsize=(12,6), colormap='tab20c', legend=False)
ax.set_xlabel('')
ax.set_ylabel('Hours')
ax.set_title(chart_title)
#plt.show()
# plt.savefig("fig.png")


# total_by_date_productivity
total_by_date_productivity = activities.groupby(['Date', 'Productive'])['Seconds'].sum().reset_index(name='Seconds')
total_by_date_productivity['Minutes'] = round((total_by_date_productivity['Seconds'] / 60), 2)
total_by_date_productivity['Hours'] = round((total_by_date_productivity['Seconds'] / 60 / 60), 2)
table = total_by_date_productivity.pivot_table(index='Date', columns='Productive', values='Hours', aggfunc=np.sum)
table.to_csv("data/days_productive_time_full.csv")

# process and simplify productivity dimensions
days_productive_time = table.fillna(value=0).copy()
days_productive_time['productive_simple'] = days_productive_time['Productif'] + days_productive_time['très productif']
days_productive_time.drop(['Productif', 'très productif'], axis=1, inplace=True)
days_productive_time['distracting_simple'] = days_productive_time['distrayant'] + days_productive_time['très distrayant']
days_productive_time.drop(['distrayant', 'très distrayant'], axis=1, inplace=True)
days_productive_time.columns = ['Neutral', 'Productive', 'Distracting']



chart_title = 'Daily Computer Time Broken Down by Productivity for Last 30 Days'
# plt.style.use('seaborn-darkgrid')
ax = days_productive_time.tail(30).plot.bar(stacked=True, rot=90, figsize=(12,6))
ax.set_xlabel('')
ax.set_ylabel('Hours')
ax.set_title(chart_title)
#plt.show()

activities.info()
print(activities.tail())

total_time_hours = activities.groupby(['Hour','Date'])['Seconds'].sum().reset_index()
#total_time_hours = 
print("patate")
print(total_time_hours)
#total_time_hours_resample = activities.resample('H','columns' )
print("patate2")
# print(total_time_hours["Seconds"].get_group(("00", "2020-01-25")).sum())


def heat_map(series, begin_date=None, end_date=None):
    d1 = datetime.date.fromisoformat(begin_date)
    d2 = datetime.date.fromisoformat(end_date)
    delta_time = d2 - d1
    result = np.zero()

set_days = set([x[1].Date for x in total_time_hours.iterrows()])
n_days = len(set_days)
x_labels = sorted(list(set_days))
y_labels = [f"{i:02d}" for i in range(24)]
heat_map_values = np.zeros((24, n_days))

for i in range(len(x_labels)):
	for j in range(len(y_labels)):
		date = x_labels[i]
		hour = y_labels[j]
		temp = total_time_hours[total_time_hours["Hour"] == hour]
		temp = temp[temp["Date"] == date]["Seconds"]
		if len(temp) == 0:
			heat_map_values[j, i] = 0
		else:
			assert len(temp) == 1, f"More than 1 entry returned ({len(temp)})"
			heat_map_values[j, i] = temp.iloc(0)[0]

plt.set_cmap("Greys")
fig, ax = plt.subplots()
im = ax.imshow(heat_map_values)
plt.colorbar(im, ax=ax, ticks=range(0, int(np.max(heat_map_values)), int(np.max(heat_map_values / 15))))


# We want to show all ticks...
ax.set_xticks(np.arange(len(x_labels)))
ax.set_yticks(np.arange(len(y_labels)))
# ... and label them with the respective list entries
ax.set_xticklabels(x_labels)
ax.set_yticklabels(y_labels)

# Rotate the tick labels and set their alignment.
plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")

# Loop over data dimensions and create text annotations.
#for i in range(len(y_labels)):
 #   for j in range(len(x_labels)):
 #       text = ax.text(j, i, heat_map_values[i, j],
 #                      ha="center", va="center", color="w")

ax.set_title("Un joli graphique")
fig.tight_layout()
plt.show()

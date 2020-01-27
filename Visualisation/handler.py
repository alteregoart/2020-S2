import requests
import json
import datetime 
import sys,os
import pandas

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

activities = get_activity(key= KEY, begin_date = '2020-01-22', end_date = '2020-01-27', resolution='hour')

activities.info()
activities.describe()
activities.tail()

print(activities.Seconds.sum()/60/60)
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
import requests
import math
from pick import pick
import pytz
import urllib
import datetime
from secrets import key, maxDurationOfProjects, minDurationOfProjects

f = open("times.txt", "w")

api = 'https://api.track.toggl.com/api/'
apiVersion = 'v8'
apiUrl = api+apiVersion+'/'

endDate = datetime.datetime.now(pytz.utc)
startDate = endDate - datetime.timedelta(days=7)
startMonthDate = endDate - datetime.timedelta(days=30)
endDate = str(endDate.replace(microsecond=0).isoformat())
startDate = str(startDate.replace(microsecond=0).isoformat())
startMonthDate = str(startMonthDate.replace(microsecond=0).isoformat())

try:
    from secrets import singleWorkSpace
    workspaceId = singleWorkSpace
except:
    workspaces = requests.get(
        apiUrl+'workspaces', auth=(key, 'api_token')).json()

    workspacesList = {}
    for workspace in workspaces:
        workspacesList.update({
            workspace['id']: workspace['name'],
        })

    workspacesOptions = workspacesList.values()
    workspacesIds = workspacesList.keys()

    workspace, index = pick(list(workspacesOptions), "Select a Workspace:")

    position = list(workspacesOptions).index(workspace)

    workspaceId = list(workspacesIds)[position]


class Project:
    def __init__(self, id, name, duration, monthDuration):
        self.id = id
        self.name = name
        self.duration = duration
        self.monthDuration = monthDuration


projects = requests.get(apiUrl+'workspaces/' + str(workspaceId) + '/projects',
                        auth=(key, 'api_token')).json()

projectsList = {}

for project in projects:
    project = Project(project['id'], project['name'], 0, 0)
    projectsList.update({
        project.id: project,
    })

timeEntries = requests.get(apiUrl+urllib.parse.quote('time_entries?start_date=' +
                           startDate+'&end_date='+endDate, safe='=?&'), auth=(key, 'api_token')).json()

timeMonthEntries = requests.get(apiUrl+urllib.parse.quote('time_entries?start_date=' +
                                                          startMonthDate+'&end_date='+endDate, safe='=?&'), auth=(key, 'api_token')).json()

totalWeekTime = 0

totalMonthTime = 0

for timeEntry in timeEntries:
    try:
        projectId = timeEntry['pid']
    except:
        projectId = 0
    try:
        project = projectsList[projectId]
        project.duration += timeEntry['duration']
        projectsList.update({
            project.id: project,
        })
        totalWeekTime += timeEntry['duration']
    except:
        pass


for timeEntry in timeMonthEntries:
    try:
        projectId = timeEntry['pid']
    except:
        projectId = 0
    try:
        project = projectsList[projectId]
        project.monthDuration += timeEntry['duration']
        projectsList.update({
            project.id: project,
        })
        totalMonthTime += timeEntry['duration']
    except:
        pass

if maxDurationOfProjects and minDurationOfProjects:
    for project in projectsList.values():
        try:
            maxDurationOfProjects[project.name]
            minDurationOfProjects[project.name]
        except:
            try:
                maxDurationOfProjects[project.name]
            except:
                maxDurationOfProjects.update({
                    project.name: 0,
                })
            minDurationOfProjects.update({
                project.name: 0,
            })
        if maxDurationOfProjects[project.name] < project.duration/3600:
            f.write(project.name+': '+str(math.ceil(project.duration/360)/10)+'h per week - OverDo! with ' +
                    str(math.ceil((project.duration/3600 - maxDurationOfProjects[project.name])*10)/10)+'h exceeded\n')
        elif minDurationOfProjects[project.name] > project.duration/3600:
            f.write(project.name+': ' + str(math.ceil(project.duration/360)/10)+'h per week - Work More! You need ' +
                    str(math.ceil((minDurationOfProjects[project.name] - project.duration/3600)*10)/10)+'h more to reach your goal\n')
        else:
            f.write(project.name+': ' +
                    str(math.ceil(project.duration/360)/10)+'h per week - Good...\n')
        if maxDurationOfProjects[project.name]*4 < project.monthDuration/3600:
            f.write(project.name+': '+str(math.ceil(project.monthDuration/360)/10)+'h per month - OverDo! with ' +
                    str(math.ceil((project.monthDuration/3600 - maxDurationOfProjects[project.name]*4)*10)/10)+'h exceeded\n\n')
        elif minDurationOfProjects[project.name]*4 > project.monthDuration/3600:
            f.write(project.name+': ' + str(math.ceil(project.monthDuration/360)/10)+'h per month - Work More! You need ' +
                    str(math.ceil((minDurationOfProjects[project.name]*4 - project.monthDuration/3600)*10)/10)+'h more to reach your goal\n\n')
        else:
            f.write(project.name+': ' +
                    str(math.ceil(project.monthDuration/360)/10)+'h per month - Good...\n\n')
elif maxDurationOfProjects:
    for project in projectsList.values():
        try:
            maxDurationOfProjects[project.name]
        except:
            maxDurationOfProjects.update({
                project.name: 0,
            })
        if maxDurationOfProjects[project.name] < project.duration/3600:
            f.write(project.name+': '+str(math.ceil(project.duration/360)/10)+'h per week - OverDo! with ' +
                    str(math.ceil((project.duration/3600 - maxDurationOfProjects[project.name])*10)/10)+'h exceeded\n')
        else:
            f.write(project.name+': ' +
                    str(math.ceil(project.duration/360)/10)+'h per week - Good...\n')
        if maxDurationOfProjects[project.name]*4 < project.monthDuration/3600:
            f.write(project.name+': '+str(math.ceil(project.monthDuration/360)/10)+'h per month - OverDo! with ' +
                    str(math.ceil((project.monthDuration/3600 - maxDurationOfProjects[project.name]*4)*10)/10)+'h exceeded\n\n')
        else:
            f.write(project.name+': ' +
                    str(math.ceil(project.monthDuration/360)/10)+'h per month - Good...\n\n')

f.write('Total Week Time: '+str(math.ceil(totalWeekTime/360)/10)+'h\n\n')
f.write('Total Month Time: '+str(math.ceil(totalMonthTime/360)/10)+'h\n\n')

f.close()


# Creating dataset
chartSize = 0
chartProjects = []
chartData = []
chartMonthData = []
for project in projectsList.values():
    if project.duration/3600 > 0.25 and project.monthDuration/3600 > 1:
        chartSize += 1
        chartProjects.append(project.name)
        chartData.append(project.duration)
        chartMonthData.append(project.monthDuration)

# Creating color scale
colors = cm.Set1(np.arange(chartSize)/chartSize)

# create a figure with two subplots
fig, (week, month) = plt.subplots(1, 2)

# plot each pie chart in a separate subplot
week.pie(chartData, labels=chartProjects, colors=colors,
        autopct='%1.1f%%', startangle=90)
month.pie(chartMonthData, labels=chartProjects, colors=colors,
        autopct='%1.1f%%', startangle=90)

plt.show()
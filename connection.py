import requests
import math
from pick import pick
import pytz
import urllib
import datetime
from secrets import key, maxDurationOfProjects

f = open("times.txt", "w")

api = 'https://api.track.toggl.com/api/'
apiVersion = 'v8'
apiUrl = api+apiVersion+'/'

endDate = datetime.datetime.now(pytz.utc)
startDate = endDate - datetime.timedelta(days=7)
endDate = str(endDate.replace(microsecond=0).isoformat())
startDate = str(startDate.replace(microsecond=0).isoformat())

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
    def __init__(self, id, name, duration):
        self.id = id
        self.name = name
        self.duration = duration


projects = requests.get(apiUrl+'workspaces/' + str(workspaceId) + '/projects',
                        auth=(key, 'api_token')).json()

projectsList = {}

for project in projects:
    project = Project(project['id'], project['name'], 0)
    projectsList.update({
        project.id: project,
    })

timeEntries = requests.get(apiUrl+urllib.parse.quote('time_entries?start_date=' +
                           startDate+'&end_date='+endDate, safe='=?&'), auth=(key, 'api_token')).json()

totalMonthTime = 0

for timeEntry in timeEntries:
    projectId = timeEntry['pid']
    try:
        project = projectsList[projectId]
        project.duration += timeEntry['duration']
        projectsList.update({
            project.id: project,
        })
        totalMonthTime += timeEntry['duration']
    except:
        pass

if maxDurationOfProjects:
    for project in projectsList.values():
        try:
            maxDurationOfProjects[project.name]
        except:
            maxDurationOfProjects.update({
                project.name: 0,
            })
        if maxDurationOfProjects[project.name] < project.duration/3600:
            f.write(project.name+': '+str(math.ceil(project.duration/360)/10)+'h - OverDo! with ' +
                    str(math.ceil((project.duration/3600 - maxDurationOfProjects[project.name])*10)/10)+'h exceeded\n')
        else:
            f.write(project.name+': ' +
                    str(math.ceil(project.duration/360)/10)+'h - Good...\n')

f.write('Total Time: '+str(math.ceil(totalMonthTime/360)/10)+'h')
f.close()

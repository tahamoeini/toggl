import requests
from pick import pick
import pytz
import urllib
import datetime
from secrets import key

api = 'https://api.track.toggl.com/api/'
apiVersion = 'v8'
apiUrl = api+apiVersion+'/'

# authResponse = requests.get(apiUrl+'me?with_related_data=true', auth=(key,'api_token')).json()
# data = authResponse['data']
# authResponseFast = requests.get(apiUrl+'me', auth=(key,'api_token')).json()
# dataFast = authResponseFast['data']


endDate = datetime.datetime.now(pytz.utc)
startDate = endDate - datetime.timedelta(days=7)
endDate = str(endDate.replace(microsecond=0).isoformat())
startDate = str(startDate.replace(microsecond=0).isoformat())

workspaces = requests.get(apiUrl+'workspaces', auth=(key, 'api_token')).json()

print(workspaces)

workspacesList = {}
for workspace in workspaces:
    workspacesList[workspace['id']] = workspace['name']

workspacesOptions = workspacesList.values()
workspacesIds = workspacesList.keys()

print(workspacesOptions)
print(workspacesIds)

workspace, index = pick(list(workspacesOptions), "Select a Workspace:")

position = list(workspacesOptions).index(workspace)

workspaceId = list(workspacesIds)[position]

projects = requests.get(apiUrl+'workspaces/' + str(workspaceId) + '/projects',
                        auth=(key, 'api_token')).json()

projectsList = {}
for project in projects:
    projectsList[project['id']] = project['name']

projectsOptions = projectsList.values()
projectsIds = projectsList.keys()

project, index = pick(list(projectsOptions), "Select a Project:")

position = list(projectsOptions).index(project)

projectId = list(projectsIds)[position]

# timeEntries = requests.get(apiUrl+urllib.parse.quote('time_entries?start_date='+startDate+'&end_date='+endDate,safe='=?&'), auth=(key,'api_token')).json()

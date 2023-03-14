# Creates a CSV with  in progress issues, size estimate, and number of days in progress
# Uses v3 of GitHub's Enterprise API and ZenHub API
# Contact Lucas Danzinger with any questions
# Requires Python 3
# Usage:
# python IssueReport.py -ol <output_location> -gt <github_token> -zt <zenhub_token> -m <milestone_number>

import argparse
import csv
import requests
import time
import numpy as np
from datetime import datetime


# create a list of the field headings that should be included in the generated report
CSV_COLUMN_HEADINGS = ['title', 'url', 'added_date', 'current_date', 'estimate', 'days_in_progress']

# Get the deserialized JSON
def get_request(url, headers):
    '''
    Gets the JSON response of a given URL and formats it into a data dictionary.

    Parameters
        url (str) - The URL at which the response can be found
        headers (str) - Any necessary headers to include with the GET request
    Returns
        A dictionary that represents a deserialized JSON response.
    '''
    try:
        response = requests.get(url=url, headers=headers, verify=False)
        data = response.json()
    except e:
        print(e)
    else:
        if 'error' in data:
            print(data['error']['message'])
            for detail in data['error']['details']:
                print(detail)
        else:
            return data
            
            
def post_slack(output_csv, token):
    my_file = {
        'file' : (output_csv, open(output_csv, 'rb'), 'png')
    }

    payload={
        "filename":output_csv,
        "token":token,
        "channels":['D02LSNGDJE6'],
    }

    requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ol', '--output_location', required=True,
                        help='The location to which the output .csv should be saved.')
    parser.add_argument('-gt', '--github_token', required=True,
                        help='The GitHub personal access token that grants access to the required repository and its projects. '
                        'A token can be created at: Devtopia Settings > Developer Settings > Personal Access Tokens.'
                        'At least "repo" access is required.')
    parser.add_argument('-zt', '--zenhub_token', required=True,
                        help='The ZenHub personal access token that grants access to the required repository and its projects. '
                        'A token can be created at: https://zentopia.esri.com/app/dashboard/tokens > "Generate New Token".')
    parser.add_argument('-st', '--slack_token', required=True),
    
    
    args = parser.parse_args()

    # define the output file location and name
    current_time = time.strftime('%a-%b-%d_%I-%M%p', time.localtime())
    output_csv = '{0}/in_progress_report_{1}.csv'.format(args.output_location, current_time)

    # set the authentication query used to gain access
    github_authentication_str = {'Authorization' : 'token {0}'.format(args.github_token)}
    # zenhub_authentication_str = {'X-Authorization' : 'token {0}'.format(args.zenhub_token)}
    zenhub_authentication_str = '?access_token=' + args.zenhub_token

    # GitHub's Enterprise API endpoint used by Devtopia
    github_api_endpoint = 'https://devtopia.esri.com/api/v3'
    zenhub_api_endpoint = 'https://zentopia.esri.com/api/p1/repositories/2878/issues' # Note - 2878 is the qt-common repo ID
    zenhub_api_endpoint_new = 'https://zentopia.esri.com/api/p2/workspaces/5af375259165400f0c3c8245/repositories/2878/board' # Note - 5af375259165400f0c3c8245 is the workspace id for arcgis-runtime-sdk-for-qt
            

    with open(file=output_csv, mode='w', newline='\n') as csv_file:
        writer = csv.DictWriter(f=csv_file, fieldnames=CSV_COLUMN_HEADINGS)
        writer.writeheader()
        pipelines = []
        issues = []
        results_available = True
        
        #getting all pipelines from zenhub
        zissue = get_request("{0}/{1}".format(zenhub_api_endpoint_new, zenhub_authentication_str), {})
        [pipelines.append(pipeline) for pipeline in zissue["pipelines"]]            
                
        for pipeline in pipelines:
            if pipeline["name"] == "In Progress":
                
                [issues.append(issue) for issue in pipeline["issues"]]
                
                for issue in issues:                     
        
                    # create in progress info dict
                    in_progress_info = {}
                    estimate = issue["estimate"]["value"]
                    issue_number= issue["issue_number"]
                    zissueevents = get_request("{0}/{1}/events{2}".format(zenhub_api_endpoint, issue_number, zenhub_authentication_str), {})
                    inProgressEvents = []
                    for zevent in zissueevents:
                        if zevent["type"] == "transferIssue":
                            if zevent["to_pipeline"]["name"] == "In Progress":
                                inProgressEvents.append(zevent)
                    in_progress_event = inProgressEvents[0]
                    # get information from git repo
                    issue_url = "{0}/repos/runtime/qt-common/issues/{1}".format(github_api_endpoint, issue_number)
                    git_issue = get_request('{0}'.format(issue_url), github_authentication_str)
                    in_progress_info['title'] = git_issue['title']
                    in_progress_info['url'] = git_issue['url'].replace('api/v3/repos/', '')
                    
                    in_progress_info['added_date']  = in_progress_event['created_at']
                    in_progress_info['current_date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    in_progress_info['estimate'] = estimate
                    
                
                    if (in_progress_info):
                        # get time delta (in days) from added to current date
                        beg_date = datetime.strptime(in_progress_info['added_date'][:10], '%Y-%m-%d')
                        cur_date = datetime.strptime(in_progress_info['current_date'][:10], '%Y-%m-%d')
                        delta = np.busday_count(beg_date.date(), cur_date.date())
                        in_progress_info['days_in_progress'] = delta
                
                        # write the output to a csv file
                        writer.writerow(in_progress_info)
    
post_slack(output_csv, 'xoxb-12801775347-880413376036-RCOVwy40NSTRYFAe2bYi5Tl8')


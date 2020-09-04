
# Import the Canvas class
from canvasapi import Canvas

import json, csv

from canvasapi.submission import Submission
from canvasapi.paginated_list import PaginatedList

from canvasapi.requester import Requester
from canvasapi.util import combine_kwargs

from configparser import ConfigParser

import time
import random
import re

from pprint import pprint

from umich_api.api_utils import ApiUtil

from requests import Response
import pandas as pd


parser = ConfigParser()
parser.read('./config.txt')

# Canvas API key
API_URL = parser.get('API_SETTINGS', 'API_URL')
API_KEY = parser.get('API_SETTINGS', 'API_KEY')

import json, logging, os
from umich_api.api_utils import ApiUtil

# Related documentation
# https://virtualenv.pypa.io/en/latest/
# https://docs.python.org/3/library/logging.html
# https://requests.readthedocs.io/en/master/api/#requests.Response
# 

# Load configuration dictionary, set up logging and constants

with open('config/apis.json', 'r', encoding='utf-8') as config_file:
    CONFIG_DICT = json.loads(config_file.read())

# Better to use logging here so you can see all the output from umich_api by specifying DEBUG
logging.basicConfig(level=CONFIG_DICT['LOG_LEVEL'])
logger = logging.getLogger(__name__)

API_UTIL = ApiUtil(CONFIG_DICT['BASE_URL'], CONFIG_DICT['CLIENT_ID'], CONFIG_DICT['SECRET'])
print(CONFIG_DICT['BASE_URL'])
print(CONFIG_DICT['CLIENT_ID'])
print(CONFIG_DICT['SECRET'])

MCOMM_URL_ENDING = 'MCommunity/People/'
MCOMM_SCOPE = 'mcommunity'

# Function(s)
def get_role_info_using_uniqname(uniqname):
    url_ending = MCOMM_URL_ENDING + uniqname
    response = API_UTIL.api_call(url_ending, MCOMM_SCOPE)
    logger.debug(response.status_code)
    data = json.loads(response.text)
    person_data = data['person']
    logger.info(person_data)
    if person_data['errors'] != '':
        error = person_data['errors']['field']['description']
        logger.error(f'Encountered an error: {error}')
        logger.error('Function will return an empty list of roles.')
        return []
    elif 'affiliation' in person_data:
        roles = data['person']['affiliation']
        logger.info(f'Roles found for {uniqname}: {roles}')
        return roles
    else:
        return []

###### GLOBAL VARIABLES AND API ACCESS #####
COURSE_ID = parser.get('MED_COURSE', 'MED_COURSE_ID')
ASSIGNMENT_ID = parser.get('MED_COURSE', 'MED_ASSIGNMENT_ID')
SCORE_THRESHOLD = float(parser.get('MED_COURSE', 'MED_SCORE_THRESHOLD'))

STUDENT_ID_LIST = []

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)
assignment = course.get_assignment(ASSIGNMENT_ID)
#quiz_72 = course.get_quiz(QUIZ_ID_72)
submissions = assignment.get_submissions()

logger.info(assignment)


# output rubric setting information
rubric = assignment.rubric
pprint(rubric)


# read the rubric assessment setting from config file
assessment_json = json.load(open('./assessment_nonmed.json'))
assessment_med_json = json.load(open('./assessment_med.json'))
assessment_lowgrade_json = json.load(open('./assessment_lowgrade.json'))


# get student submissions and update the assessment
start=time.time()
STUDENT_ID_LIST = [student.user_id for student in submissions]

kwargs= {
    "type[]" : ["StudentEnrollment"],
    "state[]": "active"
}
enrollments = course.get_enrollments()

submissions = assignment.get_submissions

student_count = 1
student_list_length = len(STUDENT_ID_LIST)

# create a dataframe for students
df = pd.DataFrame(columns=['id','login_id','score', 'in_medical_school'])

for student_enrollment in enrollments:

    print(f"update {student_count} of {student_list_length}")

    user_id = student_enrollment.user_id
    student_count += 1
    if (student_enrollment.user_id in STUDENT_ID_LIST and
        user_id not in df['id'].tolist()):
        current_score = student_enrollment.grades["current_score"]
        logger.info(current_score)
        if (current_score is not None and float(current_score) >= SCORE_THRESHOLD):
            #pprint(student_enrollment)
            user_uniqname = student_enrollment.user["login_id"]
            user_affiliations = get_role_info_using_uniqname(user_uniqname)
            in_medical_school = False
            if len(user_affiliations) > 0:
                #look for medical school affiliation: 
                # ['Medical - Student', 
                # 'Medicine MD - Student', 
                # 'HITS OCIO Administration - Sponsored Affiliate'
                for affiliation in user_affiliations:
                    if (re.search('medical', affiliation, re.IGNORECASE)
                        or re.search('medicine', affiliation, re.IGNORECASE)):
                        in_medical_school = True
                        break
            
            df = df.append({'id': user_id, 'login_id': user_uniqname, 'score': current_score, 'in_medical_school': in_medical_school}, ignore_index = True)

            submission = assignment.get_submission(user=user_id)
            if in_medical_school:
                # for medical students
                submission.edit(
                    rubric_assessment=assessment_med_json
                )
            else:
                # for other students
                submission.edit(
                    rubric_assessment=assessment_json
                )
        else:
            # for students with low course grade
            # assign 0 for dosage and other rubrics
            submission.edit(
                rubric_assessment=assessment_lowgrade_json
            )


elapsed_time = (time.time()-start)
print(elapsed_time)
print('List of all updated students: \n')
pprint(df)
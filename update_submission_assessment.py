
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

parser = ConfigParser()
parser.read('./config.txt')

API_URL = parser.get('API_SETTINGS', 'API_URL')
# Canvas API key
API_KEY = parser.get('API_SETTINGS', 'API_KEY')

###### GLOBAL VARIABLES AND API ACCESS #####
COURSE_ID = parser.get('COURSE', 'COURSE_ID')
ASSIGNMENT_ID_73 = parser.get('COURSE', 'ASSIGNMENT_ID_73')
ASSIGNMENT_ID_72 = parser.get('COURSE', 'ASSIGNMENT_ID_72')
QUIZ_ID_72 = parser.get('COURSE', 'QUIZ_ID_72')
# STUDENT_ID = parser.get('COURSE', 'STUDENT_ID')
STUDENT_ID_LIST = []

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)
assignment_73 = course.get_assignment(ASSIGNMENT_ID_73)
quiz_72 = course.get_quiz(QUIZ_ID_72)
quiz_72_submissions = quiz_72.get_submissions()


# get assignment attributes
attr_json = json.loads(json.dumps(assignment_73.attributes))

# output rubric setting information
if "rubric_settings" in attr_json:
    rubric_settings = attr_json["rubric_settings"]
    print("rubric setting")
    print(rubric_settings)
if "rubric" in attr_json:
    rubric = attr_json["rubric"]
    print(rubric)

# read the rubric assessment setting from config file
assessment_json = json.load(open('./assessment.json'))

# get student submissions and update the assessment
start=time.time()
STUDENT_ID_LIST = [student.user_id for student in quiz_72_submissions]

for student_id in STUDENT_ID_LIST:
    submission = assignment_73.get_submission(user=student_id)
    submission.edit(
        rubric_assessment=assessment_json
    )

elapsed_time = (time.time()-start)
print(elapsed_time)
print(random.sample(STUDENT_ID_LIST,20))
# print('List of all updated students: \n {}'.format(STUDENT_ID_LIST))

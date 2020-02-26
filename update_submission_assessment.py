
# Import the Canvas class
from canvasapi import Canvas

import json, csv



from canvasapi.submission import Submission
from canvasapi.paginated_list import PaginatedList

from canvasapi.requester import Requester
from canvasapi.util import combine_kwargs

from configparser import ConfigParser

parser = ConfigParser()
parser.read('./config.txt')

print(parser.get('API_SETTINGS', 'API_URL'))
print(parser.get('API_SETTINGS', 'API_KEY'))

#read from config file
config_file = open("./config.txt", 'r')
content = config_file.read()
paths = content.split("\n") #split it into lines
for path in paths:
    path_parts=path.split("=")
    

API_URL = parser.get('API_SETTINGS', 'API_URL')
# Canvas API key
API_KEY = parser.get('API_SETTINGS', 'API_KEY')

###### GLOBAL VARIABLES AND API ACCESS #####
COURSE_ID = parser.get('COURSE', 'COURSE_ID')
ASSIGNMENT_ID = parser.get('COURSE', 'ASSIGNMENT_ID')
STUDENT_ID = parser.get('COURSE', 'STUDENT_ID')

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)

assignment = course.get_assignment(ASSIGNMENT_ID)
print(course)

# get assignment attributes
attr_json = json.loads(json.dumps(assignment.attributes))

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

# get student submission and update the assessment
submission = assignment.get_submission(user=STUDENT_ID)
submission.edit(
    rubric_assessment=assessment_json
)

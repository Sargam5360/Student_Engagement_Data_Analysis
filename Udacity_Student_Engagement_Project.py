
# coding: utf-8

# ## Load Data from CSVs

# In[1]:

import unicodecsv

def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)

enrollments = read_csv('enrollments.csv')
daily_engagement = read_csv('daily_engagement.csv')
project_submissions = read_csv('project_submissions.csv')


# In[2]:

enrollments[0]


# In[3]:

daily_engagement[0]


# In[4]:

project_submissions[0]


# ## Fixing Data Types

# In[5]:

from datetime import datetime as dt

# Takes a date as a string, and returns a Python datetime object. 
# If there is no date given, returns None
def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')
    
# Takes a string which is either an empty string or represents an integer,
# and returns an int or None.
def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(i)

# Clean up the data types in the enrollments table
for enrollment in enrollments:
    enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
    enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
    enrollment['is_canceled'] = enrollment['is_canceled'] == 'True'
    enrollment['is_udacity'] = enrollment['is_udacity'] == 'True'
    enrollment['join_date'] = parse_date(enrollment['join_date'])
    
enrollments[0]


# In[6]:

# Clean up the data types in the engagement table
for engagement_record in daily_engagement:
    engagement_record['lessons_completed'] = int(float(engagement_record['lessons_completed']))
    engagement_record['num_courses_visited'] = int(float(engagement_record['num_courses_visited']))
    engagement_record['projects_completed'] = int(float(engagement_record['projects_completed']))
    engagement_record['total_minutes_visited'] = float(engagement_record['total_minutes_visited'])
    engagement_record['utc_date'] = parse_date(engagement_record['utc_date'])
    
daily_engagement[0]


# In[7]:

# Clean up the data types in the submissions table
for submission in project_submissions:
    submission['completion_date'] = parse_date(submission['completion_date'])
    submission['creation_date'] = parse_date(submission['creation_date'])

project_submissions[0]


# ## Investigating the Data and Problems in the Data

# In[8]:

# Change the "acct" field to "account_key" in the daily_engagement to be consistent with the other tables
for engagement_record in daily_engagement:
    engagement_record['account_key'] = engagement_record['acct']
    del[engagement_record['acct']]


# In[9]:

# Returns a set with the unique values of "account_key" within the given data
def get_unique_students(data):
    unique_students = set()
    for data_point in data:
        unique_students.add(data_point['account_key'])
    return unique_students


# In[10]:

# See how many enrollments there are
len(enrollments)


# In[11]:

# See how many unique students enrolled
unique_enrolled_students = get_unique_students(enrollments)
len(unique_enrolled_students)


# In[12]:

# See how many records of daily engagement we have
len(daily_engagement)


# In[13]:

# See how many unique students we have engagement data on
unique_engagement_students = get_unique_students(daily_engagement)
len(unique_engagement_students)


# In[14]:

# See how many projects were submitted
len(project_submissions)


# In[15]:

# See how many unique students submitted projects
unique_project_submitters = get_unique_students(project_submissions)
len(unique_project_submitters)


# ## Missing Engagement Records

# In[16]:

# Look at a student who enrolled but doesn't have engagement numbers
for enrollment in enrollments:
    student = enrollment['account_key']
    if student not in unique_engagement_students:
        print enrollment
        break


# ## Checking for More Problem Records

# In[17]:

# Find students who enrolled, don't have engagement numbers, and stayed enrolled at least a day
num_problem_students = 0
for enrollment in enrollments:
    student = enrollment['account_key']
    if student not in unique_engagement_students and enrollment['join_date'] != enrollment['cancel_date']:
        print enrollment
        num_problem_students += 1

num_problem_students


# ## Tracking Down the Remaining Problems

# In[18]:

# Create a set of the account keys for all Udacity test accounts
udacity_test_accounts = set()
for enrollment in enrollments:
    if enrollment['is_udacity']:
        udacity_test_accounts.add(enrollment['account_key'])
len(udacity_test_accounts)


# In[19]:

# Given some data with an account_key field, removes any records corresponding to Udacity test accounts
def remove_udacity_accounts(data):
    non_udacity_data = []
    for data_point in data:
        if data_point['account_key'] not in udacity_test_accounts:
            non_udacity_data.append(data_point)
    return non_udacity_data


# In[20]:

# Remove Udacity test accounts from all three tables
non_udacity_enrollments = remove_udacity_accounts(enrollments)
non_udacity_engagement = remove_udacity_accounts(daily_engagement)
non_udacity_submissions = remove_udacity_accounts(project_submissions)

print len(non_udacity_enrollments)
print len(non_udacity_engagement)
print len(non_udacity_submissions)


# ## Refining the Question
# 
# #### How do numbers in the daily engagement table differ for students who pass the first project?

# In[21]:

# Create a dictionary mapping students who did not cancel within 7 days to their most recent
# join date
paid_students = {}
for enrollment in non_udacity_enrollments:
    # If the student is still enrolled or they took more than 7 days to cancel, we will consider them
    # a paid student
    if not enrollment['is_canceled'] or enrollment['days_to_cancel'] > 7:
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
        
        # Add this student to the dictionary if they are not already present, or if this enrollment date
        # is the most recent one we've seen so far
        if account_key not in paid_students or enrollment_date > paid_students[account_key]:
            paid_students[account_key] = enrollment_date

len(paid_students)


# ## Getting Data from First Week

# In[23]:

# Given some data with an account_key field, removes any records corresponding to accounts that canceled with
# seven days
def remove_free_trial_cancels(data):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data


# In[24]:

# Remove data from students who canceled within 7 days from all three tables
paid_enrollments = remove_free_trial_cancels(non_udacity_enrollments)
paid_engagement = remove_free_trial_cancels(non_udacity_engagement)
paid_submissions = remove_free_trial_cancels(non_udacity_submissions)

print len(paid_enrollments)
print len(paid_engagement)
print len(paid_submissions)


# In[25]:

# Create a binary version of the num_courses_visited field, equal to
# 1 if the student visited at least one course, and 0 otherwise.
for engagement_record in paid_engagement:
    if engagement_record['num_courses_visited'] > 0:
        engagement_record['has_visited'] = 1
    else:
        engagement_record['has_visited'] = 0


# In[26]:

# Takes a student's join date and the date of a specific engagement record,
# and returns True if that engagement record happened within one week
# of the student joining.
def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days >= 0 and time_delta.days < 7

# Collect all the engagement records that come in the first week of the student's most recent enrollment
paid_engagement_in_first_week = []
for engagement_record in paid_engagement:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_record_date = engagement_record['utc_date']
    
    if within_one_week(join_date, engagement_record_date):
        paid_engagement_in_first_week.append(engagement_record)

len(paid_engagement_in_first_week)


# ## Exploring Student Engagement

# In[27]:

from collections import defaultdict

# Create a dictionary of engagement grouped by the given key name.
# The keys are the fields from the data in the key_name column,
# and the values are lists of data points.
def group_data(data, key_name):
    grouped_data = defaultdict(list)
    for data_point in data:
        key = data_point[key_name]
        grouped_data[key].append(data_point)
    return grouped_data

engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')


# In[28]:

# Takes a dictionary of grouped data as output by group_data, as well as a field name to sum over,
# and returns a new dictionary with that field summed up and other fields discarded.
# The keys of the resulting dictionary will be the same as the keys of the original,
# and the values will be numbers containing the total value of the given field across all data points for the
# associated key.
def sum_grouped_items(grouped_data, field_name):
    summed_data = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
        summed_data[key] = total
    return summed_data

total_minutes_by_account = sum_grouped_items(engagement_by_account, 'total_minutes_visited')


# In[29]:

# Show matplotlib plots within the notebook rather than in a new window.
# Omit this line if not using IPython notebook
get_ipython().magic(u'pylab inline')

import matplotlib.pyplot as plt
import numpy as np

# Summarize the given data
def describe_data(data):
    print 'Mean:', np.mean(data)
    print 'Standard deviation:', np.std(data)
    print 'Minimum:', np.min(data)
    print 'Maximum:', np.max(data)
    plt.hist(data)
    
describe_data(total_minutes_by_account.values())


# ## Debugging Data Analysis Code

# In[30]:

# Find the student who spent the most minutes during the first week

student_with_max_minutes = None
max_minutes = 0

for student, total_minutes in total_minutes_by_account.items():
    if total_minutes > max_minutes:
        max_minutes = total_minutes
        student_with_max_minutes = student
        
max_minutes


# In[31]:

# Print out every engagement record for the student who spent the most minutes
for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] == student_with_max_minutes:
        print engagement_record


# ## Lessons Completed in First Week

# In[32]:

lessons_completed_by_account = sum_grouped_items(engagement_by_account, 'lessons_completed')
describe_data(lessons_completed_by_account.values())


# ## Number of Visits in First Week

# In[33]:

days_visited_by_account = sum_grouped_items(engagement_by_account, 'has_visited')
describe_data(days_visited_by_account.values())


# ## Splitting out Passing Students

# In[34]:

# Create a set of all account keys that eventually passed the subway project

subway_project_lesson_keys = ['746169184', '3176718735']

pass_subway_project = set()

for submission in paid_submissions:
    project = submission['lesson_key']
    rating = submission['assigned_rating']
    
    # These two project ids correspond to different versions of the subway project, and both
    # PASSED and DISTINCTION indicate that the student passed the project
    if (project in subway_project_lesson_keys) and (rating == 'PASSED' or rating == 'DISTINCTION'):
        pass_subway_project.add(submission['account_key'])
        
len(pass_subway_project)


# In[35]:

# Engagement data for students who eventually pass the subway project
passing_engagement = []
# Engagement data for students who do not eventually pass the subway project
non_passing_engagement = []

for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] in pass_subway_project:
        passing_engagement.append(engagement_record)
    else:
        non_passing_engagement.append(engagement_record)


# ## Comparing the Two Student Groups

# In[36]:

passing_engagement_by_account = group_data(passing_engagement, 'account_key')
non_passing_engagement_by_account = group_data(non_passing_engagement, 'account_key')


# In[37]:

print 'non-passing students:'
non_passing_minutes = sum_grouped_items(non_passing_engagement_by_account, 'total_minutes_visited')
describe_data(non_passing_minutes.values())

# Adding plt.show() after each plot will cause the two plots in this cell to display separately,
# rather than on top of each other
plt.show()

print 'passing students:'
passing_minutes = sum_grouped_items(passing_engagement_by_account, 'total_minutes_visited')
describe_data(passing_minutes.values())
plt.show()


# In[38]:

print 'non-passing students:'
non_passing_lessons = sum_grouped_items(non_passing_engagement_by_account, 'lessons_completed')
describe_data(non_passing_lessons.values())
plt.show()

print 'passing students:'
passing_lessons = sum_grouped_items(passing_engagement_by_account, 'lessons_completed')
describe_data(passing_lessons.values())
plt.show()


# In[39]:

print 'non-passing students:'
non_passing_visits = sum_grouped_items(non_passing_engagement_by_account, 'has_visited')
describe_data(non_passing_visits.values())
plt.show()

print 'passing students:'
passing_visits = sum_grouped_items(passing_engagement_by_account, 'has_visited')
describe_data(passing_visits.values())
plt.show()


# ## Improving Plots and Sharing Findings

# In[40]:

# Import seaborn for aesthetic improvements
import seaborn as sns

# Use bins=8 since there are exactly 8 possible values for this variable - 0 through 7 inclusive
plt.hist(non_passing_visits.values(), bins=8)
plt.xlabel('Number of days')
plt.title('Distribution of classroom visits in the first week for students who do not pass the subway project')


# In[41]:

plt.hist(passing_visits.values(), bins=8)
plt.xlabel('Number of days')
plt.title('Distribution of classroom visits in the first week for students who pass the subway project')


# In[ ]:




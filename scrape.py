import requests
import os
import argparse
from bs4 import BeautifulSoup
from pprint import pprint
import sqlite3
import datetime

positions_of_interest = ["FrontendEngineer", "FrontendDeveloper", "FullStack", "BackEnd", "Frontend"]
blacklist_words = ["Senior", "architect", "Principal"]


class DatabaseManager(object):
    def __init__(self, database_name="jobs.db"):
        self._database_name = database_name
        createTable = False
        if not os.path.exists(database_name):
            createTable = True
        self.connection = sqlite3.connect(database_name, detect_types=sqlite3.PARSE_COLNAMES | sqlite3.PARSE_DECLTYPES)
        self.connection.row_factory = sqlite3.Row
        if createTable:
            self._createTable()
    
    def __del__(self):
        self.connection.close()
    
    def _createTable(self):
        query = """ CREATE TABLE Jobs (Title text, Job_id text, DateAdded text)"""
        cur = self.connection.cursor()
        cur.execute(query)
    
    def _reset_database(self):
        self.connection.close()
        if os.path.exists(self._database_name):
            os.remove(self._database_name)
        self.connection = sqlite3.connect(self._database_name)
        self._createTable()

    def findJobWithID(self, id):
        """
            Returns a Row object
        """
        cur = self.connection.cursor()
        query = """ SELECT * from Jobs WHERE Job_id=?"""
        cur.execute(query,(id,))
        result = cur.fetchone()
        if result:
            return result
        else:
            return None
    
    def doesJobExist(self, id):
        if self.findJobWithID(id) is not None:
            return True
        else:
            return False
    
    def insertJob(self, job_name, job_id):
        query = """INSERT INTO Jobs VALUES (?,?,?)"""
        cur = self.connection.cursor()
        cur.execute(query, (job_name, job_id, datetime.datetime.now(datetime.timezone.utc),))
        print(cur.lastrowid)
        self.connection.commit()

    def getAllJobs(self):
        """
            Returns a list of Row objects
        """
        cur = self.connection.cursor()
        query = """Select * from Jobs"""
        cur.execute(query)
        result = cur.fetchmany()
        return result

class Job(object):
    def __init__(self, job_title, job_id):
        self.job_title = job_title
        self.job_id = job_id
    
    def __eq__(self, o):
        if type(o) != type(self):
            raise TypeError("Cannot compare {} with {}".format(type(o), type(self)))
        return o.job_id == self.job_id and o.job_title == self.job_title

def retrieveJobs(database):
    """
        returns (list[Job], list[Job] list[Job]) of list of jobs, list of bad titles, and list of jobs already applied to
    """
    jobSite = "https://jobs.lever.co/atlassian"
    page = requests.get(jobSite)
    soup = BeautifulSoup(page.content, "html.parser")
    
    newJobs = []
    badTitles = {}
    alreadyApplied = []
    
    job_elements = soup.find_all("div", class_="posting")
    for e in job_elements:
        posting_id = e.attrs['data-qa-posting-id']
        job_title = e.find("h5").text
        location_element = e.find("span", class_="sort-by-location")
        location = "None"
        if location_element:
            location = location_element.text
        if "UnitedStates".lower().replace(' ', '') not in location.lower().replace(' ', '') and location != "None":
            continue
        foundOne = False
        for position in positions_of_interest:
            if position.lower().replace(' ', '') in job_title.lower().replace(' ', ''):
                foundOne = True
                break
            else:
                continue
        
        if foundOne:
            for word in blacklist_words:
                if word.lower().replace(' ', '') in job_title.lower().replace(' ', ''):
                    foundOne = False
                    break

        if foundOne:
            if database.doesJobExist(posting_id):
                alreadyApplied.append(Job(job_title, posting_id))
            else:
                newJobs.append(Job(job_title, posting_id))
        else:
            if job_title not in badTitles:
                badTitles[job_title] = []
            badTitles[job_title].append(posting_id)
    
    return (newJobs, badTitles, alreadyApplied)


def discover_jobs(args):
    the_database = DatabaseManager()
    
    jobs, bad_titles, already_applied_jobs = retrieveJobs(the_database)
    
    print()
    print("Bad Titles:")
    pprint(bad_titles)
    
    while True:
        i=0
        if len(jobs) == 0:
            print("You've applied to all of the available jobs!")
            break
        for job in jobs:
            print("{:2d}: {} https://jobs.lever.co/atlassian/{}".format(i, job.job_title, job.job_id))
            i += 1
        user_input = input("Input value of job you applied for, or -1 to quit\n")
        print()
        try:
            parsedNum = int(user_input)
        except ValueError:
            print("Invalid input {}".format(user_input))
            continue
        if parsedNum == -1:
            break
        if parsedNum >= len(jobs) or parsedNum <= -2:
            print("Invalid input {}".format(user_input))
            continue
        the_job = jobs[parsedNum]
        print("Applied to {} {}".format(the_job.job_title, the_job.job_id))
        the_database.insertJob(the_job.job_title, the_job.job_id)
        del(jobs[parsedNum])
        

def add_to_database(args):
    pass

def test(args):
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    myDb = DatabaseManager(database_name="test.db")
    myDb.insertJob("myjob", "myJobId")
    res = myDb.findJobWithID("myJobId")
    a = datetime.datetime.fromisoformat(res["DateAdded"])
    print(a)
    print(myDb.getAllJobs())

def see_added_jobs(args):
    myDatabaseManager = DatabaseManager()
    rows = DatabaseManager.getAllJobs()
    for row in rows:
        print("{} {} {}".format(row["Title"], row["Job_id"], datetime.datetime.fromisoformat(row["DateAdded"])))

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.set_defaults(func=discover_jobs)
    subparsers = argument_parser.add_subparsers(help = "Commands that can be run")
    test_parser = subparsers.add_parser('test', help="the testing command")
    test_parser.set_defaults(func=test)
    job_discover_parser = subparsers.add_parser('discover', help="The discover command")
    job_discover_parser.set_defaults(func=discover_jobs)
    display_parser = subparsers.add_parser('display', help="The display command")
    display_parser.set_defaults(func=see_added_jobs)
    args = argument_parser.parse_args()    
    args.func(args)

    

# Atlassian Job Scraper

Have you ever started applying to Atlassian jobs only to come back the next day and realize you have no idea which one(s) you've applied to? This program is for you!

The Atlassian Job Scraper is a command-line utility that combs through the lever jobsite that Atlassian uses, and finds jobs that you haven't applied to yet.

Once you apply to a job, simply input its number, and this program will take it off of the list!

To edit the search terms and blacklist terms, simply edit the variables at the top of the file (no spaces)

![Demo Gif](./images/demo.gif)

## How to run

To run, first create the virtual environment and install the required modules

- Create the virtual environment: `python3 -m venv ./env `

- Activate the venv `source ./env/bin/activate`

- Install dependencies `pip3 install -r ./requirements.txt`

- Finally, you can run `python3 ./scrape.py`

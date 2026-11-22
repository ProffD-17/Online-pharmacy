# Online pharmacy
Online pharmacy is a imaginary pharmacy for patients to order thier prescriptions online.

## How to use
Deployed online using Railway at https://online-pharmacy-production.up.railway.app/

You can create your own account or use the example account below

Example account:
- Username: guest
- Email: guest@guest
- Firstname: guest
- Lastname: guest
- Password: guest

## Background
I get cream for my acne on repeat prescription every two weeks. There is a pharmacy 5 minutes walk from me but you cannot order the prescription there, instead I have to go to a different town to ask the recepionist at the doctors to order it for me and then pick it up at the pharmacy a few days later. This is a recurring inconvenience and I feel there should be a easier way to do this. The NHS do have an app but it doesnt work for my area. I have started to make an example app that lets patients order prescriptions online.

## Features
### Patients
- Make an account/login
- Change account information
- View different medicines
- View information on medicines
- Request medicine
- View your prescriptions
- Order prescriptions
- View your past orders
- View the status of your orders
### Pharmacists
- Everything above and:
- Mark orders as completed/uncompleted
- View order history for anyone
### Doctors
- Everything above and:
- Prescribe medicine to patients
- View and approve/deny medicine requests

## Database 
I used a database I found online for the information on medicines. I was originally using a database from databasesample.com but the information was inacurate so I switched to https://github.com/WSAyan/medicinedb. I also added my own tables and altered the original database slightly.
The original database can be found at https://github.com/WSAyan/medicinedb and the tables I added on are in added.sql

## Github repo tour
- /databases - The database and the sql files that made it along with the lisence for using the database
- /flask_session - stores information on who has logged in
- /static - only has styles.css which is some small CSS classes I used to tweak styling slightly
- /templates - all the HTML templates for the site
- README.md - what you are reading right now
- app.py - the main logic for the site
- requirements.txt - all the dependencies for the project. you only have to install these if you want to run the site locally

## Technologies
I used:
- HTML and jinja - displaying content on the frontend
- CSS(mainly bootstrap) - making things look professional and responsive
- Flask - connecting the frontend to the backend
- SQLite - store the users, prescriptions, medicines ect.
- Python - making the logic for things like validating input and executing commands to extract/input into the database

## Notes for reviwers
I included the password to change a users role in the terra submision.
This is an update on last weeks project. I asked on terra-help about deploying a new demo for this week and they said to just deploy this weeks but if you need the demo for week 4 let me know and I will figure out how to get that hosted online.

## Possible future improvements
- Add medicine shop to allow users to buy general medicines(Would have to maybe switch db because the one I'm using doesnt have prices)
- Contact section
- Users should be able to see if thier request is waiting to be reviewed, approved or denied on account page instead of just checking if the prescription exists
- Sort review requests page into waiting to be reviewed, approved, and denied
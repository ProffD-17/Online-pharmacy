# Online pharmacy
Online pharmacy is a template for creating a website for patients to order thier prescriptions online.

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
- Make an account/login
- Change account information
- View different medicines
- View information on medicines
- Order prescriptions
- Prescribe medicine to patients(Doctors only)

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

## Tasks for next week
- sort my prescriptions page into valid and invalid prescriptions
- make medicine shop to allow users to buy medicines
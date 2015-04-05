# Eventbrite: SimpleSearch
Eventbrite: SimpleSearch is a simple, concise interface for quickly searching through Eventbrite's event listing using 
the Eventbrite API.
 
## Quick Start
To start the project, navigate to the project directory and run `python manage.py runserver`. 

## Browsing: Categories
To use the SimpleSearch, a user should select 3 categories from the dropdown menus on the homepage of the application and 
click 'Search'. A user must select 3 categories in order for the search to take place. Additionally, each category should
be unique and should be a valid category. Automated validation has been implemented on both the front- and back-end of 
this application to ensure a user has an error-free experience.

## Browsing: All Events
In addition to browsing by category, a user may browse all events. To use this feature, a user should click "Browse all 
events" at the bottom of the homepage or the results page.

## UnitTests
UnitTests have been implemented for every possible scenario of acceptable and unacceptable input. To run this project's
 tests, navigate to the project directory and run: `python manage.py tests`
 
## Author
Alex C. Williams [https://github.com/csalexwilliams/](https://github.com/csalexwilliams/)

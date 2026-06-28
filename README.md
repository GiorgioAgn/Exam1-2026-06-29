# Free Walking Tour Siracusa

Web application developed for the Introduction to Web Applications exam.
The project uses Flask, Flask-Login, SQLite, HTML5, CSS3 and Bootstrap.

## Project Theme

The platform manages Free Walking Tours in the city of Syracuse.

For the design, I took inspiration from the midterm project I developed about an
outdoor-focused social media platform. I kept most of its design and color
palette. The application is responsive and can also be used on mobile devices
and tablets.

The website interface is written in English. Titles, descriptions and other
content entered manually by guides remain exactly as written. The selected tour
language must be one spoken by the guide who created it.

## Main Features

- Separate registration and login for guides and participants.
- A unique email address for each registered account.
- Guide languages limited to Italian, English, Spanish, Portuguese and German.
- Tours can only be published in a language spoken by the guide.
- Weekly schedule with no more than one time slot per day.
- Schedule overlap checks for both guides and participants.
- Tours are visible to everyone, including visitors who are not logged in.
- Filters by date, duration and language, with text search by title or theme.
- Homepage top 3 ranked by likes and comments.
- Bookings for 1 to 4 people, with availability checks for each date.
- First name and last name required for every additional guest.
- Bookings can be cancelled at least 24 hours before the tour starts.
- Participant profile with bookings and their current status.
- Guide profile with tours, bookings and expected participants for each date.
- Tours can only be edited when they have no active bookings.
- One post-tour report with actual attendance and a proof photo.
- Likes, comments, role badges and a tour author badge.

## Test Credentials

The submitted database contains 2 guides, 4 participants, 4 tours and several
bookings. Before submission, the passwords for these sample accounts must also
be added to this section, as required by the exam specifications.

| Role | Email | Password |
| --- | --- | --- |
| Guide | `giorgio@test.it` | `password1234` |
| Guide | `lucia@test.it` | `password1234` |
| Participant | `giorgio.participant@test.it` | `password1234` |
| Participant | `marco@test.it` | `password1234` |
| Participant | `marta@test.it` | `password1234` |
| Participant | `giovanni@test.it` | `password1234` |

Login requires an email address, a password and an account type.

## Running the Project

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the application using the included sample database:

```bash
python app.py
```

Open the following address in a browser:

```text
http://127.0.0.1:5000
```

To intentionally create a new empty database:

```bash
python db.py
```

During development, I used `python db.py` to delete all data stored in
`database.db` and recreate only the empty tables for testing purposes. Do not
run it before testing the submitted sample data.

## Registering an Account

1. Click `Register` in the top-right corner.
2. Enter a first name, last name, email address and password.
3. Select either `Participant` or `Guide`.
4. For a guide account, select at least one spoken language.
5. Click `Register` to complete the registration.

## Signing In

1. Click `Sign in` in the top-right corner.
2. Enter the email address and password used during registration.
3. Select the correct account type.
4. Click `Sign in`.

## Planning a Tour

1. Sign in with a `Guide` account.
2. Click `Plan` in the navigation bar, or open the profile menu and select
   `Plan tour`.
3. Enter all the required information, at least 4 stops and at least 5 photos.
4. Select one or more days and specify a start time for each one.
5. Click `Plan Tour`.

The backend validates the language, duration, capacity, photos, stops and any
schedule overlaps with the guide's other tours.

## Booking a Tour

1. Sign in with a `Participant` account.
2. Open `Tours` and select a tour, or choose one from the homepage.
3. Select an available date on the tour detail page.
4. Enter the total number of people, from 1 to 4.
5. Enter the first name and last name of every additional guest.
6. Click `Confirm booking`.

A visitor who is not logged in can view every tour, but is redirected to the
login page when attempting to make a booking.

## Cancelling a Booking

1. Sign in as a `Participant` and open `Profile`.
2. Find the relevant booking.
3. Click `Cancel`, which is available only when the tour starts in at least 24
   hours.

## Editing a Tour

Editing is available only when the tour has no bookings with the `booked`
status, including bookings for dates that have already passed.

1. Sign in as the guide who created the tour.
2. Open the tour from the homepage or `Tours` and click `Edit`; alternatively,
   open `Profile` and click `Edit` on the relevant tour.
3. Update the information and click `Save changes`.

If all bookings are cancelled, the tour becomes editable again.

## Submitting a Post-Tour Report

1. Sign in as a guide and open `Profile`.
2. Find a past date with at least one booking.
3. Enter the actual number of participants and upload a proof photo.
4. Click `Save report`.

Only one report can be submitted for each tour and date combination.

## Project Structure

```text
app.py                 Flask routes, validation and application rules
db.py                  SQLite connection and empty database initialization
schema.sql             Relational database schema
database.db            SQLite database with sample data
templates/             Jinja templates
static/assets/css/     Custom CSS styles
static/assets/img/     Static images
static/uploads/        Tour and report photos
requirements.txt       Python dependencies
```

## Deployment

Application deployed on PythonAnywhere:

[https://giorgioagn.pythonanywhere.com/](https://giorgioagn.pythonanywhere.com/)

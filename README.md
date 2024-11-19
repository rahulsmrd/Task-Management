# Task Management System
- Project manages the different tasks assosiated to user.
- It will take the task details and check for basic validations, and stores in database.

## Design Parameters
- Tech Stack -> Python, Django, REST framework.
- I followed Django’s app-based structure, dividing the code into separate apps for better maintainability and scalability.
- Added a folder Jobs to schedule the API calls periodically.
- The project adheres to the MVC pattern to clearly separate business logic from the user interface.
- I have used PostgreSQL as my Database for local machine. To make installation easy, I have changed it to SQLite.

## Further Scope
- Can integrate the APScheduler to make a remainder of the tasks due Dates.
- Can integrate to google calenders so that users can get a notification.

## Build Instructions for windows
- Clone the repository and open command prompt with path as folder location.
- Create and Activate virtual environment
  - Open the forlder.
  - ``` bash
     python -m venv venv
    ```
  - ``` bash
      venv\Script\activate
    ```
- Install requirements
  - ``` bash
      pip install -r requirements.txt
    ```
- Migrate the database
  - ``` bash
    python manage.py makemigrations
    ```
  - ``` bash
     python manage.py migrate
    ```
- Run Tests
  - ``` bash
     python manage.py test
    ```
- Run server
  - ``` bash
     python manage.py runserver
    ```
- Navigate to [http://127.0.0.1:8000/api/v1/docs/](http://127.0.0.1:8000/api/v1/docs/)

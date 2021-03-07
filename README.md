# SE-Project
Software Engineering (CSL2060) Project
### Installation:
Procedure:
- Clone the repo and launch code:

    ```bash
    git clone https://github.com/Sahil1479/SE-Project.git
    ```
- Navigate to the cloned repository.
    ```
    cd <project_directory_name>     #   ExpenseTracker
    ```
- Install `pipenv` for dependency management
    ```
    pip install pipenv
    ```
- Use pipenv to install other dependencies from `Pipfile`
    ```
    pipenv install --dev
    ```
- Activate the new virtual environment
    ```
    pipenv shell
    ```
- Make database migrations
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```
- Create a superuser
    ```
    python manage.py createsuperuser
    ```
- Run development server on localhost
    ```
    python manage.py runserver
    ```
    

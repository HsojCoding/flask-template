Startup:
    - Initialise Venv. Originally in python 3.13, should work for other versions. Check package requirements
    - Install packages: pip install -r r.txt
    - Change database URI in app.init
    - Intialise db migrations: flask db init
    - Run initial migrations: flask db migrate -m "Initial migration"
    - Apply changes: flask db upgrade
    - Create initial admin user using CLI command
    - Run app using flask run
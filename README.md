# CleanSMRs-Website

## Setup

First, clone the repository, either through the GitHub client or the Git CLI:

```
git clone https://github.com/SWE6202-Group-6/CleanSMRs-Website.git
```

Navigate into the directory and create your virtual environment:

```
cd CleanSMRs-Website
python -m venv .venv
```

Prefer one of `env`, `venv` or `.venv` for your virtual environment name as these are already added to the `.gitignore` 
file. If you choose another name, please make sure to add it to a line in `.gitignore` to ensure it is not committed to 
the repository - they can be quite large on disk.

Activate the virtual environment.

Windows:

```
source .venv/Scripts/activate
```

Mac/Linux:

```
source .venv/bin/activate
```

To install required packages for the first time, execute the following:

```
python -m pip install -r requirements.txt
```

Whenever you add a new dependency with Pip, make sure it also gets added to the `requirements.txt` file:

```
python -m pip freeze > requirements.txt
```

For any application settings, you'll need to make a copy of `.env.dist` as `.env` and add things such as database 
details, any secrets etc. to it:

```
cp .env.dist .env
```

You'll need to configure the database depending on whether you are using SQLite or MySQL:

```
DATABASE_URL=sqlite:///db.sqlite3
```

Or:

```
DATABASE_URL=mysql://{username}:{password}@localhost/{databasename}
```

You'll need to create a database on the server, first, if using MySQL, e.g.:

```
CREATE DATABASE ecommerce;
```

Then run the migrations:

```
python manage.py migrate
```

And create a superuser:

```
python manage.py createsuperuser
```

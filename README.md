# Django File Management System

[![Python Version](https://img.shields.io/badge/python-3.6-brightgreen.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-2.0-brightgreen.svg)](https://djangoproject.com)

In this Django app, publishers can create quizzes and subscribers can take quizzes according to their interested subjects; publishers can upload files and subscribers can subscribe to files related to their interests.


## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/AmberWangjie/Django-File-Manager.git
```

Run program under virtual environment:
```bash
source school/bin/activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Create the database:

```bash
python manage.py migrate
```

Finally, run the development server:

```bash
python manage.py runserver
```

The project will be available at **127.0.0.1:8000**.



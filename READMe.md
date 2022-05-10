# Django Rest Framework
## Running Steps

#### 1. Install Required Packages
`apt-get update`<br>
`apt-get install tesseract-ocr`<br>
`apt-get install poppler-utils`<br>
`apt-get install mysql-server`<br>
`apt-get install mysql-client`<br>
`apt-get install libmysqlclient-dev`<br>
`apt-get install libssl-dev`<br>

#### 2. Create a Virtual Environment
`virtualenv venv`<br>

#### 3. Activate Virtual Environment
`source venv/bin/activate`<br>

#### 4. Install the required Packages
`pip install -r requirements.txt`<br>

#### 5. Make Migrations of Default Tables
`python manage.py makemigrations`<br>

#### 6. Migrate Database
`python manage.py migrate`<br>

#### 7. Make Migrations of Custom Tables
`python manage.py makemigrations`<br>

#### 8. Migrate Database
`python manage.py migrate`<br>

#### 9. Create Super User
`python manage.py createsuperuser`<br>

#### 10. Run Application

`python manage.py runserver`<br>

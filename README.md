# Cookbook Django Application

Welcome to the Cookbook Django Application! This project is designed to help you manage your recipes and cooking adventures with ease.

## Installation

### Prerequisites
- Have the latest [node.js](https://nodejs.org/en) version
- Have the lastest [python](https://www.python.org/) version

### Clone the Repository

```bash
git clone https://github.com/aidanvancil/cookbook.git

python -m venv venv

source venv/bin/activate

cd cookbook

pip install -r requirements.txt

cd app/static_src

npm install

cd ../../.
```

### Database Configuration

Create a PostgreSQL database and update the DATABASES configuration in cookbook/settings.py with database credentials:

- Go to `https://developer.edamam.com/login` and create an account. Go to products then signup with the Edamam Recipe API. Note down the App Id and App Key for the future. 
- Load listed PG_Schema_Dump via `psql Cookbook < cookbook_dump`
- Create a .env file in root directory (should look similar to the following):

```
DB_NAME=Cookbook 
DB_USER=postgres
DB_PASSWORD=****
DB_HOST=localhost
DB_PORT=5432
API_APP_ID=****
API_APP_KEY=****
```

- Then, apply up two split terminals (with each in the activated virtual environment).
    - In one terminal run `python3 manage.py runserver`
    - In the other terminal run `python3 manage.py tailwind start`

Upon running the above `tailwind` command, you likely will get an error to simply install a dependency, but other than that you should be on your way.

To see the application then open up in any browser: `localhost:<portnumber_listed>` (likely port 8000)

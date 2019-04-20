# ET
Easy tutoring for schools

## Requirements and Setup
 - **Python** >= 3.6
 - **MySQL** or SQLite
 - **redis**

You might want to use `virtualenv` to set up a local development enviroment:
```bash
# install virtualenv
pip3 install virtualenv
# .. or pip or python -m pip or python3 -m pip

# create a virtual enviroment
virtualenv venv

. venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
Inside the `config` folder, you need the following files:
 - `dev.cfg` for your development specific configuration
 - `test.cfg` for your test specific configuration
 - `prod.cfg` for your production specific configuration
 - `secret.cfg` *(optional)* for secrets **NEVER INCLUDE THIS IN YOU COMMIT**

You can change the default location of those config files using the following enviroment variables:
 - `CONFIG` (default: `config/dev.cfg`)
 - `SECRET` (default: `config/secret.cfg`)

Additional enviroment variables:
 - `ENV` (default: `development`, can be either `development`, `test`, `production`)

### Run
Make sure to run `redis-server` and your database implementation, then run huey and the app:
```bash
# tasks:
huey_consumer run_huey.huey
# main application:
python run.py
```

The app might crash during first startup. You will need to add a `config` entry to your database. See the model for more information.

## License

   Copyright 2018-2019 Jonas Drotleff <jonas.drotleff@gmail.com>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

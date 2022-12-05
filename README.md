# Save your Homewizzard Energy data locally  

I wanted to save my data locally as a backup, this script parses the data from the weekly graph and stores the daily
data behind it in a local SQLite DB.  

## Running

In order to get the last 10 weeks, just run the following commands.

```bash
# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create the DB, tables and constrains
python data/create_tables.py

# Set credentials
export ENERGY_EMAIL=<email>
export ENERGY_PASSWORD=<password>

# Extract 1 week of data
python main.py --weeks=1
```

# Film Production Database

CSC312 Databases, Practical Assignment 2 (University of the Western Cape)

**Team:** The Equal SQLs

| Member | Student number |
|---|---|
| Tumelo Aphane (group leader) | 4351723 |
| Yanga Madosi | 4354243 |
| Caleb Meyer | 4359047 |
| Nhlamulo Maluleka | 4358074 |
| Tanya Hadebe | 4335167 |

A MySQL database for a local film production company. It stores films, actors,
crew members, crew roles, filming locations and production schedules, and a Python
script runs ten queries against it.

## What is in this repository

| Path | What it is |
|---|---|
| `main.py` | Python script that connects to MySQL and runs the ten queries |
| `sql/01_schema.sql` | Creates the database `film_production_db` and its nine tables |
| `sql/02_sample_data.sql` | Inserts the sample data (1 404 rows) |
| `sql/03_queries.sql` | The ten queries from section 6.0 of the report |
| `requirements.txt` | The one Python package the script needs |
| `data_prep/` | Scripts that prepared the sample data and drew the diagrams (not needed to run the project) |

## How to run it

You need Python 3.8 or later and MySQL 8.0.16 or later.

```
pip install -r requirements.txt
python main.py --setup
```

`--setup` runs `01_schema.sql` and `02_sample_data.sql` and then runs the ten queries.
The script asks for the MySQL host, port, user and password. Press Enter to accept the
defaults (`127.0.0.1`, `3306`, `root`). You can also give them on the command line:

```
python main.py --host 127.0.0.1 --port 3306 --user root --setup
```

After the database exists you can leave out `--setup`:

```
python main.py              # run all ten queries
python main.py --query 7    # run one query
python main.py --all-rows   # print every row instead of the first 15
```

The script ends with the line `10 of 10 queries executed successfully.`

You can also build the database without Python: open `sql/01_schema.sql` and then
`sql/02_sample_data.sql` in MySQL Workbench and run each one. Note that
`01_schema.sql` drops and recreates `film_production_db`.

## About the sample data

Films, genres, actors, crew members, cast lists and crew lists come from the
[IMDb non-commercial datasets](https://developer.imdb.com/non-commercial-datasets/)
(33 South African films). Information courtesy of IMDb (https://www.imdb.com),
used with permission for non-commercial purposes.

IMDb has no filming data. The locations, the production schedule and the crew email
addresses are fictional sample values and do not describe the real productions.

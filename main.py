# ------------------------------------------------------------------------------
# Team name:        The Equal SQLs
# Student numbers:  4351723, 4354243, 4359047, 4358074, 4335167
# File name:        main.py
# Module:           CSC312 Databases, Practical Assignment 2
#
# Connects to the Film Production Database in MySQL and runs the ten queries
# from section 6.0 of our report (they are stored in sql/03_queries.sql).
#
# How to run:
#   pip install -r requirements.txt
#   python main.py --setup        build the database first, then run the queries
#   python main.py                run the queries on a database that already exists
#   python main.py --query 7      run one query only
#
# The script asks for the MySQL host, port, user and password. They can also be
# given on the command line or in the environment variables DB_HOST, DB_PORT,
# DB_USER, DB_PASSWORD and DB_NAME.  Example:
#   python main.py --host 127.0.0.1 --port 3306 --user root --setup
# ------------------------------------------------------------------------------

import argparse
import getpass
import os
import re
import sys
from pathlib import Path

import mysql.connector
from mysql.connector import errorcode

SQL_DIR = Path(__file__).resolve().parent / "sql"
SCHEMA_FILE = SQL_DIR / "01_schema.sql"
DATA_FILE = SQL_DIR / "02_sample_data.sql"
QUERY_FILE = SQL_DIR / "03_queries.sql"


def ask(question, default):
    """Ask for a connection detail; pressing Enter keeps the default."""
    answer = input(f"{question} [{default}]: ").strip()
    return answer or default


def read_arguments():
    parser = argparse.ArgumentParser(description="Run the Film Production Database queries.")
    parser.add_argument("--host", default=os.environ.get("DB_HOST"))
    parser.add_argument("--port", default=os.environ.get("DB_PORT"))
    parser.add_argument("--user", default=os.environ.get("DB_USER"))
    parser.add_argument("--password", default=os.environ.get("DB_PASSWORD"))
    parser.add_argument("--database", default=os.environ.get("DB_NAME", "film_production_db"))
    parser.add_argument("--setup", action="store_true",
                        help="run 01_schema.sql and 02_sample_data.sql before the queries")
    parser.add_argument("--query", type=int, metavar="N", help="run only query number N")
    parser.add_argument("--all-rows", action="store_true",
                        help="print every row (default: the first 15 rows of each result)")
    args = parser.parse_args()

    # Anything not given on the command line or in the environment is asked for,
    # so the script also works when it is started with a "Run" button.
    interactive = sys.stdin is not None and sys.stdin.isatty()
    if args.host is None:
        args.host = ask("MySQL host", "127.0.0.1") if interactive else "127.0.0.1"
    if args.port is None:
        args.port = ask("MySQL port", "3306") if interactive else "3306"
    if args.user is None:
        args.user = ask("MySQL user", "root") if interactive else "root"
    try:
        args.port = int(args.port)
    except ValueError:
        sys.exit(f"The port must be a number, not '{args.port}'.")
    if args.password is None:
        args.password = getpass.getpass(f"MySQL password for {args.user}@{args.host} "
                                        "(typing is hidden): ")
    return args


def connect(args, use_database=True):
    """Open a connection. Explains the most common problems instead of a long traceback."""
    settings = {"host": args.host, "port": args.port, "user": args.user,
                "password": args.password, "charset": "utf8mb4"}
    if use_database:
        settings["database"] = args.database
    try:
        return mysql.connector.connect(**settings)
    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            sys.exit("Could not log in: the username or password is wrong.")
        if error.errno == errorcode.ER_BAD_DB_ERROR:
            sys.exit(f"The database '{args.database}' does not exist yet. "
                     "Run:  python main.py --setup")
        if error.errno in (2003, 2005):
            sys.exit(f"Could not reach a MySQL server at {args.host}:{args.port}. "
                     "Check that the server is running and that the host and port are right.")
        sys.exit(f"Could not connect to MySQL: {error}")


def split_statements(script):
    """Split a .sql script into single statements.
    Semicolons inside quoted text and inside -- comments are ignored."""
    statements, current, in_string, i = [], [], False, 0
    while i < len(script):
        ch = script[i]
        if in_string:
            current.append(ch)
            if ch == "\\":                                   # escaped character
                current.append(script[i + 1]); i += 1
            elif ch == "'":
                if script[i + 1:i + 2] == "'":               # '' is a quote inside the text
                    current.append("'"); i += 1
                else:
                    in_string = False
        elif ch == "'":
            in_string = True
            current.append(ch)
        elif script.startswith("--", i):                     # comment: skip to end of line
            end = script.find("\n", i)
            i = len(script) if end == -1 else end - 1
        elif ch == ";":
            statements.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1
    statements.append("".join(current).strip())
    return [s for s in statements if s]


def run_script(connection, path):
    """Run every statement in a .sql file (used by --setup)."""
    cursor = connection.cursor()
    statements = split_statements(path.read_text(encoding="utf-8"))
    for statement in statements:
        cursor.execute(statement)
    connection.commit()
    cursor.close()
    print(f"  {path.name}: {len(statements)} statements executed")


def load_queries(path):
    """Read 03_queries.sql. Each query starts with a line such as
    '-- Q3 [Medium] How often each location is used', followed by comment
    lines that describe it and then the SQL itself."""
    queries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        header = re.match(r"-- Q(\d+) \[(\w+)\] (.+)", line)
        if header:
            queries.append({"number": int(header.group(1)), "level": header.group(2),
                            "title": header.group(3), "notes": [], "sql": []})
        elif queries and line.startswith("--") and not queries[-1]["sql"]:
            queries[-1]["notes"].append(line[2:].strip())
        elif queries and line.strip():
            queries[-1]["sql"].append(line)
    for query in queries:
        query["sql"] = "\n".join(query["sql"]).rstrip().rstrip(";")
    return queries


def print_table(columns, rows, limit):
    """Print a result set as a text table."""
    shown = rows if limit is None else rows[:limit]
    cells = [["NULL" if value is None else str(value) for value in row] for row in shown]
    widths = [max([len(columns[i])] + [len(row[i]) for row in cells]) for i in range(len(columns))]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(line)
    print("| " + " | ".join(columns[i].ljust(widths[i]) for i in range(len(columns))) + " |")
    print(line)
    for row in cells:
        print("| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(columns))) + " |")
    print(line)
    if len(rows) > len(shown):
        print(f"... {len(rows) - len(shown)} more rows (use --all-rows to see them)")
    print(f"{len(rows)} row(s) returned")


def run_queries(connection, queries, limit):
    """Run each query and print its result. Returns the number that succeeded."""
    succeeded = 0
    cursor = connection.cursor()
    for query in queries:
        print("\n" + "=" * 78)
        print(f"Query {query['number']} [{query['level']}]: {query['title']}")
        for note in query["notes"]:
            print(f"  {note}")
        print("-" * 78)
        print(query["sql"])
        print("-" * 78)
        try:
            cursor.execute(query["sql"])
            rows = cursor.fetchall()
            print_table([column[0] for column in cursor.description], rows, limit)
            succeeded += 1
        except mysql.connector.Error as error:
            print(f"QUERY FAILED: {error}")
    cursor.close()
    return succeeded


def main():
    if hasattr(sys.stdout, "reconfigure"):       # names such as "François" print on any console
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for path in (SCHEMA_FILE, DATA_FILE, QUERY_FILE):
        if not path.exists():
            sys.exit(f"Cannot find {path}. Keep main.py in the same folder as the 'sql' "
                     "folder (download the whole repository, not only main.py).")
    args = read_arguments()

    if args.setup:
        print("Building the database ...")
        connection = connect(args, use_database=False)
        try:
            run_script(connection, SCHEMA_FILE)
            run_script(connection, DATA_FILE)
        except mysql.connector.Error as error:
            sys.exit(f"Setup failed: {error}")
        finally:
            connection.close()

    connection = connect(args)
    print(f"Connected to '{args.database}' on {args.host}:{args.port} as {args.user}")

    queries = load_queries(QUERY_FILE)
    if args.query is not None:
        queries = [q for q in queries if q["number"] == args.query]
        if not queries:
            sys.exit(f"There is no query number {args.query}.")

    succeeded = run_queries(connection, queries, None if args.all_rows else 15)
    connection.close()

    print("\n" + "=" * 78)
    print(f"{succeeded} of {len(queries)} queries executed successfully.")
    if succeeded != len(queries):
        sys.exit(1)


if __name__ == "__main__":
    main()

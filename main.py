import paramiko
import datetime
import psycopg2
import os

try:  # Load environment variables in testing from .env
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass


def load_credentials():
    # Check to make sure database information is defined in the environment variables
    if not (
        os.getenv("db_user")
        and os.getenv("db_password")
        and os.getenv("database")
        and os.getenv("db_host")
        and os.getenv("machine")
        and os.getenv("machine_user")
        and os.getenv("machine_password")
    ):
        print("Database or machine credentials are not set in environment variables.")
        print(
            "Make sure all of the variables are set: db_user, db_password, database, db_host, db_port (optional), machine, machine_user, machine_password"
        )
        import sys  # We don't use sys anywhere else, so import it only when we need it, which should be never.

        # Stop execution due to no credentials
        sys.exit()

    # Save credentials into a dictionary for use later
    env = {
        "user": os.getenv("db_user"),
        "password": os.getenv("db_password"),
        "database": os.getenv("database"),
        "host": os.getenv("db_host"),
        "port": int(os.environ.get("db_port", 5432)),
        "machine": os.getenv("machine"),
        "machine_user": os.getenv("machine_user"),
        "machine_pass": os.getenv("machine_password"),
    }

    return env


env = load_credentials()


def ssh_connect(
    machine=env["machine"], username=env["machine_user"], password=env["machine_pass"],
):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=machine, username=username, password=password)
    return ssh


ssh = ssh_connect()

stdin, stdout, stderr = ssh.exec_command("tail -f /var/log/cmh/LuaUPnP.log")

for line in stdout:
    data = line.split()
    if (
        data[0] == "06"
        and data[3] == "Device_Variable::m_szValue_set"
        and data[5] == "18"
        and data[9] == "\x1b[35;1mCurrentTemperature\x1b[0m"
    ):
        print(data[9], ":", data[13])

        current_temp = data[13]
        date = data[1]
        time = data[2]

        # Establish database connection and do INSERT
        conn = None
        try:
            conn = psycopg2.connect(
                user=env["user"],
                password=env["password"],
                host=env["host"],
                port=env["port"],
                database=env["database"],
            )

            cur = conn.cursor()

            time = datetime.datetime.strptime(
                f"{data[1]} {data[2]}", "%m/%d/%y %H:%M:%S.%f"
            )
            tank = "House"
            sensor = "temperature"
            value = current_temp

            query = f"INSERT INTO aquariums (time, tank, sensor, value) VALUES (%s, %s, %s, %s);"
            query_values = (time, tank, sensor, value)

            cur.execute(query, query_values)
            conn.commit()

            print(query_values)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if conn is not None:
                cur.close()
                conn.close()


ssh.close()

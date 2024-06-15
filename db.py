import psycopg2

CONN = None

def create_or_get_connection():
    global CONN
    if CONN is None or CONN.closed:
        CONN = psycopg2.connect(
            user='postgres',
            password='Reza2001',
            host='localhost',
            port='5432',
            dbname='finbotincome'
        )

    CONN.autocommit = True
    return CONN

def run_sql(query):
    con = create_or_get_connection()
    cur =  con.cursor()
    cur.execute(query)

    return cur
    



def create_table(name, query):
    command = f"""CREATE TABLE IF NOT EXISTS {name} (
        {query}
    );"""

    return command

commands = {
    'user_table' : """
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL,
        user_name VARCHAR(255),
        full_name VARCHAR(255),
        invitation_link VARCHAR(255),
        referral_code VARCHAR(255),
        score INTEGER DEFAULT 0,
        access_level VARCHAR(20) CHECK (access_level IN ('Allowed', 'Unallowable'))""",

    'invoice_table' : """
        id SERIAL PRIMARY KEY,
        amount DOUBLE PRECISION NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expired_at TIMESTAMP,
        status VARCHAR(20) CHECK (status IN ('Active', 'Paid', 'Expired', 'Failed')),
        authority VARCHAR(36),
        user_id BIGINT REFERENCES user_table(id)""",

    'ticket' : """
        id SERIAL PRIMARY KEY,
        title VARCHAR(50),
        text VARCHAR(500) NOT NULL""",

    'support_account_table' : """
        id SERIAL PRIMARY KEY,
        platform VARCHAR(20) CHECK (platform IN ('Telegram', 'Gmail', 'Phone')),
        value VARCHAR(255) NOT NULL""",

    'chanell_links_table' : """
        id SERIAL PRIMARY KEY,
        title VARCHAR(50),
        link VARCHAR(500) NOT NULL"""
}

class DBQuery:
    def fetchAllSQL(sql_query):
        con = create_or_get_connection()
        cursor = con.cursor()

        cursor.execute(sql_query)
        rows = cursor.fetchall()

        return rows
    


#for key, value in commands.items():
#    result = run_sql(create_table(name=key, query=value))
#    if result is not None:
#        print(f"Success, {key} created.")
#    else:
#        print(f"Error, {key} not created.")
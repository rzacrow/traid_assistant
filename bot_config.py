import db as psql

def fetch_sql(query: str):
    result = psql.DBQuery.fetchAllSQL(query)
    return result

#Unit: IR
ACCOUNT_VIP_AMOUNT = fetch_sql("SELECT * FROM telegram_vipaccountamount;")[0][1]

#Bot Token
bot_conf = fetch_sql("SELECT * FROM telegram_botconfig;")[0]
TOKEN = bot_conf[3]

BOT_NAME = bot_conf[1]

BOT_USERNAME = bot_conf[2]



#Get all of links from DB
sql_query = "SELECT * FROM telegram_telegramchannels;"
result = psql.DBQuery.fetchAllSQL(sql_query)
LINKS = dict()

for index in range(len(result)):
    LINKS[result[index][1]] = result[index][2]


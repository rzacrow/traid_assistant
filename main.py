from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, helpers
import db as psql
import logging, datetime, json
from payments import zarinpal


#import teleton
#from unidecode import unidecode

#Token
TOKEN = "7111711383:AAH5xL-FunByrIZvV_HyWr2y7d5e1UqKELo"

#Important variables
ADMINS = ["5538826229"]

sql_query = "SELECT * FROM telegram_vipaccountamount;"
result = psql.DBQuery.fetchAllSQL(sql_query)
amount = result[0][1]

ACCOUNT_VIP_AMOUNT = int(amount) #Unit: IR

#Get support telegram from DB
SUPPORT_EMAILS = list()
SUPPORT_TELEGRAM_IDS = list()


#Get all of links from DB
sql_query = "SELECT * FROM telegram_telegramchannels;"
result = psql.DBQuery.fetchAllSQL(sql_query)
LINKS = dict()

for index in range(len(result)):
    LINKS[index[1]] = index[2]




#Main keyboard
KEYBOARD = [
    [InlineKeyboardButton("👤 مشاهده پروفایل", callback_data="profile")],
    [InlineKeyboardButton("🪙 ایردراپ", callback_data="airdrop")],
    [InlineKeyboardButton("📈 سیگنال", callback_data="signal")],
    [InlineKeyboardButton("🤖 ربات معامله گر", callback_data="trading_bot")],
    [InlineKeyboardButton("💰 کسب درآمد", callback_data="earn_money")],
    [InlineKeyboardButton("💎 ارزهای پر پتانسیل", callback_data="potential_currencies")],
    [InlineKeyboardButton("💵 بونوس", url=LINKS['Bonus'])],
    [InlineKeyboardButton("🧑🏻‍🏫 آموزش", callback_data="eduction")],
    [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
]

#Log configuration
logging.basicConfig(format='%(levelname)s - (%(asctime)s) - %(message)s - (Line: %(lineno)d) - [%(filename)s]',
                    datefmt='%H:%M:%S',
                    encoding='utf-8',
                    level=logging.WARNING)

logger = logging.getLogger(__name__)


async def error_message(context, update, query=None):
    if query:
        await query.edit_message_text(
            text="مشکلی در درخواست شما به وجود آمد لطفا مجددا امتحان کنید!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                ]
            )
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="مشکلی در درخواست شما به وجود آمد لطفا مجددا امتحان کنید!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                ]
            )
        )

def check_membership_access_level(user_id):
    """
    Checking a user's membership and access level
    """
    query = "SELECT user_name,access_level FROM telegram_telegramprofile WHERE telegram_id=%s;" % (user_id)
    user = psql.DBQuery.fetchAllSQL(sql_query=query)

    if user:
        KEYBOARD[0] = [InlineKeyboardButton("👤 مشاهده پروفایل", callback_data="profile")]
        if user[0][1] == "Allowed":
            return True
        else:
            return False
    else:
        KEYBOARD[0] = [InlineKeyboardButton("👤 ثبت نام", callback_data="signup")]
        return False




def check_member_ship(user_id):
    """
    Checking a user's membership
    """
    query = "SELECT user_name,access_level FROM telegram_telegramprofile WHERE telegram_id=%s;" % (user_id)
    user = psql.DBQuery.fetchAllSQL(sql_query=query)

    if user:
        return True
    return False

CHECK_THIS_OUT = "check-this-out"




async def start(update: Update, context: CallbackContext):
    """
    -> start command bot
    """
    logger.warning("user %s started bot", update.effective_user.id) 
    
    #check if user joined via referral code
    print('text:', update.message.text)   # /start something
    print('args:', context.args)          # ['something']

    print(len(context.args))

    if len(context.args) >= 1:
        referral = context.args[0]
        print(referral)
        if referral.isnumeric():
            context.user_data['referral'] = referral
            print(context.user_data['referral'])


    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "🔰 با تشکر از انتخاب شما\n\n لطفا یکی از خدمات زیر را انتخاب فرمایید" ,
        reply_markup=InlineKeyboardMarkup(
            KEYBOARD
        )
    )

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.args)
    await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "🔰 با تشکر از انتخاب شما\n\n لطفا یکی از خدمات زیر را انتخاب فرمایید" ,
        )

async def get_data():
    """
    ->   This function from Teleton module checks whether the transaction number
         entered by the user is acceptable or not
    """
    #client = teleton.client
    #async with client:
    #    main = await teleton.main()
    #    return main




async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


    cm = check_membership_access_level(update.effective_user.id)

    if query.data == "signup":
        await query.edit_message_text(
            text="لطفا جهت ایجاد حساب از لینک زیر عضویت ویژه تهیه کنید، سپس با وارد کردن شماره تراکنش، بصورت آنی عضویت شما انجام خواهد شد.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("💰 خرید اشتراک ویژه", callback_data="payment")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                ]
            )
        )


    elif query.data == "back":
        user = update.effective_user
        check_membership_access_level(user.id)
        await query.delete_message(
        
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "لطفا یکی از گزینه های زیر را انتخاب کنید",
            reply_markup=InlineKeyboardMarkup(
                KEYBOARD
            )
        )


    elif query.data == "checkout":

        logger.warning("user %s on stage checkout.", update.effective_user.id)
        check_paid = ""
        if check_paid:
            check_membership_access_level(user.id)

            await query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="پرداخت شما موفقیت آمیز بود، اکنون میتوانید از ربات استفاده کنید",
                reply_markup=InlineKeyboardMarkup(
                    KEYBOARD
                )
            )



            logger.warning("user %s has entered a code, and change status to Allowed successfully!", user.id)



    elif query.data == "payment":
        user = update.effective_user

        logger.warning("user %s on stage payment", user.id)

        cm_and_type = check_membership_access_level(user.id)
        check_member = check_member_ship(user.id)

        #if user is not registered
        if (not cm_and_type) and (not check_member):
            invitation_link = f"https://t.me/traidassistant_bot?start={user.id}"
            sql_query = f"INSERT INTO telegram_telegramprofile (telegram_id,user_name,full_name,access_level,invitation_link,score) VALUES ('{user.id}','{user.username}','{user.full_name}','Unallowable','{invitation_link}',0);"
            psql.run_sql(sql_query)
            logger.warning("user %s registered.", user.id)

        request = zarinpal.send_request(amount=ACCOUNT_VIP_AMOUNT)


        #try:
        if request.status_code == 200:
            request = request.json()
    

        #If is request is not valid
        if request['data']['code'] != 100:
            await error_message(context=context, update=update, query=query)
            return
        
        authority = request['data']['authority']
        link = zarinpal.make_link(authority=authority)

        time_now = datetime.datetime.now()

        #create invoice 
        sql_query = f"INSERT INTO payment_invoice (amount,status,authority,telegram_profile_id,created_at) VALUES ('{ACCOUNT_VIP_AMOUNT}','Active','{authority}',(SELECT id FROM telegram_telegramprofile WHERE telegram_id='{user.id}'),'{time_now}');"
        psql.run_sql(sql_query)

        

        await query.edit_message_text(
            text=f"فاکتور شما ایجاد گردید. مبلغ قابل پرداخت:\n\n {ACCOUNT_VIP_AMOUNT} تومان.\n\n جهت رفتن به درگاه پرداخت روی دکمه زیر کلیک نمایید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("💰 پرداخت", url=link)],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                ]
            )
        )

        #except:
         #   await error_message(context=context, update=update, query=query)
        
        

        



    elif query.data == "profile":
        if not cm:
            await query.edit_message_text(
                text="برای استفاده از ربات، اشتراک ویژه تهیه نمایید.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("💰 خرید اشتراک ویژه", callback_data="payment")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )
        else:
            user = update.effective_user

            sql_query = f"SELECT * FROM telegram_telegramprofile WHERE telegram_id={user.id};"
            result = psql.DBQuery.fetchAllSQL(sql_query)

            
            sql_query = f"SELECT * FROM payment_invoice WHERE telegram_profile_id=(SELECT id FROM telegram_telegramprofile WHERE telegram_id='{user.id}');"
            payment_detail = psql.DBQuery.fetchAllSQL(sql_query)



            payment_date = payment_detail[0][2]
            result = result[0]
            access_level = ""

            if result[7] == "Allowed":
                access_level = "عضویت ویژه"
            else:
                access_level = "عضویت معمولی"

            await query.edit_message_text(
                text=f"👤 نام کاربری: {result[2]}\n\n🏆 امتیاز: {result[6]}\n\n🔗 لینک دعوت شما:\n <pre>{result[5]}</pre>\n\n📌 نوع عضویت: {access_level}\n\n ⏱ عضو شده در: {payment_date.strftime('%Y/%m/%d')}\n\n ⌛️ اعتبار حساب تا: ---\n\n<b>Traid assistant</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                ),
                parse_mode="HTML"
            )
            print("By")
            try:
                print("Hi")
                referral = context.user_data['referral']
                print(referral)
            except:
                pass
            else:
                sql_query = f"SELECT referral_code FROM telegram_telegramprofile WHERE telegram_id='{user.id}';"
                result = psql.DBQuery.fetchAllSQL(sql_query)

                print(result[0][0])

                #referral code
                if result[0][0] == None:
                    sql_query = f"UPDATE telegram_telegramprofile SET referral_code='{referral}' WHERE telegram_id='{user.id}';"
                    psql.run_sql(sql_query)
                    sql_query = f"SELECT score,user_name FROM telegram_telegramprofile WHERE telegram_id='{referral}';"
                    result = psql.DBQuery.fetchAllSQL(sql_query)
                    score = int(result[0][0])
                    score += 5
                    username = result[0][1]
                    print("Score: ", score)
                    sql_query = f"UPDATE telegram_telegramprofile SET score='{score}' WHERE telegram_id='{referral}';"
                    psql.run_sql(sql_query)

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"شما از طریق کاربر {username} به ربات دعوت شده اید. این کد تایید گردید و تعداد 5 امتیاز به حساب ایشان اضافه گردید.\n\n شما هم می توانید با دعوت دوستانتان از طریق این کد امتیاز خود را افزایش دهید و کسب درآمد کنید"
                    )

                    await context.bot.send_message(
                        chat_id=referral,
                        text="پیام ربات:\n\nتعداد 5 امتیازات به مجموع امتیاز شما اضافه گردید"
                    )

    elif not cm:
        await query.edit_message_text(
            text="جهت استفاده از ربات، لطفا از گزینه ثبت نام و یا از قسمت پروفایل سپس شارژ حساب، اشتراک تهیه کنید",
            reply_markup=InlineKeyboardMarkup(
                KEYBOARD
            )
        )

    else:
        if query.data == "signal":
            await query.edit_message_text(
                text="یکی از خدمات زیر را انتخاب کنید",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📈 سیگنال فارکس", url=LINKS['Forex'])],
                        [InlineKeyboardButton("📉 سیگنال کریپتو", url=LINKS['Crypto'])],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )
        elif query.data == "trading_bot":
            await query.edit_message_text(
                text="برای دریافت فایل ربات ها، گزینه مشاهده اسکریپت ها را انتخاب نمایید",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📥 مشاهده اسکریپت ها ", url=LINKS['TraderBot'])],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )
        elif query.data == "earn_money":
            await query.edit_message_text(
                text="یکی از خدمات زیر را انتخاب کنید",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔗 ثبت نام بروکر", url=LINKS['Broker'])],
                        [InlineKeyboardButton("📮 دریافت کد معرف شما", callback_data="referral")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )

        elif query.data == "referral":
            user = update.effective_user
            sql_query = f"SELECT invitation_link FROM telegram_telegramprofile WHERE telegram_id={user.id};"
            result = psql.DBQuery.fetchAllSQL(sql_query)
            referral_link = result[0][0]
            await query.edit_message_text(
                text=f"با دعوت دوستان خود از طریق لینک زیر به ربات، با ثبت نام آنها شما <b>5</b> امتیاز دریافت خواهید کرد. با رسیدن به <b>30</b> امتیاز، یک اشتراک ویژه رایگان به شما اعطا خواهد شد\nکد معرف شما:\n <pre>{referral_link}</pre>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                ),
                parse_mode="HTML"
            )




if __name__ == "__main__":
    logger.warning("starting bot ...")

    application = ApplicationBuilder().token(token=TOKEN).build()
    application.add_handler(CommandHandler('start', start, has_args=True))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('checkout', checkout))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

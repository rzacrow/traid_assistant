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
ACCOUNT_VIP_AMOUNT = 5000

#Get support accounts from DB
SUPPORT_EMAILS = list()
SUPPORT_TELEGRAM_IDS = list()


#Get all of links from DB
sql_query = "SELECT * FROM chanell_links_table;"
result = psql.DBQuery.fetchAllSQL(sql_query)
BONUS_LINK = "https://t.me/traid_assistant"
BROKER_LINK = "https://t.me/traid_assistant"


for obj in result:
    if obj[1] == "broker":
        BROKER_LINK = obj[2]
        continue
    if obj[1] == "bonus":
        BONUS_LINK = obj[2]
        continue



#Main keyboard
KEYBOARD = [
    [InlineKeyboardButton("👤 مشاهده پروفایل", callback_data="profile")],
    [InlineKeyboardButton("🪙 ایردراپ", callback_data="airdrop")],
    [InlineKeyboardButton("📈 سیگنال", callback_data="signal")],
    [InlineKeyboardButton("🤖 ربات معامله گر", callback_data="trading_bot")],
    [InlineKeyboardButton("💰 کسب درآمد", callback_data="earn_money")],
    [InlineKeyboardButton("💎 ارزهای پر پتانسیل", callback_data="potential_currencies")],
    [InlineKeyboardButton("💵 بونوس", url=BONUS_LINK)],
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
    query = "SELECT user_name,access_level FROM user_table WHERE telegram_id=%s;" % (user_id)
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
    query = "SELECT user_name,access_level FROM user_table WHERE telegram_id=%s;" % (user_id)
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
    if len(context.args) >= 1:
        referral = context.args[0]
        if referral.isnumeric():
            context.user_data['referral'] = referral


    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "🔰 با تشکر از انتخاب شما\n\n لطفا یکی از خدمات زیر را انتخاب فرمایید" ,
        reply_markup=InlineKeyboardMarkup(
            KEYBOARD
        )
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
            sql_query = f"UPDATE user_table SET access_level='Allowed' WHERE telegram_id='{user.id}';"
            psql.run_sql(sql_query)

            create_invoice_query = f"INSERT INTO invoice_table (amount,status,user_id) VALUES (0,'Paid',(SELECT id FROM user_table WHERE telegram_id='{user.id}'));"
            creaet_payment_query = f"INSERT INTO payments_table (payment_date,reference_id,invoice_id) VALUES ('{datetime.datetime.now()}','',(SELECT id FROM invoice_table WHERE id=(SELECT id FROM user_table WHERE telegram_id='{user.id}')));"
            
            psql.run_sql(create_invoice_query)
            psql.run_sql(creaet_payment_query)
            user = update.effective_user
            check_membership_access_level(user.id)

            await query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="پرداخت شما موفقیت آمیز بود، اکنون میتوانید از ربات استفاده کنید",
                reply_markup=InlineKeyboardMarkup(
                    KEYBOARD
                )
            )

            try:
                referral = context.user_data['referral']
            except:
                pass
            else:
                sql_query = f"SELECT referral_code FROM user_table WHERE telegram_id='{user.id}';"
                result = psql.DBQuery.fetchAllSQL(sql_query)

                print(result[0])

                #referral code
                if len(result[0]) < 1:
                    sql_query = f"UPDATE user_table SET referral_code='{referral}' WHERE telegram_id='{user.id}';"
                    psql.run_sql(sql_query)
                    sql_query = f"SELECT score,user_name FROM user_table WHERE telegram_id='{referral}';"
                    result = psql.DBQuery.fetchAllSQL(sql_query)
                    score = int(result[0][0])
                    score += 5
                    username = result[0][1]
                    print("Score: ", score)
                    sql_query = f"UPDATE user_table SET score='{score}' WHERE telegram_id='{referral}';"
                    psql.run_sql(sql_query)

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"شما از طریق کاربر {username} به ربات دعوت شده اید. این کد تایید گردید و تعداد 5 امتیاز به حساب ایشان اضافه گردید.\n\n شما هم می توانید با دعوت دوستانتان از طریق این کد امتیاز خود را افزایش دهید و کسب درآمد کنید"
                    )

                    await context.bot.send_message(
                        chat_id=referral,
                        text="پیام ربات:\n\nتعداد 5 امتیازات به مجموع امتیاز شما اضافه گردید"
                    )


            logger.warning("user %s has entered a code, and change status to Allowed successfully!", user.id)



    elif query.data == "payment":
        user = update.effective_user

        logger.warning("user %s on stage payment", user.id)

        cm_and_type = check_membership_access_level(user.id)
        check_member = check_member_ship(user.id)

        #if user is not registered
        if (not cm_and_type) and (not check_member):
            invitation_link = f"https://t.me/traidassistant_bot?referral={user.id}"
            sql_query = f"INSERT INTO user_table (telegram_id,user_name,full_name,access_level,invitation_link) VALUES ('{user.id}','{user.username}','{user.full_name}','Unallowable','{invitation_link}');"
            psql.run_sql(sql_query)
            logger.warning("user %s registered.", user.id)

        request = zarinpal.send_request(amount=ACCOUNT_VIP_AMOUNT)


        try:
            if request.status_code == 200:
                request = request.json()
        

            #If is request is not valid
            if request['data']['code'] != 100:
                await error_message(context=context, update=update, query=query)
                return
            
            link = zarinpal.make_link(authority=request['data']['authority'])

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"فاکتور شما ایجاد گردید. مبلغ قابل پرداخت {ACCOUNT_VIP_AMOUNT}.\n\n جهت رفتن به درگاه پرداخت روی دکمه زیر کلیک نمایید.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("💰 پرداخت", url=link)],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )

        except:
            await error_message(context=context, update=update, query=query)
        
        

        



    elif query.data == "profile":
        if not cm:
            await query.edit_message_text(
                text="لطفا حساب خود را شارژ نمایید.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("💰 خرید عضویت ویژه از درگاه پرداخت", callback_data="payment")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )
        else:
            user = update.effective_user

            sql_query = f"SELECT * FROM user_table WHERE telegram_id={user.id};"
            result = psql.DBQuery.fetchAllSQL(sql_query)

            
            sql_query = f"SELECT payment_date FROM payments_table WHERE invoice_id=(SELECT id FROM invoice_table WHERE user_id=(SELECT id FROM user_table WHERE telegram_id='{user.id}'));"
            payment_date = psql.DBQuery.fetchAllSQL(sql_query)

            payment_date = payment_date[0][0]
            result = result[0]
            access_level = ""
            if result[7] == "Allowed":
                access_level = "عضویت ویژه"
            else:
                access_level = "عضویت معمولی"

            await query.edit_message_text(
                text=f"👤 نام کاربری: {result[2]}\n\n🏆 امتیاز: {result[6]}\n\n🔗 لینک دعوت شما:\n <pre>{result[4]}</pre>\n\n📌 نوع عضویت: {access_level}\n\n ⏱ عضو شده در: {payment_date.strftime('%Y/%m/%d')}\n\n ⌛️ اعتبار حساب تا: ---\n\n<b>Traid assistant</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                ),
                parse_mode="HTML"
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
                        [InlineKeyboardButton("📈 سیگنال فارکس", url="https://t.me/bookrpchanell")],
                        [InlineKeyboardButton("📉 سیگنال کریپتو", url="https://t.me/bookrpchanell")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )
        elif query.data == "trading_bot":
            await query.edit_message_text(
                text="برای دریافت فایل ربات ها، گزینه مشاهده اسکریپت ها را انتخاب نمایید",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📥 مشاهده اسکریپت ها ", url="https://t.me/bookrpchanell")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )
        elif query.data == "earn_money":
            await query.edit_message_text(
                text="یکی از خدمات زیر را انتخاب کنید",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔗 ثبت نام بروکر", url=BROKER_LINK)],
                        [InlineKeyboardButton("📮 دریافت کد معرف شما", callback_data="referral")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )

        elif query.data == "referral":
            user = update.effective_user
            sql_query = f"SELECT invitation_link FROM user_table WHERE telegram_id={user.id};"
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
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

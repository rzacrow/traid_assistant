from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, helpers
import db as psql
import logging, datetime, json
from payments import zarinpal
import bot_config
from datetime import timedelta



#Main keyboard
KEYBOARD = [
    [InlineKeyboardButton("👤 مشاهده پروفایل", callback_data="profile")],
    [InlineKeyboardButton("🪙 ایردراپ", callback_data="airdrop")],
    [InlineKeyboardButton("📈 سیگنال", callback_data="signal")],
    [InlineKeyboardButton("🤖 ربات معامله گر", callback_data="trading_bot")],
    [InlineKeyboardButton("💰 کسب درآمد", callback_data="earn_money")],
    [InlineKeyboardButton("💎 ارزهای پر پتانسیل", callback_data="potential_currencies")],
    [InlineKeyboardButton("💵 بونوس", url=bot_config.LINKS['Bonus'])],
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
            
            #check_expired_account
            sql_query = f"SELECT * FROM payment_invoice WHERE telegram_profile_id=(SELECT id FROM telegram_telegramprofile WHERE telegram_id='{user_id}');"
            payment_detail = psql.DBQuery.fetchAllSQL(sql_query)

            expired_date = payment_detail[0][3]

            
            if expired_date:
                time_now = datetime.datetime.now()
                try:
                    if expired_date < time_now:
                        sql_query = f"UPDATE telegram_telegramprofile SET access_level='Unallowable' WHERE telegram_id='{user.id}';"
                        result = psql.run_sql(sql_query)
                        return False
                except:
                    return True    
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

    user_id = update.effective_user.id
    check_membership_access_level(user_id=user_id)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "🔰 با تشکر از انتخاب شما\n\n لطفا یکی از خدمات زیر را انتخاب فرمایید" ,
        reply_markup=InlineKeyboardMarkup(
            KEYBOARD
        )
    )


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

        try:
            context.user_data["user_ticket"][0] = False
        except:
            pass

    elif query.data == "payment":
        user = update.effective_user

        logger.warning("user %s on stage payment", user.id)

        cm_and_type = check_membership_access_level(user.id)
        check_member = check_member_ship(user.id)

        #if user is not registered
        if (not cm_and_type) and (not check_member):
            invitation_link = f"https://t.me/{bot_config.BOT_USERNAME}?start={user.id}"
            sql_query = f"INSERT INTO telegram_telegramprofile (telegram_id,user_name,full_name,access_level,invitation_link,score) VALUES ('{user.id}','{user.username}','{user.full_name}','Unallowable','{invitation_link}',0);"
            psql.run_sql(sql_query)
            logger.warning("user %s registered.", user.id)

        request = zarinpal.send_request(amount=bot_config.ACCOUNT_VIP_AMOUNT)


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


        

        msg_id = await query.edit_message_text(
            text=f"فاکتور شما ایجاد گردید. مبلغ قابل پرداخت:\n\n {bot_config.ACCOUNT_VIP_AMOUNT} ریال.\n\n جهت رفتن به درگاه پرداخت روی دکمه زیر کلیک نمایید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("💰 پرداخت", url=link,)],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                ]
            )
        )


        
        #create invoice 
        sql_query = f"INSERT INTO payment_invoice (amount,status,authority,telegram_profile_id,created_at,msg_id) VALUES ('{bot_config.ACCOUNT_VIP_AMOUNT}','Active','{authority}',(SELECT id FROM telegram_telegramprofile WHERE telegram_id='{user.id}'),'{time_now}','{msg_id.id}');"
        psql.run_sql(sql_query)

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
            try:
                user = update.effective_user

                sql_query = f"SELECT * FROM telegram_telegramprofile WHERE telegram_id='{user.id}';"
                result = psql.DBQuery.fetchAllSQL(sql_query)

                
                sql_query = f"SELECT * FROM payment_invoice WHERE telegram_profile_id=(SELECT id FROM telegram_telegramprofile WHERE telegram_id='{user.id}');"
                payment_detail = psql.DBQuery.fetchAllSQL(sql_query)


                payment_date = payment_detail[0][2]
                expired_date = payment_detail[0][3]

                #check_expired_account
                if expired_date:
                    time_now = datetime.datetime.now()
                    try:
                        if expired_date.strptime(expired_date.strftime("%Y%m%d"), "%Y%m%d") < time_now.strptime(time_now.strftime("%Y%m%d"), "%Y%m%d"):
                            sql_query = f"UPDATE telegram_telegramprofile SET access_level='Unallowable' WHERE telegram_id='{user.id}';"
                            result = psql.run_sql(sql_query)

                            await query.edit_message_text(
                                text="اعتبار حساب شما به پایان رسیده است، جهت تمدید عضویت ویژه خود اقدام نمایید.",
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [InlineKeyboardButton("💰 خرید اشتراک ویژه", callback_data="payment")],
                                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                                    ]
                                )
                            )

                            return
                        expired_date = expired_date.strftime('%Y/%m/%d')
                    except:
                        expired_date = "---"
                else:
                    expired_date = "---"

                result = result[0]
                access_level = ""

                if result[7] == "Allowed":
                    access_level = "عضویت ویژه"
                else:
                    access_level = "عضویت معمولی"

                await query.edit_message_text(
                    text=f"👤 نام کاربری: {result[2]}\n\n🏆 امتیاز: {result[6]}\n\n🔗 لینک دعوت شما:\n <pre>{result[5]}</pre>\n\n📌 نوع عضویت: {access_level}\n\n ⏱ عضو شده در: {payment_date.strftime('%Y/%m/%d')}\n\n ⌛️ اعتبار حساب تا: {expired_date}\n\n<b>{bot_config.BOT_NAME}</b>",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                        ]
                    ),
                    parse_mode="HTML"
                )
                try:
                    referral = context.user_data['referral']
                except:
                    pass
                else:
                    sql_query = f"SELECT referral_code FROM telegram_telegramprofile WHERE telegram_id='{user.id}';"
                    result = psql.DBQuery.fetchAllSQL(sql_query)


                    #referral code
                    if result[0][0] == None:
                        sql_query = f"UPDATE telegram_telegramprofile SET referral_code='{referral}' WHERE telegram_id='{user.id}';"
                        psql.run_sql(sql_query)
                        sql_query = f"SELECT score,user_name FROM telegram_telegramprofile WHERE telegram_id='{referral}';"
                        result = psql.DBQuery.fetchAllSQL(sql_query)
                        score = int(result[0][0])
                        score += 5
                        username = result[0][1]
                        sql_query = f"UPDATE telegram_telegramprofile SET score='{score}' WHERE telegram_id='{referral}';"
                        psql.run_sql(sql_query)

                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"شما از طریق کاربر {username} به ربات دعوت شده اید. این کد تایید شد و تعداد 5 امتیاز به حساب ایشان اضافه گردید.\n\n شما هم می توانید با دعوت دوستانتان از طریق این کد امتیاز خود را افزایش دهید و کسب درآمد کنید"
                        )

                        await context.bot.send_message(
                            chat_id=referral,
                            text="پیام ربات:\n\nتعداد 5 امتیازات به مجموع امتیاز شما اضافه گردید"
                        )
            except:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text = 'مشکلی پیش آمد، از منوی زیر ربات را دوباره راه اندازی کنید'
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
                        [InlineKeyboardButton("📈 سیگنال فارکس", url=bot_config.LINKS['Forex'])],
                        [InlineKeyboardButton("📉 سیگنال کریپتو", url=bot_config.LINKS['Crypto'])],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )


        elif query.data == "trading_bot":
            await query.edit_message_text(
                text="ربات های تریدر، برای دریافت سورس این ربات ها روی لینک زیر کلیک نمایید",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📥 مشاهده اسکریپت ها ", url=bot_config.LINKS['TraderBot'])],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )



        elif query.data == "airdrop":
            await query.edit_message_text(
                text="با عضویت در کانال معرفی ایردراپ ها، می توانید از پروژه هایی دارای آینده روشن استفاده و سرمایه گذاری کنید.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📥 لینک", url=bot_config.LINKS['Airdrop'])],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )


        elif query.data == "potential_currencies":
            await query.edit_message_text(
                text="با عضویت در کانال معرفی ارز های پر پتانسیل، از معرفی ارز هایی با سود دهی بالا در بلند مدت و کوتاه مدت، جا نمانید!",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📥 لینک ", url=bot_config.LINKS['PotentialCurrencies'])],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            ) 


        elif query.data == "eduction":
            await query.edit_message_text(
                text="با عضویت در کانال آموزش، از تمامی خدماتی که ما ارائه می دهیم و همچنین نحوه استفاده از آن ها مطلع شوید.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📥 لینک ", url=bot_config.LINKS['Eduction'])],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            ) 


        
        elif query.data == "support":

            sql_query = "SELECT * FROM telegram_supportaccount"
            result = psql.DBQuery.fetchAllSQL(sql_query=sql_query)

            support_account = ""

            for i in result:
                support_account += f"'{i[1]}':  {i[2]}\n"

            message = await query.edit_message_text(
                text=f"اکنون مشکل و یا طرح سئوال خود را برای پشتیبانی ما بنویسید تا در اسرع وقت از طریق همین ربات و یا به صورت مستقیم همکاران ما با شما ارتباط بگیرند.\n\n همچنین راه های ارتباطی با ما:\n{support_account}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                    ]
                )
            )

        

            context.user_data['user_ticket'] = [True, message.id]


        elif query.data == "earn_money":
            await query.edit_message_text(
                text="برای اطلاع کامل از نحوه کسب درآمد از طریق ربات، به کانال آموزش سر بزنید.\n\n از خدمات زیر یکی را برگزینید.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔗 ثبت نام بروکر", url=bot_config.LINKS['Broker'])],
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


async def support_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = context.user_data['user_ticket']
    except:
        return
    else:
        if context.user_data['user_ticket'][0]:
            user = update.effective_user.id
            message = update.effective_message.text
            datetime_created = datetime.datetime.now()

            sql_query = f"INSERT INTO telegram_telegramticket (telegram_account_id,text,created,status) VALUES ((SELECT id FROM telegram_telegramprofile WHERE telegram_id='{user}'),'{message}','{datetime_created}','Open');"
            psql.run_sql(sql_query)

            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['user_ticket'][1]
            )

            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "تیکت شما ما موفقیت ثبت شد. همکاران ما در اسرع وقت پاسخ شما را خواهند داد. از صبوری شما سپاس گذاریم.",
                reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("🔙 بازگشت", callback_data='back')],
                        ]
                    ),
            )

            context.user_data['user_ticket'][0] = False


if __name__ == "__main__":
    logger.warning("starting bot ...")

    application = ApplicationBuilder().token(token=bot_config.TOKEN).build()
    application.add_handler(CommandHandler('start', start, has_args=True))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters=filters.ALL, callback=support_messages))
    application.run_polling()

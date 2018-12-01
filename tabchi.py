# -*- coding: utf-8 -*-
import re
import json
import requests
from telebot import TeleBot, types
from os import execl, path, remove
from time import sleep
from redis import StrictRedis
from configparser import ConfigParser
from ruamel.yaml import YAML
from pyrogram.api import functions
# from pyrogram.api.types import InputUser
from pyrogram import (
    Client, Filters, InputPhoneContact
)
from pyrogram.api.errors import (
    BadRequest, Flood, InternalServerError,
    SeeOther, Unauthorized, UnknownError, FloodWait
)
from sys import (
    executable, argv
)

config = ConfigParser()
if path.isfile("./config.ini"):
    config.read("config.ini")
else:
    api_id = input("Please Input ApiId : ")
    api_hash = input("Please Input ApiHash : ")
    phone = input("Please Input Phone Number : ")
    config["pyrogram"] = {
        'api_id': api_id,
        'api_hash': api_hash,
        'phone_number': phone,
        'app_version': '5.0.3',
        'device_model': 'Samsung Galaxy S8',
        'system_version': ''
    }
    gplog = input("Please Input Group Log : ")
    botapi = input("Please Input Helper Token : ")
    info = TeleBot(int(botapi)).get_me()
    botid = info.id
    botuser = info.username
    sudo = input("Please Input Sudo Users : ")
    tabchi = input("Please input Tabchi Id : ")
    f_name = input("Please Input First Name : ")
    DB = input("Please Input DB Number : ")
    session_name = input("Please Input Session Name : ")
    config["tabchi"] = {
        'gplog': gplog,
        'botapi': botapi,
        'api_id': botid,
        'bot_username': botuser,
        'sudo': sudo,
        'tabchi': tabchi,
        'first_name': f_name,
        'DB': DB,
        'session_name': session_name
    }
    with open("config.ini", "w") as configfile:
        config.write(configfile)
    r = StrictRedis(host="localhost", port=6379, decode_responses=True, db=int(DB))
    r.set("info:contacts", "on")
    r.set("info:groups", "on")
    r.set("info:links", "on")
    r.set("info:timelimit", "off")
    r.set("info:fwdspeed", "on")
    r.set("tabchi:gpstime", "35")
    r.set("tabchi:setgpslimit", "60")
    r.set("tabchi:limitgps", "50")
    r.set("tabchi:limitsgps", "50")
    r.set("tabchi:speed", "85")
    r.set("tabchi:jointext", "Hi!")
db = StrictRedis(host="localhost", port=6379, decode_responses=True, db=int(config["tabchi"]["DB"]))
yaml = YAML(typ='safe', pure=True)
txt = yaml.load(open("txt.yml"))
bot = Client(session_name=config["tabchi"]["session_name"], config_file="./config.ini")
gplog = int(config["tabchi"]["gplog"])
tb = TeleBot(config["tabchi"]["botapi"])
tabchi = config["tabchi"]["tabchi"].split(" ")
bot.start()


def is_sudo(user_id):
    sudo_users = config["tabchi"]["sudo"].split(",")
    if str(user_id) in sudo_users:
        return True
    else:
        return False


def sndgplog(text):
    bot.send_message(gplog, text, parse_mode="MarkDown")


def load_data(fname):
    try:
        f = open(fname, "rb")
        return json.loads(f.read())
    except Exception as e:
        print(e)
        return []


def save_data(fname, data):
    f = open(fname, "w")
    f.write(json.dumps(data))
    f.close()


def cnew(foldname, fnewname, opt):
    remove(foldname)
    data = {} if opt == "dict" else []
    with open(fnewname, 'w') as outfile:
        json.dump(data, outfile)


print("Tabchi has been running")
sndgplog("Bot Now Running")


def autfwd(client, m):
    try:
        speed = db.get("tabchi:speed")
        if not db.get("tabchi:time:ads:{}".format(m.chat.id)) and db.get("tabchi:banerid"):
            db.setex("tabchi:time:ads:{}".format(m.chat.id), int(speed), True)
            bot.forward_messages(m.chat.id, gplog, int(db.get("tabchi:banerid")))
    except FloodWait as e:
        print(f"Bot Has Been ShutDown For {e.x} Seconds")
        sleep(e.x)
    except BadRequest as e:
        print(e)
        sndgplog(str(e))
    except Flood as e:
        print(e)
        sndgplog(str(e))
    except InternalServerError as e:
        print(e)
        sndgplog(str(e))
    except SeeOther as e:
        print(e)
        sndgplog(str(e))
    except Unauthorized as e:
        print(e)
        sndgplog(str(e))
    except UnknownError as e:
        print(e)
        sndgplog(str(e))


@bot.on_message(Filters.incoming, group=0)
def groups_received(client, m):
    try:
        if str(m.chat.id) == '777000':
            print(m)
        redis_sgps = len(db.smembers("tabchi:Sgps"))
        redis_gps = len(db.smembers("tabchi:gps"))
        redis_gps_number = db.get("tabchi:limitgps")
        redis_sgps_number = db.get("tabchi:limitsgps")
        text = m.text if m.text else m.caption
        entities = m['entities'] if m["entities"] else m["caption_entities"]
        if str(m.chat.id)[:4] == '-100':
            if redis_gps <= int(redis_gps_number):
                db.sadd("tabchi:Sgps", m.chat.id)
                db.sadd("tabchi:all", m.chat.id)
        else:
            if redis_sgps <= int(redis_sgps_number):
                db.sadd("tabchi:gps", m.chat.id)
                db.sadd("tabchi:all", m.chat.id)
        if entities:
            for i in entities:
                if i['type'] == "url":
                    if re.findall("(t|telegram|tlgrm)(\.)(me|org|dog)(/)(joinchat)(/)(.{22})",
                                  text):
                        r = re.findall("(t|telegram|tlgrm)(\.)(me|org|dog)(/)(joinchat)(/)(.{22})",
                                       text)
                        for v in r:
                            url = 'https://' + ''.join(v)
                            tel = requests.get(url)
                            if not db.get("info:groups") == "on":
                                return
                            if redis_gps <= int(redis_gps_number) and re.findall(">Join Group</a>", tel.text):
                                if db.get("info:timelimit") == "on" and db.get("tabchi:groupjointime"):
                                    if db.get("info:links") == "on":
                                        links = load_data("./links.json")
                                        if url not in links:
                                            links.append(url)
                                        save_data("./links.json", links)
                                    gp = bot.join_chat(url)
                                    print(gp)
                                    if gp.chats.megagroup:
                                        bot.send_message(int("-100" + str(gp.chats.id)), db.get("tabchi:jointext"))
                                    elif gp.chats.megagroup == False:
                                        bot.send_message(int("-" + str(gp.chats.id)), db.get("tabchi:jointext"))
                                    db.setex("tabchi:groupjointime", db.get("tabchi:gpstime"), ":|")
                                    sndgplog("Ye gp join shod va link gp save shod")
                                else:
                                    if db.get("info:links") == "on":
                                        links = load_data("./links.json")
                                        if url not in links:
                                            links.append(url)
                                        save_data("./links.json", links)
                                    bot.join_chat(url)
                                    sndgplog("Ye gp join shod va link gp save shod")
        if is_sudo(m.from_user.id):
            if text == 'bot':
                sndgplog(txt["bot"])
            elif text == 'help':
                sndgplog(txt["help"])
            elif text == "leave gps":
                gps = list(db.smembers("tabchi:gps"))
                for _ in gps:
                    bot.leave_chat(int(_))
            elif text == 'leave sgps':
                sgps = list(db.smembers("tabchi:Sgps"))
                for _ in sgps:
                    bot.send(functions.channels.LeaveChannel(bot.resolve_peer(int(_))))
            elif text == 'leave':
                bot.leave_chat(m.chat.id)
            elif text == 'addall':
                contacts = load_data("./contacts.json")
                for _ in contacts:
                    bot.send(functions.channels.InviteToChannel(
                        channel=bot.resolve_peer(m.chat.id),
                        users=[
                            bot.resolve_peer(_)
                        ]
                    ))
            elif text == 'setbaner' and m.reply_to_message:
                db.set('tabchi:banerid', m.reply_to_message.message_id)
                bot.forward_messages(gplog, gplog, m.reply_to_message.message_id)
                sndgplog(f"Banner has been set to : {m.reply_to_message.message_id}")
            elif text == 'getbaner':
                if db.get("tabchi:banerid"):
                    bot.forward_messages(gplog, gplog, m.reply_to_message.message_id)
                else:
                    sndgplog("Banner Not Found!!!")
            elif text == 'rembaner':
                db.delete("tabchi:banerid")
                sndgplog("baner has been removed")
            elif text == 'getspeed':
                sndgplog("Speed Is {}".format(db.get("tabchi:speed")))
            elif text == 'block pvs':
                pvs = list(db.smembers("tabchi:Pvs"))
                print(type(pvs))
                for _ in pvs:
                    bot.send(functions.contacts.Block(bot.resolve_peer(int(_))))
                sndgplog("All contacts Blocked")
            elif text == "unblock pvs":
                pvs = list(db.smembers("tabchi:Pvs"))
                for _ in pvs:
                    bot.send(functions.contacts.Unblock(bot.resolve_peer(int(_))))
                sndgplog("All contacts unblocked")
            elif text == 'reload':
                while True:
                    python = executable
                    execl(python, python, *argv)
                    sndgplog("**Reloaded**")
                    break
            elif text == 'reload sgps':
                gps = db.smembers("tabchi:Sgps")
                for i in gps:
                    try:
                        bot.get_chat(int(i.replace("-100", "")))
                    except Exception as e:
                        print(e)
                        db.srem("tabchi:Sgps", i)
                        db.srem("tabchi:all", i)
                sndgplog("**Reloaded**\nGroups : {}".format(len(db.smembers('tabchi:Sgps'))))
            elif text == 'reload gps':
                gps = db.smembers("tabchi:gps")
                for i in gps:
                    try:
                        bot.get_chat(int(i.replace("-", "")))
                    except Exception as e:
                        print(e)
                        db.srem("tabchi:gps", i)
                        db.srem("tabchi:all", i)
                sndgplog("**Reloaded**\nGroups : {}".format(len(db.smembers('tabchi:gps'))))
            elif text == "panel":
                bot_results = bot.get_inline_bot_results(config["tabchi"]["bot_username"], config["tabchi"]["DB"])
                bot.send_inline_bot_result(
                    m.chat.id,
                    bot_results.query_id,
                    bot_results.results[0].id
                )
            elif text == "jf":
                sndgplog("Started")
                links = load_data("links.json")
                for _ in links:
                    bot.join_chat(_)
                    sleep(60)
                sndgplog("Finished")
            if re.findall("sleep (.*)", text):
                r = re.findall("sleep (.*)", text)
                sndgplog(txt["sleep"].format(r[0]))
                sleep(int(r[0]))
            elif re.findall("t (.*)", text):
                r = re.findall("t (.*)", text)
                gp = bot.send(functions.messages.CheckChatInvite(r[0]))
                print(gp.chat.id)
                bot.send_message(-1001330894605, "سلام")
            elif re.findall("addme (.*)", text):
                r = re.findall("addme (.*)", text)
                bot.send(functions.channels.InviteToChannel(
                    channel=bot.resolve_peer(r[0]),
                    users=[
                        bot.resolve_peer(173929873)
                    ]
                ))
            elif re.findall("join (.*)", text):
                r = re.findall("join (.*)", text)
                bot.join_chat(r[0])
            elif re.findall("settext (.*)", text):
                r = re.findall("settext (.*)", text)
                db.set("tabchi:jointext", r[0])
                sndgplog(f"Join text Seted To : {r[0]}")
            elif re.findall("setspeed (.*)", text):
                r = re.findall("setspeed (.*)", text)
                db.set("tabchi:speed", r[0])
                sndgplog(f"Banner AutoFwd Set to {r[0]}")
            elif re.findall("setgpstime (.*)", text):
                r = re.findall("setgpstime (.*)", text)
                db.set("tabchi:gpstime", r[0])
                sndgplog(txt["gpstime"].format(r[0]))
            elif re.findall("setgpslimit (.*)", text):
                r = re.findall("setgpslimit (.*)", text)
                db.set("tabchi:limitgps", r[0])
                sndgplog(txt["limitgps"].format(r[0]))
            elif re.findall("setsgpslimit (.*)", text):
                r = re.findall("setsgpslimit (.*)", text)
                db.set("tabchi:limitsgps", r[0])
                sndgplog(txt["limitsgps"].format(r[0]))
            elif re.findall("(fwd|snd) (sgps|gps|pvs|all) ([0-9]+)", text) and m.reply_to_message:
                r = re.findall("(fwd|snd) (gps|pvs|all) ([0-9]+)", text)
                postviews = int(bot.get_messages(m.reply_to_message.forward_from_chat.username,
                                                 m.reply_to_message.forward_from_message_id)["views"])
                if postviews >= int(r[0][2]):
                    sndgplog("WTF???")
                else:
                    links = ''
                    if r[0][1] == 'sgps':
                        links = db.smembers("tabchi:Sgps")
                    elif r[0][1] == 'gps':
                        links = db.smembers("tabchi:gps")
                    elif r[0][1] == 'pvs':
                        links = db.smembers("tabchi:Pvs")
                    elif r[0][1] == 'all':
                        links = db.smembers("tabchi:all")
                    if r[0][0] == 'fwd':
                        for _ in links:
                            if postviews != int(r[0][2]):
                                pre = _.replace("-", "")
                                bot.forward_messages(int(pre.replace("100", "")), m.chat.id,
                                                     m.reply_to_message.message_id)
                                if db.get("info:fwdspeed") == "on":
                                    sleep(int(db.get("tabchi:setgpslimit")))
                            elif postviews >= int(r[0][2]):
                                sendgplog("Finished")
                                break
                    elif r[0][0] == 'snd':
                        for _ in links:
                            pre = _.replace("-", "")
                            bot.send_message(int(pre.replace("100", "")), m.reply_to_message.text,
                                             parse_mode="MarkDown")
                            if db.get("info:fwdspeed") == "on":
                                sleep(int(db.get("tabchi:setgpslimit")))
            elif re.findall("(recent|remove) (contacts|links|sgps|gps|pvs|all)", text):
                r = re.findall("(recent|remove) (contacts|links|sgps|gps|pvs|all)", text)
                if r[0][0] == 'recent':
                    if r[0][1] == "contacts":
                        contacts = load_data("contacts.json")
                        sndgplog("**Contacts:**\n" + "\n".join(contacts[:10]))
                    elif r[0][1] == 'links':
                        links = load_data("links.json")
                        sndgplog("**Links : **\n" + "\n".join(links[:10]))
                    elif r[0][1] == 'gps':
                        gps = db.smembers("tabchi:gps")
                        sndgplog("**Groups : **\n" + "\n".join(list(gps)[:10]))
                    elif r[0][1] == 'sgps':
                        sgps = db.smembers("tabchi:Sgps")
                        sndgplog("**Super Groups : **\n" + "\n".join(list(sgps)[:10]))
                elif r[0][0] == 'remove':
                    if r[0][1] == 'contacts':
                        cnew("contacts.json", "contacts.json", "list")
                        sndgplog("Remove Shod")
                    elif r[0][1] == 'links':
                        cnew("links.json", "links.json", "list")
                        sndgplog("Remove Shod")
                    elif r[0][1] == 'gps':
                        db.delete("tabchi:gps")
                        sndgplog("Del Shod")
                    elif r[0][1] == 'sgps':
                        db.delete("tabchi:Sgps")
                        sndgplog("Del Shod")
                    elif r[0][1] == 'pvs':
                        db.delete("tabchi:Pvs")
                        sndgplog("Del Shod")
                    elif r[0][1] == 'all':
                        db.delete("tabchi:all")
                        sndgplog("Del Shod")
            # elif re.findall("(.*) (on|off)", text):
            #     r = re.findall("(.*) (on|off)", text)
            #     list_options = ['contacts', 'links', 'groups', 'timelimit']
            #     if r[0][0] in list_options:
            #         db.set(f"info:{r[0][0]}", r[0][1])
            #         sndgplog(txt["on/off"].format(r[0][0], r[0][1]))
    except FloodWait as e:
        print(f"Bot Has Been ShutDown For {e.x} Seconds")
        sleep(e.x)
    except BadRequest as e:
        print(e)
        sndgplog(str(e))
    except Flood as e:
        print(e)
        sndgplog(str(e))
    except InternalServerError as e:
        print(e)
        sndgplog(str(e))
    except SeeOther as e:
        print(e)
        sndgplog(str(e))
    except Unauthorized as e:
        print(e)
        sndgplog(str(e))
    except UnknownError as e:
        print(e)
        sndgplog(str(e))


@bot.on_message(filters=Filters.contact, group=-1)
def contact(client, m):
    if not db.get("info:contacts") == "on":
        return
    contacts = load_data("./contacts.json")
    if m.contact.phone_number not in contacts:
        contacts.append(m.contact.phone_number)
    save_data("./contacts.json", contacts)
    bot.send_contact(m.chat.id, config["pyrogram"]["phone_number"], config["tabchi"]["first_name"])
    bot.send_message(m.chat.id, "اددم کن بیا پیوی 🙃")
    bot.add_contacts([InputPhoneContact(str(m.contact.phone_number), str(m.contact.first_name))])


@bot.on_message(filters=Filters.private & Filters.incoming)
def private(client, m):
    db.sadd("tabchi:Pvs", m.chat.id)
    db.sadd("tabchi:all", m.chat.id)


@tb.inline_handler(lambda query: True)
def query(query):
    try:
        if str(query.from_user.id) in tabchi:
            if int(query.query) == int(config["tabchi"]["DB"]):
                markup = types.InlineKeyboardMarkup()
                main = types.InlineKeyboardButton(text="Info", callback_data="info")
                setdata = types.InlineKeyboardButton(text="Set Datas", callback_data="setdata")
                markup.add(main, setdata)
                r1 = types.InlineQueryResultArticle('1', "Panel :|",
                                                    types.InputTextMessageContent('Welcome to Panel Choose One :D '),
                                                    reply_markup=markup)
                tb.answer_inline_query(query.id, [r1])
        else:
            tb.answer_inline_query(query.id, [
                types.InlineQueryResultArticle('1', "You aren't Sudo", types.InputTextMessageContent("Sick"))])
    except Exception as e:
        print(e)


@tb.callback_query_handler(func=lambda call: True)
def callback(call):
    buttonname = types.InlineKeyboardButton(text="Button Name : ", callback_data="nothing_name")
    stats = types.InlineKeyboardButton(text="Status : ", callback_data="nothing_status")
    savecontacts = types.InlineKeyboardButton(text="Save Contacts : ", callback_data="nothig_cnts")
    joingps = types.InlineKeyboardButton(text="Join Gps : ", callback_data="nothig_gps")
    savelinks = types.InlineKeyboardButton(text="Save links : ", callback_data="nothig_links")
    fwdspeed = types.InlineKeyboardButton(text="Forward limit Speed", callback_data="nothing_speedlimitfwd")
    limittime = types.InlineKeyboardButton(text="Time Limit Join : ", callback_data="nothing_lmttime")
    gplinks = types.InlineKeyboardButton(text="Group Links : ", callback_data="nothing_gplinks")
    all = types.InlineKeyboardButton(text="All : ", callback_data="nothing_all")
    pvs = types.InlineKeyboardButton(text="Pvs : ", callback_data="nothing_pvs")
    gps = types.InlineKeyboardButton(text="Groups : ", callback_data="nothing_gps")
    sgps = types.InlineKeyboardButton(text="Sgps : ", callback_data="nothing_sgps")
    cnts = types.InlineKeyboardButton(text="Contacts : ", callback_data="nothing_cnts")
    add_gpstime = types.InlineKeyboardButton("➕", callback_data="add_gpstime")
    sub_gpstime = types.InlineKeyboardButton("➖", callback_data="sub_gpstime")
    nothing = types.InlineKeyboardButton("-----------------", callback_data="nothing")
    add_limitgps = types.InlineKeyboardButton("➕", callback_data="add_limitgps")
    sub_limitgps = types.InlineKeyboardButton("➖", callback_data="sub_limitgps")
    add_limitsgps = types.InlineKeyboardButton("➕", callback_data="add_limitsgps")
    sub_limitsgps = types.InlineKeyboardButton("➖", callback_data="sub_limitsgps")
    sub_limitspeed = types.InlineKeyboardButton("➖", callback_data="sub_setgpslimit")
    add_limitspeed = types.InlineKeyboardButton("➕", callback_data="add_setgpslimit")
    add_banerspeed = types.InlineKeyboardButton("➕", callback_data="add_speed")
    sub_banerspeed = types.InlineKeyboardButton("➖", callback_data="sub_speed")
    back = types.InlineKeyboardButton(text="🔙", callback_data="back")
    main = types.InlineKeyboardButton(text="Info", callback_data="info")
    setdata = types.InlineKeyboardButton("Set Datas", callback_data="setdata")
    mid = call.inline_message_id
    if is_sudo(call.from_user.id):
        if call.data == "info":
            infocontacts = types.InlineKeyboardButton(text=db.get("info:contacts"),
                                                      callback_data="change_contacts")
            infolmttime = types.InlineKeyboardButton(text=db.get("info:timelimit"),
                                                     callback_data="change_timelimit")
            infojoingps = types.InlineKeyboardButton(text=db.get("info:groups"), callback_data="change_groups")
            infolinks = types.InlineKeyboardButton(text=db.get("info:links"), callback_data="change_links")
            infofwdspeed = types.InlineKeyboardButton(text=db.get("info:fwdspeed"), callback_data="change_fwdspeed")
            infogpslink = types.InlineKeyboardButton(text=len(load_data("./links.json")),
                                                     callback_data="links")
            infoall = types.InlineKeyboardButton(text=len(db.smembers("tabchi:all")), callback_data="All")
            infopvs = types.InlineKeyboardButton(text=len(db.smembers("tabchi:Pvs")), callback_data="Pvs")
            infogps = types.InlineKeyboardButton(text=len(db.smembers("tabchi:gps")), callback_data="gps")
            infospgs = types.InlineKeyboardButton(text=len(db.smembers("tabchi:Sgps")), callback_data="Sgps")
            infocnts = types.InlineKeyboardButton(text=len(load_data("./contacts.json")),
                                                  callback_data="cnts")
            markup = types.InlineKeyboardMarkup()
            markup.add(buttonname, stats)
            markup.add(savecontacts, infocontacts)
            markup.add(joingps, infojoingps)
            markup.add(savelinks, infolinks)
            markup.add(fwdspeed, infofwdspeed)
            markup.add(limittime, infolmttime)
            markup.add(gplinks, infogpslink)
            markup.add(all, infoall)
            markup.add(pvs, infopvs)
            markup.add(gps, infogps)
            markup.add(sgps, infospgs)
            markup.add(cnts, infocnts)
            markup.add(back)
            tb.edit_message_text(text="Information Of Bot", inline_message_id=mid, reply_markup=markup)
        elif call.data == "setdata":
            markup = types.InlineKeyboardMarkup()
            gpstime = types.InlineKeyboardButton("Join Time : {}".format(db.get("tabchi:gpstime")),
                                                 callback_data="nothing_gpstime")
            limitgps = types.InlineKeyboardButton("Limit Groups : {}".format(db.get("tabchi:limitgps")),
                                                  callback_data="nothing_limitgps")
            limitsgps = types.InlineKeyboardButton("Limit Sgps : {}".format(db.get("tabchi:limitsgps")),
                                                   callback_data="nothing_limitsgps")
            limitspeed = types.InlineKeyboardButton("Speed Limit : {}".format(db.get("tabchi:setgpslimit")),
                                                    callback_data="nothing_limitspeed")
            banerspeed = types.InlineKeyboardButton("Baner Speed: {}".format(db.get("tabchi:speed")),
                                                    callback_data="nothing_speed")
            markup.add(sub_gpstime, gpstime, add_gpstime)
            markup.add(nothing)
            markup.add(sub_limitgps, limitgps, add_limitgps)
            markup.add(nothing)
            markup.add(sub_limitsgps, limitsgps, add_limitsgps)
            markup.add(nothing)
            markup.add(sub_limitspeed, limitspeed, add_limitspeed)
            markup.add(nothing)
            markup.add(sub_banerspeed, banerspeed, add_banerspeed)
            markup.add(back)
            tb.edit_message_text(":D", inline_message_id=mid, reply_markup=markup)
        elif call.data == "back":
            markup = types.InlineKeyboardMarkup()
            markup.add(main, setdata)
            tb.edit_message_text(text="Welcome to Panel Choose One :D ", inline_message_id=mid,
                                 reply_markup=markup)
        if re.findall(r"change_(.*)", call.data):
            r = re.findall(r"change_(.*)", call.data)
            status = db.get("info:{}".format(r[0]))
            if status == "on":
                db.set("info:{}".format(r[0]), "off")
            else:
                db.set("info:{}".format(r[0]), "on")
            infocontacts = types.InlineKeyboardButton(text=db.get("info:contacts"),
                                                      callback_data="change_contacts")
            infolmttime = types.InlineKeyboardButton(text=db.get("info:timelimit"),
                                                     callback_data="change_timelimit")
            infojoingps = types.InlineKeyboardButton(text=db.get("info:groups"), callback_data="change_groups")
            infolinks = types.InlineKeyboardButton(text=db.get("info:links"), callback_data="change_links")
            infofwdspeed = types.InlineKeyboardButton(text=db.get("info:fwdspeed"), callback_data="change_fwdspeed")
            infogpslink = types.InlineKeyboardButton(text=len(load_data("./links.json")),
                                                     callback_data="links")
            infoall = types.InlineKeyboardButton(text=len(db.smembers("tabchi:all")), callback_data="All")
            infopvs = types.InlineKeyboardButton(text=len(db.smembers("tabchi:Pvs")), callback_data="Pvs")
            infogps = types.InlineKeyboardButton(text=len(db.smembers("tabchi:gps")), callback_data="gps")
            infospgs = types.InlineKeyboardButton(text=len(db.smembers("tabchi:Sgps")), callback_data="Sgps")
            infocnts = types.InlineKeyboardButton(text=len(load_data("./contacts.json")),
                                                  callback_data="cnts")
            markup = types.InlineKeyboardMarkup()
            markup.add(buttonname, stats)
            markup.add(savecontacts, infocontacts)
            markup.add(joingps, infojoingps)
            markup.add(savelinks, infolinks)
            markup.add(fwdspeed, infofwdspeed)
            markup.add(limittime, infolmttime)
            markup.add(gplinks, infogpslink)
            markup.add(all, infoall)
            markup.add(pvs, infopvs)
            markup.add(gps, infogps)
            markup.add(sgps, infospgs)
            markup.add(cnts, infocnts)
            markup.add(back)
            tb.edit_message_text(text="Information Of Bot", inline_message_id=mid, reply_markup=markup)
        elif re.findall("(add|sub)_(.*)", call.data):
            r = re.findall("(add|sub)_(.*)", call.data)
            if r[0][0] == 'add':
                get = db.get("tabchi:{}".format(r[0][1]))
                db.set("tabchi:{}".format(r[0][1]), int(get) + 5)
            elif r[0][0] == 'sub':
                get = db.get("tabchi:{}".format(r[0][1]))
                db.set("tabchi:{}".format(r[0][1]), int(get) - 5)
            markup = types.InlineKeyboardMarkup()
            gpstime = types.InlineKeyboardButton("Join Time : {}".format(db.get("tabchi:gpstime")),
                                                 callback_data="nothing_gpstime")
            limitgps = types.InlineKeyboardButton("Limit Groups : {}".format(db.get("tabchi:limitgps")),
                                                  callback_data="nothing_limitgps")
            limitsgps = types.InlineKeyboardButton("Limit Sgps : {}".format(db.get("tabchi:limitsgps")),
                                                   callback_data="nothing_limitsgps")
            limitspeed = types.InlineKeyboardButton("Speed Limit : {}".format(db.get("tabchi:setgpslimit")),
                                                    callback_data="nothing_limitspeed")
            banerspeed = types.InlineKeyboardButton("Baner Speed: {}".format(db.get("tabchi:speed")),
                                                    callback_data="nothing_speed")
            markup.add(sub_gpstime, gpstime, add_gpstime)
            markup.add(nothing)
            markup.add(sub_limitgps, limitgps, add_limitgps)
            markup.add(nothing)
            markup.add(sub_limitsgps, limitsgps, add_limitsgps)
            markup.add(nothing)
            markup.add(sub_limitspeed, limitspeed, add_limitspeed)
            markup.add(nothing)
            markup.add(sub_banerspeed, banerspeed, add_banerspeed)
            markup.add(back)
            tb.edit_message_text(":D", inline_message_id=mid, reply_markup=markup)
    else:
        tb.answer_callback_query(call.id, text="You Aren't Sudo Please Sick", show_alert=True)


tb.polling()

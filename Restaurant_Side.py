# importing the telegram bot
import time

import telegram
from telegram import *
from telegram.ext import *
# importing the items and prices from Menu
from Menu import item_list
# to copy the content from one file to another file
import shutil
# importing json
import json

# helps us connect to the telegram with the
Token1 = '5131675223:AAH_9GqSF3RMtCaUEiALwcbr3ly869oTMls'

print("Restaurant bot started...")

order_items = ''

admin_ids = [967864205]


# displays the current Menu with the prices.
def Menu(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        item_prices = {}
        with open("temp_menuitems.txt") as f:
            for line in f:
                (k, v) = line.replace(':', ':').replace('-', ':').split(':')
                item_prices[k] = float(v)
        list_items = list(item_prices.items())

        final = ''
        for x in list_items:
            final += str(x).replace(",", ":").replace("'", "").replace("(", "").replace(")", "\n")

        # displaying the items in the bot.
        update.message.reply_text(f'Current Item List: \n\n{final}')
    else:
        update.message.reply_text('You are not authorized to access this BOT')


# displays the feedbacks received.
def feedback(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        # opening the feedbacks from a file.
        with open("feedbacks.txt", 'r', encoding='utf-8') as f:
            feed_string = f.read()
        # displaying the result in the Restaurant bot
        update.message.reply_text(feed_string)
    else:
        update.message.reply_text('You are not authorized to access this BOT')


# displays the inquiries received.
def inquiries(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        # opening the inquiries from a file.
        with open("inquiries.txt", 'r', encoding='utf-8') as f:
            feed_string = f.read()
        # displaying the result in the Restaurant bot
        update.message.reply_text(feed_string)
    else:
        update.message.reply_text('You are not authorized to access this BOT')


# shows the useful commands during the session with a short description.
def help_commands(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="/menu - to check the current menu list with prizes\n"
                                      "/scheme [item-name] - to activate the Try your Luck scheme(exact name)\n "
                                      "/show [YYYY-MM-DD] - to see the orders received on a particular date\n"
                                      "/maintenance - to set the bot to maintenance \n"
                                      "/online - to set the bot back online \n"
                                      "/feedback -  to see the received feedbacks\n"
                                      "/unavailable [exact item-name]- to set an item to unavailable list\n"
                                      "/available [exact item-name]- to set an item to available\n"
                                      "/unavailable_list - displays the unavailable items \n"
                                      "/scheme_list - displays the items under the scheme \n"
                                      "/inquiries - shows all the collected inquiries \n"
                                      "/help - displays all the usable commands")
    else:
        update.message.reply_text('You are not authorized to access this BOT')


# usable commands
def action(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        update.message.reply_text("Try to communicate using the following commands with the Bot. "
                                  "I cannot understand any other language besides the following commands")
        help_commands(update, context)
    else:
        update.message.reply_text("You are not authorized to access this Bot")


# changing the price an item to zero to activate the scheme
def activateScheme(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        change = update.effective_message.text
        edit = change[8:].strip()
        if edit == 'deactivate':
            shutil.copyfile('original_menuitems.txt', 'temp_menuitems.txt')
            # emptying the scheme list.
            with open("scheme_list.txt", 'w') as f:
                f.truncate(0)
            f.close()
            update.message.reply_text("Scheme has been deactivated")
        elif edit == "list":
            # opening the scheme list
            with open("scheme_list.txt", 'r', encoding='utf-8') as f:
                feed_string = f.read()
            if len(feed_string) == 0:
                update.message.reply_text('Scheme Not Activated')
            else:
                # displaying the result in the Restaurant bot
                update.message.reply_text("Item's list under the Scheme: \n \n" + feed_string)
        elif len(edit) == 0:
            update.message.reply_text('There is nothing to put under scheme. \n'
                                      'Format: /scheme [exact item-name]\n'
                                      'for example: /scheme Basbousa')
        else:
            # to capitalize the first letter of each word of item.
            edit = edit.title()
            fan = edit.strip()

            menu_items = {}
            # reading the items list from the file
            with open("temp_menuitems.txt") as f:
                for line in f:
                    (k, v) = line.replace(':', ':').replace('-', ':').split(':')
                    menu_items[k] = float(v)  # changing the prize of a specific item you asked for

            menu_items[fan] = 0.0
            f.close()

            # adding the item to scheme list
            with open("scheme_list.txt", 'a') as f:
                f.write(fan+"\n")
            f.close()

            # re-writing the new modified list back into the list
            with open("temp_menuitems.txt", 'w') as f:
                for key, value in menu_items.items():
                    f.write('%s: %.2f\n' % (key, float(value)))
            f.close()
            update.message.reply_text("Item is under the scheme")
    else:
        update.message.reply_text("You are not authorized to access this Bot")


# setting bot under maintenance
def maintenance(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        with open("maintenance.txt", 'w') as f:
            f.write("Maintenance")
        f.close()
        update.message.reply_text("Bot is set to Maintenance state.")

    else:
        update.message.reply_text("You are not authorized to access this Bot")


# setting bot to online
def online(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        with open("maintenance.txt", 'r+') as f:
            content = f.read()
            if len(content) >= 5:
                f.truncate(0)
        f.close()

        update.message.reply_text("Bot is online")

    else:
        update.message.reply_text("You are not authorized to access this Bot")


# shows orders of a specific date.
def showOrders(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        change = update.effective_message.text
        edit = change[5:].strip()
        edit = edit + '.txt'
        try:
            # opening the file if exists.
            f = open(edit, 'r')
            update.message.reply_text(f.read())
            f.close()
        except IOError:  # if the files does not exist or spell wrong
            update.message.reply_text("No File Exists on that name\n"
                                      "Format: /show YYYY-MM-DD\n"
                                      "Example: /show 2022-05-31")

    else:
        update.message.reply_text("You are not authorized to access this Bot")


# setting an item to unavailable list
def unavailable(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        item = update.effective_message.text
        edit = item[12:].strip()
        file1 = open("unavailable.txt", "r+")
        readfile = file1.read()
        if edit in readfile:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="The item is already set to unavailable")
        else:
            file1.write(edit + "\n")
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="The item is set unavailable")

    else:
        update.message.reply_text('You are not authorized to access this BOT')


# setting an item to available
def available(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        item = update.effective_message.text
        edit = item[10:].strip()

        # Read file.txt
        with open('unavailable.txt', 'r') as file:
            readfile = file.read()

        if edit == 'all':
            with open('unavailable.txt', 'w') as file:
                file.truncate(0)
                file.close()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Every item is set to available.")
        elif edit in readfile:
            # Delete text and Write
            with open('unavailable.txt', 'w') as file:
                # Delete
                new_text = readfile.replace(edit, '')
                # Write
                file.write(new_text)
                file.close()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="The item is set to available.")

        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="The item is already set to available")

    else:
        update.message.reply_text('You are not authorized to access this BOT')


# displays the scheme list
def scheme(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        # opening the scheme list
        with open("scheme_list.txt", 'r', encoding='utf-8') as f:
            feed_string = f.read()
        if len(feed_string) == 0:
            update.message.reply_text('Scheme Not Activated')
        else:
            # displaying the result in the Restaurant bot
            update.message.reply_text("Item's list under the Scheme: \n \n"+feed_string)
    else:
        update.message.reply_text('You are not authorized to access this BOT')


# displays the unavailable list
def unavailablelist(update: Update, context: CallbackContext):
    if update.message.from_user.id in admin_ids:
        # opening the unavailable
        with open("unavailable.txt", 'r', encoding='utf-8') as f:
            feed_string = f.read()
        if len(feed_string) == 0:
            update.message.reply_text('All items are available at the moment')
        else:
            # displaying the result in the Restaurant bot
            update.message.reply_text("Unavailable Items list: \n \n"+feed_string)
        f.close()
    else:
        update.message.reply_text('You are not authorized to access this BOT')


def main():
    # Start the bot
    # accessing the file for the received feedbacks.
    persistence = PicklePersistence(filename="feedbacks")

    # get the updater to register handlers to the particular bot using token
    updater = Updater(Token1, persistence=persistence)
    dp = updater.dispatcher

    # reacting to the commands - according to the commands
    dp.add_handler(CommandHandler('feedback', feedback))
    dp.add_handler(CommandHandler('menu', Menu))
    dp.add_handler(CommandHandler('scheme', activateScheme))
    dp.add_handler(CommandHandler('maintenance', maintenance))
    dp.add_handler(CommandHandler('online', online))
    dp.add_handler(CommandHandler('unavailable', unavailable))
    dp.add_handler(CommandHandler('available', available))
    dp.add_handler(CommandHandler('show', showOrders))
    dp.add_handler(CommandHandler('start', help_commands))
    dp.add_handler(CommandHandler('help', help_commands))
    dp.add_handler(CommandHandler('unavailable_list', unavailablelist))
    dp.add_handler(CommandHandler('scheme_list', scheme))
    dp.add_handler(CommandHandler('inquiries', inquiries))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, action))

    # connect to telegram and wait for the messages.
    updater.start_polling()

    # keep the program running until interrupted.
    updater.idle()


# starting the bot
if __name__ == '__main__':
    main()

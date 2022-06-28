# importing the telegram bot
import logging

from telegram import *
from telegram.ext import *

import io
# to know the date and time
import datetime

# importing the token
from key import *

# to get the user location and calculate the distance
from geopy.geocoders import Nominatim
from geopy import distance

# necessary variables, def's  from menu
from Menu import random, menu, item_list, prices, inquiries, common_special_days, friday, sunday

TOKEN = Token
print("Customer bot started...")
cart_dict = {}
Location = ''
Order_type = ''
pNumber = ''
startsession = False
location_count = 0
rest_lat, rest_long = 17.4299296940903, 78.41130927055349  # Restaurant coordinates
user_latcord = ''
user_longcord = ''

# logger format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# prints the user moments trough out the session
logger = logging.getLogger(__name__)


# Tells what to do to make order and shows all the usable commands with short descriptions attached.
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s has stared the bot", user.first_name)
    update.message.reply_text(text="I can help you place and manage your order.  \n \n"
                                   "TO DO things to Order: \n"
                                   "1. Start the session\n"
                                   "2. Choose your Order Type(Online/Pickup)\n"
                                   "3. Provide your phone number\n"
                                   "4. Provide your delivery coordinates if you preferred order type is online \n "
                                   "5. Choose your items"
                                   "6. Confirm checkout\n\n"
                                   "You can control me by sending these commands: \n \n"
                                   "/start_session - starts the session \n"
                                   "/order_type - to change the order type \n"
                                   "/number [phone number] - to provide your phone number(Indian only)\n"
                                   "/locate [lat],[long] - to provide your delivery location(latitude, longitude)\n"
                                   "/cart - shows the cart items \n"
                                   "/delete [item_no] - enter number of item \n"
                                   "/feedback [Enter the feedback] - to submit the feedback\n"
                                   "/inquiry [Enter the inquiry] - to submit the inquiry\n"
                                   "/checkout - check out of the session and place order\n"
                                   "/cancel - to cancel the session\n"
                                   "/coordinates_laptop - exemplary steps to know the coordinates from laptop\n"
                                   "/coordinates_phone - exemplary steps to know the coordinates from phone\n\n"
                                   "NOTE: \n"
                                   "1. You cannot delete the order once you have placed\n"
                                   "2. Pay/Cash on Delivery/Pickup.")


# user should choose an option among three (Menu, Day to Day Specials, Inquires)
def menu_list(update: Update, context: CallbackContext):
    global startsession
    user = update.message.from_user
    logger.info("User %s has started the bot chat_id: %s", user.first_name, update.message.from_user.id)
    currentTime = datetime.datetime.now().time()
    f = open("maintenance.txt", 'r+')
    content = f.read()
    # checking weather the bot is set to maintenance state or not
    if content == 'Maintenance':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Bot is under Maintenance. Sorry for the inconvenience")
    # if the bot is not set to maintenance state and order is in time... Allowing the customer to choose their mode
    # of delivery.
    elif len(content) == 0:
        startsession = True
        if time_in_range(currentTime):
            reply_buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("Online Delivery", callback_data="Online")],
                [InlineKeyboardButton("Pickup", callback_data='Pickup')]
            ])

            # sends the message with three option buttons attached.
            context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there, please choose your order type.",
                                     reply_markup=reply_buttons)
        # letting the users know if the time is up for orders for the day.
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Sorry we are closed for orders. You can make orders from \n"
                                          "10AM - 10PM everyday. Thank you and visit again.")


# returns weather the current time is open or close for orders
def time_in_range(current):
    start = datetime.time(10, 0, 0)
    end = datetime.time(23, 00, 0)
    return start <= current <= end


# displays the cart list
def cart_list(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s is viewing cart", user.first_name)
    # "cart is empty" will be displayed if nothing in the cart
    if len(cart_dict) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Cart is empty")
    else:
        # calling the organize method to get the cart organized to display format
        car, order_amt = organize()
        line_space = '\n'
        stir = ' \n'.join(car)
        stir += "\n \n" + "Total amount: " + "\t     ₹" + str(order_amt)
        # cart list will be displayed in the bot
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your Cart: {line_space}{stir}")


# to delete the item from cart
def delete(update: Update, context: CallbackContext):
    user = update.message.from_user
    # getting the text from the user
    delete_item = update.message.text
    # finding the number to delete
    item_no = delete_item[7:].strip()
    logger.info("User %s wants to delete", user.first_name)

    # checking if it's numeric or not
    if item_no.isnumeric():
        # if numeric and below the length of cart list - deleting the item
        if len(cart_dict) >= int(item_no) >= 1:
            li = list(cart_dict.keys())
            # deleting the item from the cart
            del cart_dict[li[int(item_no) - 1]]
            # displaying the deleted message
            context.bot.send_message(chat_id=update.effective_chat.id, text="item has been deleted from your cart.")
        # if intent number is beyond the cart length
        elif int(item_no) >= len(cart_dict) or int(item_no) == 0:
            # if the cart length is 0
            if len(cart_dict) == 0:
                # displaying the cart is empty - no items
                context.bot.send_message(chat_id=update.effective_chat.id, text="Your cart is empty!!")
            # if the inputted number is beyond
            else:
                # displaying the user to check their input.
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="your input is wrong. please check your input.")
    # displaying the correct format if the entered command is not correct.
    elif type(item_no) == str or len(item_no) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="your command is unclear. please try to be "
                                                                        "clear.\n "
                                                                        "No item number present\n"
                                                                        "format is /delete [your item Number] \n"
                                                                        "Example: /delete 1 - will delete the 1st "
                                                                        "item from your cart")


# will be triggered on entering queries or to solve them.
def action(update: Update, context: CallbackContext):
    global Order_type, pNumber, Location, startsession, user_longcord, user_latcord

    # getting the text from the bot.
    update.callback_query.answer()
    choice = update.callback_query.data

    # if the text is menu, calling the menu
    if choice == "menu":
        menu(update, context)
    # if the text is from the menu items, adding the item to the cart
    elif choice in item_list:
        with open('unavailable.txt', 'r') as file:
            readfile = file.read()
        day = datetime.datetime.today().strftime('%A')
        if startsession:
            # checking the availability of the item
            if choice in readfile:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f'{choice} is not available at the '
                                                                                f'moment. Sorry for the inconvenience.')
            # if the item is available, it will be added to the cart
            elif choice in cart_dict:
                cart_dict.update({choice: (int(cart_dict.get(choice)) + 1)})
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"{choice} added to the cart")
            elif day == 'Friday' or day == 'Sunday':
                if choice in readfile:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{choice} is not available at the '
                                                                                    f'moment. Sorry for the '
                                                                                    f'inconvenience.')
                else:
                    cart_dict.update({choice: 1})
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{choice} added to the cart")
            elif day != 'Friday' and choice in friday:
                if choice in common_special_days:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{choice} is available on '
                                                                                    f'Fridays and Sundays only')
                elif choice in friday:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{choice} is available on '
                                                                                    f'Fridays only')
            elif day != 'Sunday' and choice in sunday:
                if choice in common_special_days:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{choice} is available on '
                                                                                    f'Fridays and Sundays only')
                elif choice in friday:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{choice} is available on '
                                                                                    f'Sundays only')
            # if the item is already in the cart, it will just increase the items number+1.
            else:
                cart_dict.update({choice: 1})
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"{choice} added to the cart")
        # if user did not start the session
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You did not start the session yet")
    elif choice == 'no':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ok")
    elif choice == 'inquiry':
        inquiries(update, context)
    elif choice == 'store_address':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Gismat restaurants, 1st floor,"
                                                                        "1217/A Shreshtra Aura,RoadNo-36,"
                                                                        "Jubilee Hills, Hyderabad,"
                                                                        "Telangana- 5000033, INDIA")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Store Location: https://maps.app.goo.gl/5NofNcVCg7jLaM4t6")
    elif choice == 'customer_care_number':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You can contact +91 7075234341 for any inquiries")
    elif choice == 'open_timings':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Store Timings - 10:00 AM to 11:00 PM\n"
                                                                        "Bot Order Timings - 10:00 AM to 10:00 PM")
    elif choice == "delivery_time":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You will receive your order within 35-40 mins from ordered time.")
    elif choice == "pickup-time":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You can collect the after 20-25 mins from ordered time.")
    elif choice == "Pickup":
        Order_type = 'Pickup'
        random(update, context)
    elif choice == "Online":
        Order_type = 'Online'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="please type in your location 📍 coordinates using /locate (lat),(long) using "
                                      "this "
                                      "format. In case if you don't know how? /coordinates_phone or /coordinates_laptop")
    elif choice == "change_Pickup":
        Order_type = 'Pickup'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Your Order type has been successfully updated to Pickup.")
    elif choice == "change_Online":
        Order_type = 'Online'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Your Order type has been successfully updated to Online Delivery. "
                                      "Please provide the delivery coordinates(/locate lat,long ) if you haven't yet. ")
    elif choice == 'Yes_checkout':
        if len(cart_dict) == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Cart is empty")
        else:
            with io.open('orders.txt', "a", encoding="utf-8") as f:
                # asking the user to provide the phone number
                if len(pNumber) == 0:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Sorry! you cannot checkout without providing your phone number")
                # asking the user to choose an order type.
                elif len(Order_type) == 0:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Sorry! you cannot checkout without choosing your order type")
                    changeOrderType(update, context)
                # checkout the user with pickup as order type
                elif Order_type == 'Pickup':
                    startsession = False
                    car, order_amt = organize()
                    stir = f'Name: {update.effective_user.full_name} \n' \
                           f'Phone Number: {pNumber} \n' \
                           f'Order type: {Order_type}\n' \
                           f'Date/time: {datetime.datetime.now()}\n \n'
                    stir += ' \n'.join(car)
                    stir += "\n \n" + "TOTAL AMOUNT: " + "\t     ₹" + str(order_amt)
                    f.write(stir)
                    # indicates the end of the order and its specifics.
                    f.write("\n#### \n \n")
                    f.close()
                    cart_dict.clear()
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="You can pick your meal from the Store after 25 minutes.\n \n"
                                                  "PickUp Location: https://maps.app.goo.gl/5NofNcVCg7jLaM4t6")
                    update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
                # checkout the user with Online delivery  as order type
                elif Order_type == 'Online':
                    startsession = False

                    if not len(Location) == 0:
                        car, order_amt = organize()
                        stir = f'Name: {update.effective_user.full_name} \n' \
                               f'Coordinates Latitude, Longitude: {user_latcord, user_longcord}\n' \
                               f'Location: {Location} \n' \
                               f'Phone Number: {pNumber} \n' \
                               f'Order type: {Order_type}\n' \
                               f'Date/time: {datetime.datetime.now()} \n \n'
                        stir += ' \n'.join(car)
                        stir += "\n \n" + "TOTAL AMOUNT: " + "\t     ₹" + str(order_amt)
                        f.write(stir)
                        # indicates the end of the order and its specifics.
                        f.write("\n#### \n \n")
                        f.close()
                        cart_dict.clear()
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Your Meal is on the way.")
                        update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id,
                                                 text="Sorry! you cannot checkout without providing your delivery "
                                                      "coordinates.")
                    clear(update, context)

    elif choice == 'No_checkout':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Checked Out")
        clear(update, context)
    # cancelling the order
    elif choice == 'cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Your order has been successfully cancelled.')
        update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))
        clear(update, context)
    # if input is anything beyond the above choices, asking the user regarding their problem.
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="What's your problem")


# displaying an helpful image with steps how to get the coordinates from phone
def coordphone(update: Update, context: CallbackContext):
    context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('images/phone.png', 'rb'))


# displaying an helpful image with steps how to get the coordinates from phone
def coordlaptop(update: Update, context: CallbackContext):
    context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('images/laptop.png', 'rb'))


# clearing the user's prior location, number and ordertype to start the fresh session
def clear(update: Update, context: CallbackContext):
    global pNumber, Location, Order_type, startsession, location_count, user_latcord, user_longcord
    pNumber = ''
    Location = ''
    Order_type = ''
    cart_dict.clear()
    startsession = False
    location_count = 0
    user_latcord = ''
    user_longcord = ''


# collects the user phone number
def phoneNumber(update: Update, context: CallbackContext):
    global pNumber
    user_message = update.message.from_user
    user_number = update.effective_message.text

    number = user_number[7:].strip()

    if number.isdigit() and len(number) == 10:
        logger.info("User %s provided the Phone Number", user_message.first_name)
        pNumber = number
        context.bot.send_message(chat_id=update.effective_chat.id, text="Number has been successfully stored")
    # letting user know that inputted number is not an appropriate phone number.
    elif not number.isdigit():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please enter only 10 digit phone number")
    # letting the user know that the inputted number is not exactly 10 digits.
    elif len(number) > 10 or len(number) < 10:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Inputted number should be only of 10 digits!")


# collecting the location of the user.
def location(update: Update, context: CallbackContext):
    global Location, location_count, rest_lat, rest_long, user_longcord, user_latcord
    user_message = update.message.from_user
    user_coordinates = update.effective_message.text
    coordinates = user_coordinates[8:].strip()

    # displaying the correct format, incase the inputted format is wrong
    if len(coordinates) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="There are no coordinates\n"
                                      "format is : /locate [lat], [long] \n"
                                      "Example: /locate 1.2342, 8.345")

    user_lat, user_long = coordinates.replace(':', ',').replace('-', ',').split(',')

    geolocator = Nominatim(user_agent='geoapiExercises')

    rest_location = (rest_lat, rest_long)
    user_location = (user_lat, user_long)
    locname = geolocator.reverse(user_location)
    # calculating the distance from the store
    dist = distance.distance(rest_location, user_location).km

    user_latcord = user_lat
    user_longcord = user_long

    if dist <= 10:
        logger.info("User %s provided the location", user_message.first_name)
        location_count = location_count + 1
        Location = locname.address
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Location confirmed")
        if location_count <= 1:
            random(update, context)
        else:
            pass
    # letting the user know that delivery services are available unto 10 KM radius only.
    elif dist > 10:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Delivery Service is only available within the 10KM radius due to the distant "
                                      "issues. Please choose a location within the specified radius")


# to submit your feedback.
def feedback(update: Update, context: CallbackContext):
    user = update.message.from_user
    # getting the feedback form the bot
    feed = update.effective_message.text
    edit = feed[9:].strip()

    # if the feedback is empty - displaying the format
    if len(edit) == 0:
        update.message.reply_text("feedback is empty.... \n"
                                  "format is /feedback [your feedback] \n"
                                  "Example: /feedback your service is awesome")
    # if feedback is not empty
    elif len(edit) > 0:
        logger.info("User %s has submitted the feedback", user.first_name)
        # storing the feedback in the file with user-ID, Full Name and date time.
        with open("feedbacks.txt", 'a', encoding='utf-8') as f:
            f.write(
                f'ID: {update.effective_user.id}, Fullname: {update.effective_user.full_name}, Date_Time: {datetime.datetime.now()}  \n '
                f'{edit}\n \n \n')
        update.message.reply_text('feedback submitted')
        f.close()


# to submit your inquiry.
def inquiry(update: Update, context: CallbackContext):
    user = update.message.from_user
    # getting the inquiry form the bot
    feed = update.effective_message.text
    edit = feed[9:].strip()

    # if the inquiry is empty - displaying the format
    if len(edit) == 0:
        update.message.reply_text("inquiry is empty.... \n"
                                  "format is /inquiry [your inquiry] \n"
                                  "Example: /inquiry do you have door service?")
    # if inquriry is not empty
    elif len(edit) > 0:
        logger.info("User %s has submitted an inquiry", user.first_name)
        # storing the inquiry in the file with user-ID, Full Name and date time.
        with open("inquiries.txt", 'a', encoding='utf-8') as f:
            f.write(
                f'ID: {update.effective_user.id}, Fullname: {update.effective_user.full_name}, Date_Time: {datetime.datetime.now()}  \n '
                f'{edit}\n \n \n')
        update.message.reply_text('Inquiry submitted')
        f.close()


# cancelling the order
def cancelOrder(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s wants to cancel the order", user.first_name)
    if not startsession:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You did not start the session.")
    # conforming one last time.
    else:
        reply_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data="cancel"),
             InlineKeyboardButton("No", callback_data='no')]
        ])

        context.bot.send_message(chat_id=update.effective_chat.id, text="Are you sure you want to cancel the order",
                                 reply_markup=reply_buttons)


# places the order on checking out. if no order, displays the "no order placed" text.
def checkout(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s wants to checkout", user.first_name)
    # if cart is empty - just checks out without placing any order
    if len(cart_dict) == 0:
        reply_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data="No_checkout"),
             InlineKeyboardButton("No", callback_data='no')]
        ])
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Your cart is empty. Do you still wanna checkout?"
                                 , reply_markup=reply_button)
        # context.bot.deleteMessage(chat_id=update.effective_chat.id, message_id= )
    # if cart is not empty - asks the user final time to place the order or not.
    else:
        reply_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data="Yes_checkout"),
             InlineKeyboardButton("No", callback_data='no')]
        ])

        # asking to provide the phone number, incase they haven't
        if len(pNumber) == 0:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Please provide your phone number to checkout. /number [phone_number]")
        # asking to choose order type, incase they haven't
        elif len(Order_type) == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Please choose your Order type")
            changeOrderType(update, context)
        # if the order type is pickup
        elif Order_type == 'Pickup':
            car, order_amt = organize()
            stir = f'Name: {update.effective_user.full_name} \n' \
                   f'phone Number: {pNumber} \n' \
                   f'Order type: {Order_type}\n' \
                   f'Date/time: {datetime.datetime.now()}\n\n'
            stir += ' \n'.join(car)
            stir += "\n \n" + "TOTAL AMOUNT: " + "\t     ₹" + str(order_amt)
            stir += "\n \n" + "NOTE: pay/cash on delivery/pickup"
            context.bot.send_message(chat_id=update.effective_chat.id, text=stir, reply_markup=reply_buttons)
        # if the order type is Online
        elif Order_type == 'Online':
            if not len(Location) == 0:
                car, order_amt = organize()
                stir = f'Name: {update.effective_user.full_name} \n' \
                       f'Coordinates Latitude, Longitude: {user_latcord, user_longcord}\n' \
                       f'Location: {Location} \n' \
                       f'phone Number: {pNumber} \n' \
                       f'Order type: {Order_type}\n' \
                       f'Date/time: {datetime.datetime.now()} \n \n'
                stir += ' \n'.join(car)
                stir += "\n \n" + "TOTAL AMOUNT: " + "\t     ₹" + str(order_amt)
                stir += "\n \n" + "NOTE: pay/cash on delivery/pickup"
                context.bot.send_message(chat_id=update.effective_chat.id, text=stir, reply_markup=reply_buttons)
            # asking to provide the delivery coordinates, incase they haven't
            elif len(Location) == 0:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Please provide your delivery coordinates")


# changing the order type.
def changeOrderType(update: Update, context: CallbackContext):
    global location_count
    location_count = location_count + 1
    user = update.message.from_user
    logger.info("User %s wants to change the order type", user.first_name)
    reply_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Online Delivery", callback_data="change_Online")],
        [InlineKeyboardButton("Pickup", callback_data='change_Pickup')]
    ])

    # sends the message with three option buttons attached.
    context.bot.send_message(chat_id=update.effective_chat.id, text="choose your Order type.",
                             reply_markup=reply_buttons)


# organizing the cart into displayable format.
def organize():
    car = []
    order_amt = 0.0
    for key, value in cart_dict.items():
        car.append(key + "\t     " + str(value) + "*" + str(prices(key)))
        order_amt += float(float(value) * float(prices(key)))
    return car, order_amt


# shows the useful commands during the session with a short description.
def help_commands(update: Update, context: CallbackContext):
    update.message.reply_text("Usable commands:  \n \n"
                              "/start - to see the brief things to do with the bot\n"
                              "/start_session - starts the session \n"
                              "/order_type - to change the order type \n"
                              "/number [phone number] - to provide your phone number(Indian only)\n"
                              "/locate [lat],[long] - to provide your delivery location(latitude, longitude)\n"
                              "/cart - shows the cart items \n"
                              "/delete [item_no] - enter number of item \n"
                              "/feedback [Enter the feedback] - to submit the feedback\n"
                              "/checkout - check out of the session and place order\n"
                              "/cancel - to cancel the session\n"
                              "/coordinates_laptop - steps to know the coordinates from laptop\n"
                              "/coordinates_phone - steps to know the coordinates from phone")


# while any error occurs
def error(bot, update):
    logger.error("Shit!! Update {} caused error {}".format(update, update.error))


def out_of_commands(update: Update, context: CallbackContext):
    update.message.reply_text("Try to communicate using the following commands with the Bot. "
                              "I cannot understand any other language besides the following commands")
    help_commands(update, context)


def main():
    # Start the bot

    # storing the feedback into the feedbacks file.
    persistence = PicklePersistence(filename="feedbacks")

    # get the updater to register handlers to the particular bot using token
    updater = Updater(TOKEN, persistence=persistence)
    dp = updater.dispatcher

    # reacting to the commands - according to the commands
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('start_session', menu_list))
    dp.add_handler(CommandHandler('feedback', feedback))
    dp.add_handler(CommandHandler('locate', location))
    dp.add_handler(CommandHandler('cart', cart_list))
    dp.add_handler(CommandHandler('checkout', checkout))
    dp.add_handler(CommandHandler('help', help_commands))
    dp.add_handler(CommandHandler('order_type', changeOrderType))
    dp.add_handler(CommandHandler('delete', delete))
    dp.add_handler(CommandHandler('cancel', cancelOrder))
    dp.add_handler(CommandHandler('number', phoneNumber))
    dp.add_handler(CommandHandler('coordinates_phone', coordphone))
    dp.add_handler(CommandHandler('coordinates_laptop', coordlaptop))
    dp.add_handler(CommandHandler('inquiry', inquiry))
    dp.add_handler(CallbackQueryHandler(action))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, out_of_commands))

    dp.add_error_handler(error)
    # connect to telegram and wait for the messages.
    updater.start_polling()

    # keep the program running until interrupted.
    updater.idle()


# starting the bot
if __name__ == '__main__':
    main()

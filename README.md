
# GISMAT Bot

This chatbot is capable of serving you with your favorite eateries from GISMAT Restaurants. Moreover, helps you make an order with your preferred order type(online/pickup). Happy to serve you as always.

The whole system is divided into three bots. 


one for the Customer side and remaining for the restaurant use.

Telegram Bot username -  concise description

@gismatbot_Bot - It is for the customer use. can order with your preferred order type.

@gismatOrderBot - It is designed to recieve orders without any interruptions.

@sidebot_bot - It helps you manage the customer side bot such as setting the unavailable items, bot under maintenance. 
## Installation

```bash
  pip install python-telegram-bot
```
```bash
  pip install geopy
```

versions: 

python 3.8.

python telegram bot 13.0

geopy 2.2.0
## To start the bot

To deploy this project run.

1. Start all three files from the pycharm terminal.

```bash
  python .\Customer_Side.py
```

```bash
  python .\Restaurant_Side.py
```
```bash
  python .\GismatOrderBot.py
```

2. Give the orders command in the @gismatOrderBot telegram channel. 

```bash
  /orders
```
You can start to use the bot..

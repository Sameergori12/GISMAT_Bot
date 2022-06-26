import datetime

day = datetime.datetime.today().strftime('%A')

if day == "Sunday":
    print("this is friday...")
elif day != 'Sunday':
    print("It's not friday... you idiot... its sunday ")
else:
    print("Not the case")


print(day)
import os
import discord
import requests
import json
import random
from keep_alive import keep_alive
# from discord.ext import tasks
from datetime import datetime
import threading
import pymongo
from pytz import timezone

# Set timezone
tz = timezone("US/Eastern")

url = os.getenv('DataURL')
client = pymongo.MongoClient(url)
db = client.test

# print(db.list_collection_names())

# Getting the collection
my_collection = db.coldTakes

client = discord.Client()

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]

starter_encouragements = [
    "Cheer up!",
    "Hang in there.",
    "You are a great person / bot!"
]

british_words = [
    "Fancy a cuppa?",
    "I’m knackered!",
    "Do you want to join us for a cheeky pint?",
    "I’m chuffed to bits!",
    "bloody delicious!",
    "Ohhh look at that lovely young man by the bus stop!",
    "That’s rubbish!",
    "Bugger off",
    "I haven’t seen that in donkey's years.",
    "You’ve thrown a spanner in the works.",
    "That’s manky.",
    "You’re taking the piss.",
    "I’ve dropped a clanger.",
    "maffs!",
]

roll = ["signs point to no", "has harbaugh beaten tucker?", "50/50", "try again", "ask again later", "meow", "leave me alone", "yes", "no", "never", "absolutely",
        "help me please I am being held hostage", "god will allow it", "1/10,000 odds",
        "I am not a bot. This is a cry for help", "NOOOOOOOOOO", "Yes! (;", "When pigs fly", "free me", "grant decides",
        "ask jacob", "greg has the final decision", "ben will choose your fate", "matt chooses for you",
        "max will answer this", "brock? what do you think"]


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return (quote)


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    if msg.startswith('$roll'):
        await message.channel.send(random.choice(roll))

    if msg.startswith('$british'):
        await message.channel.send(random.choice(british_words))

    if msg.startswith(
            '$cold'):  # https://www.reddit.com/r/learnpython/comments/mdpyau/how_could_i_go_about_distinguishing_between/gsaqkte/
        if message.reference.resolved:
            old_message = await message.channel.fetch_message(message.reference.message_id)
            coldTake = old_message.content
            author = old_message.author.name

            dateCold = msg.split("$cold ", 1)[1]

            my_collection.insert_one({"date": dateCold, "message": coldTake, "author": author})

            await message.channel.send("cold take recorded")

    if message.author.id == "INSERT AUTHOR NUMBER HERE":
        await message.channel.send("Hello, Master")


# Allows you to run seperate functions and put on a timer, could be useful one day
'''
async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)
    channel = client.get_channel('') 
    await channel.send("hello")

async def main():

    task1 = asyncio.create_task(
        say_after(2, 'hello'))

    task2 = asyncio.create_task(
        say_after(1, 'world'))
    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")
'''


# DONE 1. make the bot send a message once a day, while also being able to use other commands
# 2. ability to add to database
# 3. make bot send messages from database, then delete that message from database
# 4. make message get sent only on that date
# 5. make the replied to message get added to database
# https://stackoverflow.com/questions/63625246/discord-py-bot-run-function-at-specific-time-every-day
def checkTime():
    # This function runs periodically every 1 second
    threading.Timer(1, checkTime).start()

    now = datetime.now(tz)

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    if (current_time == '16:20:00'):  # check if matches with the desired time
        print('sending message')
        channel = client.get_channel("INSERT CHANNEL NUMBER HERE")
        client.loop.create_task(channel.send('Fire'))

    if (current_time == '13:00:00'):  # check if matches with the desired time
        print('colding')
        channel = client.get_channel("INSERT CHANNEL NUMBER HERE")

        # convert to date String
        today = now.strftime("%m/%d/%Y")

        # Find the document
        coldtakes = my_collection.find({"date": today})

        for take in coldtakes:
            print(take["message"])
            client.loop.create_task(channel.send("COLD TAKE?"))
            client.loop.create_task(channel.send(take["author"] + " said " + take["message"]))

        # Delete the document
        my_collection.delete_many({"date": today})


if __name__ == "__main__":
    # asyncio.run(main())
    checkTime()
    keep_alive()
    try:
        client.run(os.getenv('TOKEN'))
    except:
        os.system("kill 1")
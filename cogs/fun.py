import aiohttp, urllib.parse
from discord import Embed
from discord.ext import commands
from random import randint, choice
from datetime import datetime
import json
import requests

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_user_self(self, user_mentioned):
        bot_as_user = self.bot.user
        if (user_mentioned.name == bot_as_user.name 
        and user_mentioned.discriminator == bot_as_user.discriminator
        and user_mentioned.bot):
            return True
        else:
            return False

    def make_ban_message(self, user_mentioned):
        ban_messages = [
            f"brb, banning {user_mentioned}.",
            f"you got it, banning {user_mentioned}.",
            f"{user_mentioned}, you must pay for your crimes. A ban shall suffice.",
            f"today's controvesial opinion reward goes to {user_mentioned}. The prize? A ban, duh.",
            f"{user_mentioned} gotta ban you now. Sorry.",
            f"{user_mentioned} stop talking before you--oh, wait. Too late.",
            f"{user_mentioned}, really? I wish I could ban you more than once.",
            f"Banned: the server has automatically banned you for saying a bad word.",
            f"{user_mentioned} the game of hide and seek is over, tag, you're banned.",
        ]
        ban_easter_eggs = [
            f"{user_mentioned} I WARNED YOU ABOUT STAIRS BRO. I TOLD YOU.",
            f"Let's be honest with ourselves: we just wanted to ping {user_mentioned} twice.",
            f"{user_mentioned} has broken the unspoken rule.",
        ]
        odds = randint(1, 1000)
        if odds > 900:
            return choice(ban_easter_eggs)
        return choice(ban_messages)

    @commands.command()
    async def ping(self, ctx):
        """
        Returns pong
        """
        await ctx.send('pong')

    @commands.command()
    async def say(self, ctx, *, arg):
        """
        Says what you put
        """
        await ctx.send(arg)

    @commands.command(hidden=True)
    async def secret(self, ctx, *, arg=''):
        if(ctx.message.attachments):
            for a in ctx.message.attachments:
                await ctx.send(a.url)
        if(len(arg) > 0):
            await ctx.send(arg)
        await ctx.message.delete()

    @commands.command()
    async def escalate(self, ctx):
        await ctx.send('ESCALATING')

    @commands.command(pass_context=True)
    async def roll(self, ctx, arg1="1", arg2="100"):
        """
        You can specify the amount of dice with a space or delimited with a 'd', 
        else it will be 2 random nums between 1-6
        """
        await ctx.message.add_reaction('\U0001F3B2')
        author = ctx.message.author.mention  # use mention string to avoid pinging other people

        sum_dice = 0
        message = ""
        arg1 = str(arg1).lower()

        if ("d" in arg1):
            arg1, arg2 = arg1.split("d", 1)
            if (arg1 == ""):
                arg1 = "1"
            if (arg2 == ""):
                await ctx.send(f"Woah {author}, your rolls are too powerful")
                return

        if (not arg1.isdecimal() or not str(arg2).isdecimal()):
            await ctx.send(f"Woah {author}, your rolls are too powerful")
            return

        arg1 = int(arg1)
        arg2 = int(arg2)

        if (arg1 > 100 or arg2 > 100):
            await ctx.send(f"Woah {author}, your rolls are too powerful")
            return
        elif arg1 < 1 or arg2 < 1:
            await ctx.send(f"Woah {author}, your rolls are not powerful enough")
            return

        # Is it possible to be *too* pythonic?
        message += (
            f"{author} rolled {arg1} d{arg2}{(chr(39) + 's') if arg1 != 1 else ''}\n"
        )
        # Never.

        message += ("\n")
        for i in range(1, arg1 + 1):
            roll = randint(1, arg2)
            sum_dice += roll
            if (arg2 == 20 and roll == 20):
                message += (f"Roll {i}: {roll} - Critical Success! (20)\n")
            elif (arg2 == 20 and roll == 1):
                message += (f"Roll {i}: {roll} - Critical Failure! (1)\n")
            else:
                message += (f"Roll {i}: {roll}\n")

        message += ("\n")
        message += (f"Sum of all rolls: {sum_dice}\n")
        if (len(message) >= 2000):
            await ctx.send(f"Woah {author}, your rolls are too powerful")
        else:
            await ctx.send(message)

    @commands.command(pass_context=True)
    async def ban(self, ctx):
        """
        Bans (but not actually) the person mentioned.
        If argument is an empty string, assume it was the last person talking.
        """
        cannot_ban_bot = ctx.message.author.mention + " you can't ban me!"
        user_attempted_bot_ban = False

        mentions_list = ctx.message.mentions
        message_text = ctx.message.content

        ban_has_text = False
        if len(mentions_list) < 1 \
        and len(message_text.split(" ")) > 1:
            ban_has_text = True

        message = ""
        user_mentioned = ""

        # Check that only one user is mentioned
        if len(mentions_list) > 1:
            # Multiple user ban not allowed
            await ctx.send(ctx.message.author.mention + " woah bucko, one ban at a time, please!")
        elif len(mentions_list) == 1:
            # One user ban at a time.
            # If the user not a bot, ban them. Otherwise, special message.
            user_mentioned = mentions_list[0]
            if not self.is_user_self(user_mentioned):
                # Check that the user being banned is not a professor.
                # Get user's roles then lowercase them
                roles_raw = [i.name for i in list(user_mentioned.roles)]
                roles_lower = [i.lower() for i in roles_raw]
                # Tell users who try to ban a professor that they may not do so.
                if "professors" in roles_lower:
                    message = ctx.message.author.mention + " you can't ban a professor."
                else:
                    message = self.make_ban_message(user_mentioned.mention)
            else:
                user_attempted_bot_ban = True
                message = cannot_ban_bot
        else:
            if ban_has_text:
                # Some users apparently want to "!ban me", "!ban you", or other edge cases.
                # This is where we handle that.
                message_text = ctx.message.content[5:]
                if message_text == "me":
                    # Person executing the command wants to be banned.
                    user_mentioned = ctx.message.author.mention
                    message = self.make_ban_message(ctx.message.author.mention)
                elif message_text == "you":
                    channel = ctx.channel
                    prev_author = await channel.history(limit=2).flatten()
                    user_being_banned = prev_author[1].author
                    prev_author = prev_author[1].author.mention
                    user_mentioned = prev_author

                    if not self.is_user_self(user_being_banned):
                        message = self.make_ban_message(prev_author)
                    else:
                        user_attempted_bot_ban = True
                        message = cannot_ban_bot
                else:
                    # I guess we're just banning whatever now, then ¯\_(ツ)_/¯
                    if message_text == "charon":
                        # Unless it's the bot 🙅‍♂️
                        user_attempted_bot_ban = True
                        message = cannot_ban_bot
                    else:
                        message = self.make_ban_message(message_text)
            else:
                channel = ctx.channel
                prev_author = await channel.history(limit=2).flatten()
                user_being_banned = prev_author[1].author
                prev_author = prev_author[1].author.mention
                
                if not self.is_user_self(user_being_banned):
                    message = self.make_ban_message(prev_author)
                else:
                    user_attempted_bot_ban = True
                    message = cannot_ban_bot

        odds = randint(1, 100)
        if odds > 99 and not user_attempted_bot_ban:
            # 1 in 100 chance of getting a gif instead.
            if user_mentioned != "":
                await ctx.send(user_mentioned)
                await ctx.send("https://c.tenor.com/d0VNnBZkSUkAAAAM/bongocat-banhammer.gif")
                return
            else:
                await ctx.send(message_text)
                await ctx.send("https://c.tenor.com/d0VNnBZkSUkAAAAM/bongocat-banhammer.gif")
                return
        await ctx.send(message)
    
    @commands.command(pass_context=True)
    async def yeet(self, ctx):
        '''
        YEET
        '''
        await ctx.send(f"{ctx.message.author.mention} YEET!\nhttps://youtu.be/mbDkgGv-vJ4?t=4")
  
    @commands.command(pass_context=True)
    async def mock(self, ctx):
        """MoCk sOmEonE's StuPiD IdEa"""
        command_name = "!mock "
        message_text = ctx.message.content[len(command_name):].lower()
        mock_text = ""
        channel = ctx.channel

        argIsText = False
        mock_has_text = False
        # Shamelessly stolen from the uwu command
        if len(ctx.message.content.split(" ")) > 1:
            mock_has_text = True
            msg_id = message_text
            if(msg_id.isnumeric()):
                # arg1 is a message ID
                msg_id = int(message_text)
            elif(message_text.find('-') != -1):
                text = message_text.rsplit('-', 1)[1]
                if(text.isnumeric()):
                    # arg1 is a message ID in the form of <channelID>-<messageID>
                    msg_id = int(text)
                else:
                    argIsText = True
            elif(message_text.find('/') != -1):
                text = message_text.rsplit('/', 1)[1]
                if(text.isnumeric()):
                    # arg1 is a link to a message
                    msg_id = int(text)
                else:
                    argIsText = True
            else:
                argIsText = True

        if not mock_has_text:
            prev_message = await channel.history(limit=2).flatten()
            message_text = prev_message[1].content.lower()
        elif not argIsText:
            message_text = await channel.fetch_message(msg_id)
            message_text = message_text.content.lower()

        for i in range(0, len(message_text)):
            p = randint(0, 1)
            
            if p == 1:
                mock_text += message_text[i].upper()
                continue
            else:
                mock_text += message_text[i]

        await ctx.send(mock_text)

    @commands.command(pass_context=True)
    async def wiki(self, ctx):
        """ Gets the wikipedia article that is the closest match for the given text """
        em = Embed
        if(len(ctx.message.content.split(" ")) > 1):
            requested_article = "_".join(ctx.message.content.split()[1:]).lower() # splits and rejoins message_text into the format needed for the query
            urllib.parse.quote(requested_article)
            query = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&format=json&titles=%s' % requested_article
            async with aiohttp.ClientSession() as session:
                async with session.get(query) as response:
                    content = await response.json()
                    if(list(content['query']['pages'].keys())[0] != '-1'):
                        article = list(content['query']['pages'].values())[0] # gets the content of the article
                        article_extract = article['extract'][:article['extract'].find('\n')] # gets just the first paragraph of the article
                        if article_extract == '':
                            article_extract = 'No content returned.'
                        em = Embed(title=article['title'], description=article_extract)
                        article_url = 'https://en.wikipedia.org/wiki/%s' % requested_article
                        em.add_field(name='URL', value=article_url)
                    else:
                        em = Embed(title='No page found for %s' % requested_article)
        else:
            em = Embed(title='No page given')
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    async def catfact(self,ctx):
        """Subscribes to CatFacts!, Returns a random catfact.
        Some of these are questionable"""
        catfactsurl=["https://raw.githubusercontent.com/vadimdemedes/cat-facts/master/cat-facts.json"]
        catfactsBody = requests.get(url=choice(catfactsurl))
        if not catfactsBody.ok:
            await ctx.send(f"There seems to be some issues grabbing cat facts right now. So sorry!")
            return
        catfacts=json.loads(catfactsBody.text)
        await ctx.send("Thanks for signing up for Cat Facts! You now will recive fun daily facts about Cats! >o<")
        await ctx.send(choice(catfacts))

    @commands.command(pass_context=True)
    async def fact(self,ctx):
        """ Returns a random fact! could be true, could be false. Im not the judge of information. 
        Add to the list! https://github.com/thomasdevine01/hackbot-functions/blob/main/fact.json"""
        facturl=["https://raw.githubusercontent.com/thomasdevine01/hackbot-functions/main/fact.json"]
        factsBody = requests.get(url=choice(facturl))
        if not factsBody.ok:
            await ctx.send(f"There seems to be some issues grabbing facts right now. So sorry!")
            return
        facts=json.loads(factsBody.text)
        await ctx.send(choice(facts))
    #shamelessly stolen from mifflin. Do not persecute
    

    @commands.command()
    async def trickortreat(self,ctx):
        """ Happy Halloween! Returns trick or treat, only works during spooktober!""" 
        currentMonth = datetime.now().month
        if(currentMonth == 10):
            trickOrTreat = choice(["Trick!", "Treat"])
            if trickOrTreat == "Trick!":
                gifTrickOrTreat = choice([f"https://tenor.com/view/skull-electricity-skeleton-gif-15813803",
                                          f"https://tenor.com/view/dance-halloween-halloween-dance-trick-or-treat-jack-o-lantern-gif-5003448",
                                          f"https://tenor.com/view/motocicleta-skeleton-blue-fire-gif-13657514",
                                          f"https://tenor.com/view/skeleton-unicycle-gif-8512375",
                                          f"https://tenor.com/view/skeleton-falling-gif-27355771",
                                          f"https://tenor.com/view/skeleton-skeleton-fall-apart-skeleton-burst-pop-skeleton-exploding-gif-25434496"])
            elif trickOrTreat == "Treat":
                gifTrickOrTreat = choice([f"https://tenor.com/view/lots-of-candy-gif-26651307",
                                          f"https://tenor.com/view/halloween-happy-funny-oprah-winfrey-gif-15441089",
                                          f"https://tenor.com/view/candy-floss-kid-girl-excited-gif-5963913",
                                          f"https://tenor.com/view/sml-candy-corn-throwing-throw-halloween-gif-26482738"])

            await ctx.send(trickOrTreat)
            await ctx.send(gifTrickOrTreat)


        else:
            notOctober = choice(["it is not spooktober, try again later", "try again in october",
                                 "YOU DARE TRY TO TRICK OR TREAT WHEN IT'S NOT OCTOBER"])
            await ctx.send(notOctober)

def setup(bot):
    bot.add_cog(FunCog(bot))

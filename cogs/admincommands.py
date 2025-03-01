import json
import cogs.essentialfunctions as es
from discord.ext import commands
import discord, asyncio


class admincommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_any_role("Admins", "HM", "Developer")
    async def deleteitem(self, ctx, target: discord.User):

        await ctx.send(f"Which item do you want to delete from {target.mention}'s bag?")

        # check function for wait_for
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Try waiting for message if 60 seconds passed error comes
        try:
            msg = await self.client.wait_for('message', timeout=60, check=check)
        except asyncio.TimeoutError:
            await ctx.send('You didnt answer in time')
            return
        item = msg.content.lower()
        try:
            await es.del_item(target.id, item, 1)
        except:
            await ctx.send("Error item not found or jlfkadsöjfdf @!<442913791215140875>")

        await ctx.send(f"{item} has been successfully removed from {target.name}'s inventory!")

    @commands.command()
    @commands.has_any_role("Admins", "HM", "Developer")
    async def gift(self, ctx, winner: discord.User, money, *, moneyform="lemons"):
        user = ctx.author
        role = discord.utils.get(user.guild.roles, id=598307015181467650)
        print(role)
        print(user.roles)
        role2 = discord.utils.get(user.guild.roles, id=825532026462797835)

        users = await es.get_bank_data(winner.id)
        if moneyform == "lemons":
            mode = "pocket"
        else:
            mode = "safe"
        print(f"{user.name} gifted {winner} {money} {moneyform}")
        await es.update_balance(winner, int(money), mode=mode)
        await ctx.send(f"{winner} received {money} {moneyform}")

    @commands.has_any_role("Admins", "Developer", "HM")
    @commands.command()
    async def refill(self, ctx, item, amount=0):
        if amount == 0:
            await ctx.send("You didnt specify the amount `lem refill Mysteryskin 10` for example")
            return
        user = ctx.author
        specialitems = await es.get_item_data()
        index = -1
        exists = 0
        item = item.lower()
        for thing in specialitems:
            for specialitem in specialitems[thing]:
                print(specialitem)
                name = specialitem['name'].lower()
                stock = specialitem['stock']
                index = index + 1
                if name == item:
                    exists = 1
                    break
        if exists == 0:
            await ctx.send("That item cannot be refilled!")
            str1 = ""
            for thing in specialitems:
                for specialitem in specialitems[thing]:
                    str1 += f"{specialitem['name']}, "
            await ctx.send(f"List of items that can be refilled {str1}")
            return
        specialitems["MysterySkin"][index]["stock"] = specialitems["MysterySkin"][index]["stock"] + int(amount)
        instock = specialitems["MysterySkin"][index]["stock"]
        with open("spItems.json", "w") as f:
            json.dump(specialitems, f, indent=4)
        await ctx.send(f"There are now {instock} {name}'s in stock")

    """GETS ITEM AMOUNTS FOR A SPECIFIC ITEM AND RETURNS LIST FROM USERS ONLY FOR ADMINS"""

    @commands.has_any_role("Admins", "Developer", "HM")
    @commands.command()
    async def listitem(self, ctx, item="None"):
        if item == "None":
            await ctx.send("You didn't specify which item you want to list `lem listItem itemname`")
            return
        mysql = f'SELECT id, amount FROM items WHERE name = "{item.lower()}"'
        es.mycursor.execute(mysql)
        data = es.mycursor.fetchall()
        print(data)

        em = discord.Embed(colour=discord.Color.red(), title=f"List of users with {item}")

        for tuple in data:
            print(tuple)
            user = await self.client.fetch_user(tuple[0])
            em.add_field(name=f"name: {user}", value=f"id: {tuple[0]}\namount: {tuple[1]}", inline=False)

        await ctx.send(embed=em)

    @gift.error
    async def on_command_error(self, ctx, error):
        await ctx.send(
            f"{ctx.author.mention}\nYou need to be an Admin, in order to use this command\nIf you are a Mod, please use **lem modgift** instead\nAnd the winner **MUST** have startupped with **lem startup**")

    @refill.error
    async def on_command_error(self, ctx, error):
        await ctx.send(f"{ctx.author.mention}\nYou need to be an Admin to use this command")

    @deleteitem.error
    async def on_command_error(self, ctx, error):
        await ctx.send(
            f"{ctx.author.mention}\nYou need to be an Admin, in order to use this command\nIf you are a Mod, please use **lem moddeleteitem** instead")
        await ctx.send(error)


def setup(client):
    client.add_cog(admincommands(client))
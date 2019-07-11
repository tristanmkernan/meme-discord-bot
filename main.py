import aiohttp
import discord
import io
import os

from bs4 import BeautifulSoup


INVOCATION = "!meme "


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetch_bytes(session, url):
    async with session.get(url) as response:
        return io.BytesIO(await response.read())


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}")
        await client.change_presence(activity=discord.Game(name="SKYNET"))

    async def on_message(self, message):

        if message.content.lower().startswith(INVOCATION):
            query = message.content.lower().split(INVOCATION)[1]

            async with aiohttp.ClientSession() as session:
                html = await fetch(session, f"http://knowyourmeme.com/search?q={query}")

                soup = BeautifulSoup(html, "html.parser")
                memes_list = soup.find(class_="entry_list")

                if not memes_list:
                    await message.channel.send("No meme found!")

                    return

                meme_path = memes_list.find("a", href=True)["href"]
                meme_url = "https://knowyourmeme.com%s" % meme_path

                html = await fetch(session, meme_url)
                soup = BeautifulSoup(html, "html.parser")

                image_url = soup.find("meta", attrs={"property": "og:image"})["content"]
                buffer = await fetch_bytes(session, image_url)

                filename = f"image.{image_url.rsplit('.')[-1]}"

                await message.channel.send(file=discord.File(buffer, filename=filename))


client = MyClient()
client.run(os.environ.get("BOT_PASSWORD"))

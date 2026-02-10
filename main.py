import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Bot, Dispatcher, F


# Your bot token from BotFather
BOT_TOKEN = "8068054307:AAEXG5TTT-gxn7-eES1Ujl3q136r6tZ6_UQ"

# Create bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# This function runs when someone sends /start


@dp.message(CommandStart())
async def say_hello(message: Message):
    first_name = message.from_user.first_name
    await message.answer(f"Hello {first_name}! I'm your bot!")


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer("""/start
/help

Use these commands!
...
""")

# /start

# Start the bot


async def main():
    print("Bot has been started ...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

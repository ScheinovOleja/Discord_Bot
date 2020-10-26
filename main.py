from pprint import pprint

import discord
from settings import settings


class MyClient(discord.Client):

    def get_roles(self):
        pass

    async def emojis(self):
        pass

    async def on_ready(self):
        print('Вы вошли как {0}!'.format(self.user))

    async def on_message(self, message):
        roles = message.guild.roles
        print([role for role in roles])
        if message.author == self.user:
            return
        if message.content.startswith('/hello'):
            if message.author.id == 429782019656908812:
                # await self.add_roles(Moji, emoji='')
                await message.channel.send(f'Привет, {message.author.name}!')
        if message.content.startswith('/give'):

            pprint(message)
        print(f'Сообщение от {message.author} с канала "{message.channel}": {message.content}')

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not payload.message_id == 857927430966955024:  # ID сообщения на которое нужно ставить реакции
            return
        if not payload.emoji.id == 590075717724733845:  # или payload.emoji.name == "✔" для unicode-эмодзей
            return
        if member := payload.member:
            await member.add_roles(member.guild.get_role(785342162242088823))

    # async def give_role(self, message):
        # if not ctx.message.channel.is_private:
        #     await bot.say("Private command only")
        # server = await bot.get_Server(target_server_id)
        # role = discord.utils.get(server.roles, id=target_role_id)
        # member = server.get_member(ctx.message.author.id)
        # if member:
        #     await bot.add_roles(member, role)
        # else:
        #     await bot.say("You are not a member")


if __name__ == '__main__':
    bot = MyClient()
    bot.run(settings['token'])

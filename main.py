import discord
from discord.ext.commands import Bot

from create_db import database, InfoOnUsers, Helmets, Armours, Boots, Weapons, Mobs
from settings import settings


class RpgBot:

    def __init__(self, token):
        database.connect()
        database.create_tables([InfoOnUsers, Helmets, Armours, Boots, Weapons, Mobs])
        self.emojis = ['⚔', '😀', '😄', '😇']
        self.all_members = []
        self.roles = {}
        self.token = token
        self.bot = Bot(command_prefix='/', intents=discord.Intents.all())
        self.prepare_clients()

    def run(self):
        self.bot.run(self.token)

    def prepare_clients(self):

        async def check_to_channel(message):
            if message.channel.name == 'приветствие' and message.author != self.bot.user:
                await message.channel.purge(limit=1)
                return True

        def add_user_to_db(member):
            user_data = [{'name': member.name + member.discriminator,
                          'user_id_discord': member.id,
                          'experience': 0,
                          'money': 10,
                          'helmet': 1,
                          'armour': 1,
                          'boots': 1,
                          'weapon': 1}]
            InfoOnUsers.insert_many(user_data).execute()

        @self.bot.event
        async def on_ready():
            for role in self.bot.guilds[0].roles:
                if role.id == 768484322944352296 or role.id == 770550789345247234:
                    continue
                else:
                    self.roles[role.name] = role
            print(f'Вы вошли как {self.bot.user}!')
            print(f'Список ролей - {self.roles}')

        @self.bot.event
        async def on_member_join(member):
            check = False
            add_user_to_db(member)
            guild = member.guild
            user_id = member.id
            if guild.system_channel is not None:
                await guild.system_channel.send(f"Приветствую тебя, {member.mention}!Ты на сервере {guild.name}")
                message_bot = await guild.system_channel.send(f'Выбери свой класс!(Воин, паладин, лучник, стрелок)')
                for emoji in self.emojis:
                    await message_bot.add_reaction(emoji)
                while not check:
                    reaction, user = await self.bot.wait_for('reaction_add',
                                                             check=lambda reaction, user:
                                                             (reaction.emoji == '⚔'
                                                              or reaction.emoji == '😀'
                                                              or reaction.emoji == '😄'
                                                              or reaction.emoji == '😇')
                                                             and user.bot is False)
                    if user_id == user.id:
                        if reaction.emoji == '⚔':
                            await member.add_roles(self.roles['Воин'])
                        elif reaction.emoji == '😀':
                            await member.add_roles(self.roles['Паладин'])
                        elif reaction.emoji == '😄':
                            await member.add_roles(self.roles['Лучник'])
                        elif reaction.emoji == '😇':
                            await member.add_roles(self.roles['Стрелок'])
                        await guild.system_channel.purge(limit=50)
                        check = True
                        await guild.system_channel.send('Ждем тебя в таверне, странник!', )

        @self.bot.event
        async def on_member_remove(member):
            guild = member.guild
            if guild.system_channel is not None:
                await guild.system_channel.send(f'К сожалению нас покинул {member.mention}! Нам будет не хватать его(')
            InfoOnUsers.delete().where(InfoOnUsers.user_id_discord == member.id).execute()

        @self.bot.command(pass_context=True)
        async def hello(message):
            if await check_to_channel(message):
                return
            await message.channel.send(f'Привет, {message.author.mention}!')

        @self.bot.command(pass_context=True)
        async def clear(message):
            await message.channel.purge(limit=50)

        @self.bot.command(pass_context=True)
        async def all_members(message):
            if await check_to_channel(message):
                return
            self.all_members = self.bot.get_all_members()
            await message.channel.send(f'{[member.mention for member in self.all_members]}\n')

        @self.bot.command(pass_context=True)
        async def helped(message):
            if await check_to_channel(message):
                return
            await message.channel.send('Ээээ')

        @self.bot.command(pass_context=True)
        async def create_db(message):
            if await check_to_channel(message):
                return
            if message.author.id == settings['admin']:
                helmets_data = [{'name': 'Шлем бомжа',
                                 'power': 1,
                                 'protection': 1,
                                 'endurance': 1}]
                armours_data = [{'name': 'Броня бомжа',
                                 'power': 1,
                                 'protection': 1,
                                 'endurance': 1}]
                boots_data = [{'name': 'Ботинки бомжа',
                               'power': 1,
                               'protection': 1,
                               'endurance': 1}]
                weapons_data = [{'name': 'Палка бомжа',
                                 'power': 1,
                                 'protection': 1,
                                 'endurance': 1}]
                mobs_data = [{'location': 'Подвал',
                              'name': 'Крыса',
                              'health': 5,
                              'damage': 2,
                              'experience': 10,
                              'money': 2}]
                Helmets.insert_many(helmets_data).execute()
                Armours.insert_many(armours_data).execute()
                Boots.insert_many(boots_data).execute()
                Weapons.insert_many(weapons_data).execute()
                Mobs.insert_many(mobs_data).execute()
                await message.channel.send('Бд успешно создана')
            else:
                await message.channel.send('Ты как вообще об этой команде узнал?. Ну-ка нахер пошел отсюда!!!')

        @self.bot.command(pass_context=True)
        async def stats(message):
            if await check_to_channel(message):
                return
            try:
                data = InfoOnUsers.get(InfoOnUsers.user_id_discord == message.author.id)
                await message.channel.send(f'{data}')
            except Exception as exc:
                await message.channel.send(f'Произошла неизвестная ошибка! Обратитесь к Админу!\n{exc}')

        @self.bot.command(pass_context=True)
        async def add_all_to_db(message):
            if await check_to_channel(message):
                return
            for user in message.guild.members:
                if user.bot:
                    continue
                else:
                    user_data = [{'name': user.name + user.discriminator,
                                  'user_id_discord': user.id,
                                  'experience': 0,
                                  'money': 10,
                                  'helmet': 1,
                                  'armour': 1,
                                  'boots': 1,
                                  'weapon': 1}]
                    InfoOnUsers.insert_many(user_data).execute()

        @self.bot.command(pass_context=True)
        async def mobs(message):
            user = message.author
            await user.send('Дарова! Вот список мобов в данной локации - ...')


if __name__ == "__main__":
    bot = RpgBot(settings['token'])
    bot.run()

import asyncio as asyncio
import discord
from discord.ext.commands import Bot
from equipments import helmets, armours, boots, weapons, bracers
from mobs import mobs
from create_db import database, InfoOnUsers, Helmets, Armours, Bracers, Boots, Weapons, Mobs
from settings import settings


class RpgBot:

    def __init__(self, token):
        database.connect()
        database.create_tables([InfoOnUsers, Helmets, Armours, Bracers, Boots, Weapons, Mobs])
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
                Helmets.insert_many(helmets).execute()
                Armours.insert_many(armours).execute()
                Bracers.insert_many(bracers).execute()
                Boots.insert_many(boots).execute()
                Weapons.insert_many(weapons).execute()
                Mobs.insert_many(mobs).execute()
                await message.channel.send(f'Бд успешно создана')
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
                                  'health': 100,
                                  'experience': 0,
                                  'money': 10,
                                  'healing_potion': 1,
                                  'helmet': 1,
                                  'armour': 1,
                                  'bracer': 1,
                                  'boots': 1,
                                  'weapon': 1}]
                    InfoOnUsers.insert_many(user_data).execute()
                await message.channel.send('Пользователи успешно добавлены в БД.')

        async def user_damage_calc(user):
            for info in InfoOnUsers.select().where(InfoOnUsers.user_id_discord == user.id):
                damage_armour = info.armour.power
                damage_boots = info.boots.power
                damage_bracers = info.bracer.power
                damage_helmets = info.helmet.power
                damage_weapons = info.weapon.power
                total_damage = sum([damage_armour, damage_boots, damage_helmets, damage_bracers, damage_weapons])
                return total_damage

        async def calc_exp_money(user, mob):
            exp_money = InfoOnUsers.get(InfoOnUsers.user_id_discord == user.id)
            exp_money.experience += mob["experience"]
            exp_money.money += mob["money"]
            exp_money.save()

        async def battle(message, user, mob):
            await user.send(f'Начинается сражение с мобом - {message.content}\n'
                            f'У вас есть 5 секунд, чтобы атаковать в полную силу, иначе пройдет только половина урона')
            user_damage = await user_damage_calc(user)
            user_stats = InfoOnUsers.get(InfoOnUsers.user_id_discord == user.id)
            while not mob['health'] <= 0:
                fight = await user.send(f'БЕЙ!!!!! У {mob["name"]} всего {mob["health"]} здоровья')
                await fight.add_reaction('⚔')

                def check_reaction(reaction, user):
                    return user == message.author and str(reaction.emoji) == '⚔'

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=5.0, check=check_reaction)
                except asyncio.TimeoutError:
                    await user.send(
                        f'Ты чего мешкаешь!? {mob["name"]} бьет и наносит {mob["damage"]}. '
                        f'У тебя осталось {user_stats.health} здоровья')
                    user_stats.health -= mob["damage"]
                    user_stats.save()
                else:
                    mob['health'] -= user_damage
                    await user.send(f'Нанесен полный урон в размере {user_damage}')
                if mob['health'] <= 0:
                    break
                else:
                    user_stats.health -= mob["damage"]
                    await user.send(f'{mob["name"]} бьет и наносит {mob["damage"]}. '
                                    f'У тебя осталось {user_stats.health} здоровья')
                    user_stats.save()
            await calc_exp_money(user, mob)
            await user.send(
                f'Поздравляю, вы победили моба и получили {mob["experience"]} - опыта и {mob["money"]} монет!\n'
                f'Для повторения боя заново введите команду "/mob" в локации, либо же здесь введите команду '
                f'"/mob (название локации)"'
            )

        @self.bot.command(pass_context=True)
        async def fight(message, location=None):
            if location is None:
                location = message.channel.name
            user = message.author
            mobs = []
            await user.send(
                f'Дарова! Вот список мобов в локации "{location}" :')
            for moby in Mobs.select().where(Mobs.location == location.lower()):
                await user.send(
                    f'Моб - {moby.name}, \n'
                    f'Здоровье - {moby.health}, \n'
                    f'Дамаг - {moby.damage}, \n'
                    f'Опыт за убийство - {moby.experience}, \n'
                    f'Золота за убийство - {moby.money}, \n'
                    '==============================================='
                )
                mobs.append(moby.name)
            await user.send('Выбирай моба(просто введи его имя)')

            def check_msg(msg):
                for mob in Mobs.select():
                    if msg.content.lower() == mob.name:
                        return msg.content.lower() == mob.name

            m = await self.bot.wait_for('message', check=check_msg)
            for bei in Mobs.select().where(Mobs.name == m.content.lower()):
                being = {
                    'name': bei.name,
                    'health': bei.health,
                    'damage': bei.damage,
                    'experience': bei.experience,
                    'money': bei.money,
                }
            if m:
                await battle(m, user, being)

        @self.bot.command(pass_context=True)
        async def heal(message):
            healing = InfoOnUsers.get(InfoOnUsers.user_id_discord == message.author.id)
            if healing.healing_potion == 0:
                await message.channel.send('Хилок нет, иди в жопу')
            else:
                healing.healing_potion -= 1
                healing.health = 100
                healing.save()
                await message.channel.send('Ну теперь ты полон сил, поздравляю!')


if __name__ == "__main__":
    bot = RpgBot(settings['token'])
    bot.run()

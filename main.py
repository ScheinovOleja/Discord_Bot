import asyncio as asyncio
import discord
from discord.ext.commands import Bot
from equipments import initial_equipment
from mobs import mobs
from create_db import database, InfoOnUsers, Helmets, Armours, Bracers, Boots, Weapons, Mobs, Stats
from settings import settings


class RpgBot:

    def __init__(self, token):
        database.connect()
        database.create_tables([InfoOnUsers, Stats, Helmets, Armours, Bracers, Boots, Weapons, Mobs])
        self.emojis = ['⚔', '😀', '😄', '😇']
        self.location =['подвал', 'равнины']
        self.all_members = []
        self.roles = {}
        self.token = token
        self.bot = Bot(command_prefix='/', intents=discord.Intents.all())
        self.prepare_clients()

    def run(self):
        self.bot.run(self.token)

    def prepare_clients(self):

        async def add_class():
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     check=lambda reaction, user:
                                                     (reaction.emoji == '⚔'
                                                      or reaction.emoji == '😀'
                                                      or reaction.emoji == '😄'
                                                      or reaction.emoji == '😇')
                                                     and user.bot is False)
            if reaction.emoji == '⚔':
                await user.add_roles(self.roles['Воин'])
            elif reaction.emoji == '😀':
                await user.add_roles(self.roles['Паладин'])
            elif reaction.emoji == '😄':
                await user.add_roles(self.roles['Лучник'])
            elif reaction.emoji == '😇':
                await user.add_roles(self.roles['Стрелок'])
            else:
                return False
            return True

        @self.bot.command(pass_context=True)
        async def me_class(message):
            if len(message.author.roles) < 2:
                message_bot = await message.channel.send(f'Выбери свой класс!(Воин, паладин, лучник, стрелок)')
                for emoji in self.emojis:
                    await message_bot.add_reaction(emoji)
                if await add_class():
                    await message.channel.purge(limit=3)
                    return
            else:
                await message.channel.send("У тебя уже есть класс, дурак!")
                return

        async def check_to_greeting(message):
            try:
                if message.channel == message.guild.system_channel and message.author != self.bot.user:
                    await message.channel.purge(limit=2)
                    return True
            except Exception as exc:
                print(f'Произошла ошибка - {exc}')

        async def check_to_private(message):
            if message.channel.type.name == 'private' and message.author != self.bot.user:
                return True

        def user_data(member):
            data = {'name': member.name + member.discriminator,
                    'user_id_discord': member.id,
                    'stats': member.id,
                    'helmet': 1,
                    'armour': 1,
                    'bracer': 1,
                    'boots': 1,
                    'weapon': 1}
            stat = {
                'user_id': member.id,
            }

            return data, stat

        async def insert_to_db(member):
            data, stat = user_data(member)
            Stats.insert_many(stat).execute()
            InfoOnUsers.insert_many(data).execute()

        async def add_user_to_db(member):
            await insert_to_db(member)
            health = await user_characteristics_calc(user=member, endurance=True)
            user_dating = InfoOnUsers.get(InfoOnUsers.user_id_discord == member.id)
            user_dating.health, user_dating.max_health = health, health
            user_dating.save()

        @self.bot.event
        async def on_ready():
            for role in self.bot.guilds[0].roles:
                if role.id == 768484322944352296 or role.id == 775279022715830273:
                    continue
                else:
                    self.roles[role.name] = role
            print(f'Вы вошли как {self.bot.user}!')
            print(f'Список ролей - {self.roles}')

        @self.bot.event
        async def on_member_join(member):
            check = False
            await add_user_to_db(member)
            guild = member.guild
            if guild.system_channel is not None:
                await guild.system_channel.send(f"Приветствую тебя, {member.mention}!Ты на сервере {guild.name}")
                message_bot = await guild.system_channel.send(f'Выбери свой класс!(Воин, паладин, лучник, стрелок)')
                for emoji in self.emojis:
                    await message_bot.add_reaction(emoji)
                while not check:
                    if await add_class():
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
        async def clear(message):
            if message.author.id == settings['admin']:
                await message.channel.purge(limit=50)

        @self.bot.command(pass_context=True)
        async def create_db(message):
            if await check_to_greeting(message):
                return
            if message.author.id == settings['admin']:
                Helmets.insert_many(initial_equipment['helmets']).execute()
                Armours.insert_many(initial_equipment['armours']).execute()
                Bracers.insert_many(initial_equipment['bracers']).execute()
                Boots.insert_many(initial_equipment['boots']).execute()
                Weapons.insert_many(initial_equipment['weapons']).execute()
                Mobs.insert_many(mobs).execute()
                await message.channel.send(f'Бд успешно создана')
            else:
                await message.channel.send('Ты как вообще об этой команде узнал?. Ну-ка нахер пошел отсюда!!!')

        @self.bot.command(pass_context=True)
        async def stats(message):
            if await check_to_greeting(message):
                return
            if await check_to_private(message):
                sender = message.author
            else:
                sender = message.channel
            try:
                data = InfoOnUsers.get(InfoOnUsers.user_id_discord == message.author.id)
                stat = Stats.get(Stats.user_id == message.author.id)
                await sender.send(f'{data}\n{stat}')
            except Exception as exc:
                await sender.send(f'Произошла неизвестная ошибка! Обратитесь к Админу!\n{exc}')

        @self.bot.command(pass_context=True)
        async def add_all_to_db(message):
            if await check_to_greeting(message):
                return
            for user in self.bot.users:
                if user.bot:
                    continue
                else:
                    await insert_to_db(user)
                    health = await user_characteristics_calc(user=user, endurance=True)
                    user_from_db = InfoOnUsers.get(InfoOnUsers.user_id_discord == user.id)
                    user_from_db.health, user_from_db.max_health = health, health
                    user_from_db.save()
            await message.channel.send('Пользователи успешно добавлены в БД.')

        async def user_characteristics_calc(user, power=None, protect=None, endurance=None):
            info = InfoOnUsers.get(InfoOnUsers.user_id_discord == user.id)
            stat = Stats.get(Stats.user_id == user.id)
            total_damage = 0
            total_protection = 0
            total_endurance = 0
            if power:
                total_damage = sum(
                    [
                        info.armour.power,
                        info.boots.power,
                        info.helmet.power,
                        info.bracer.power,
                        info.weapon.power,
                        stat.power,
                    ]
                )
            if protect:
                total_protection = sum(
                    [
                        info.armour.protection,
                        info.boots.protection,
                        info.bracer.protection,
                        info.helmet.protection,
                        info.weapon.protection,
                        stat.protection,
                    ]
                )
            if endurance:
                total_endurance = sum(
                    [
                        info.armour.endurance,
                        info.boots.endurance,
                        info.bracer.endurance,
                        info.helmet.endurance,
                        info.weapon.endurance,
                        stat.endurance,
                    ]
                )
            if total_damage:
                return total_damage
            elif total_protection:
                return total_protection / 100
            elif total_endurance:
                return total_endurance * 25

        async def calc_exp_money(user, mob):
            exp_money = InfoOnUsers.get(InfoOnUsers.user_id_discord == user.id)
            exp_money.experience += mob["experience"]
            exp_money.money += mob["money"]
            exp_money.save()

        async def battle(message, user, mob, user_stats):
            await user.send(f'Начинается сражение с мобом - {message.content}\n'
                            f'У вас есть 5 секунд, чтобы атаковать в полную силу, иначе пройдет только половина урона')
            mob_damage = mob['damage'] - mob['damage'] * await user_characteristics_calc(user, protect=True)
            user_damage = await user_characteristics_calc(user, power=True)
            while not mob['health'] <= 0:
                combat = await user.send(f'БЕЙ!!!!! У {mob["name"]} всего {mob["health"]} здоровья')
                await combat.add_reaction('⚔')

                def check_reaction(reaction, user):
                    return user == message.author and str(reaction.emoji) == '⚔'

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=5.0, check=check_reaction)
                except asyncio.TimeoutError:
                    await user.send(
                        f'Ты чего мешкаешь!? {mob["name"]} бьет и наносит {mob_damage} с учетом твоей брони. '
                        f'У тебя осталось {user_stats.health} здоровья')
                    user_stats.health -= mob_damage
                    user_stats.save()
                else:
                    mob['health'] -= user_damage
                    await user.send(f'Нанесен полный урон в размере {user_damage}')
                if mob['health'] <= 0:
                    break
                else:
                    user_stats.health -= mob_damage
                    await user.send(f'{mob["name"]} бьет и наносит {mob_damage} с учетом твоей брони. '
                                    f'У тебя осталось {user_stats.health} здоровья')
                    user_stats.save()
            else:
                await user.send("Извини, но ты мерт физически и морально. Отдохни или выпей хилку.")
                return
            await calc_exp_money(user, mob)
            await user.send(
                f'Поздравляю, вы победили моба и получили {mob["experience"]} - опыта и {mob["money"]} монет!\n'
                f'Для повторения боя заново введите команду "/fight" в локации, либо же здесь введите команду '
                f'"/fight (название локации)"'
            )

        @self.bot.command(pass_context=True)
        async def fight(message, location=None):
            user_stats = InfoOnUsers.get(InfoOnUsers.user_id_discord == message.author.id)
            if user_stats.health <= 0:
                await message.author.send("Извини, но ты мерт физически и морально. Отдохни или выпей хилку.")
                return
            if location is None:
                location = message.channel.name
            user = message.author
            mobs_name_list = []
            await user.send(
                f'Дарова! Вот список мобов в локации "{location}" :')
            for moby in Mobs.select().where(Mobs.location == location.lower() and Mobs.boss == 0):
                await user.send(
                    f'Моб - {moby.name}, \n'
                    f'Здоровье - {moby.health}, \n'
                    f'Дамаг - {moby.damage}, \n'
                    f'Опыт за убийство - {moby.experience}, \n'
                    f'Золота за убийство - {moby.money}, \n'
                    '==============================================='
                )
                mobs_name_list.append(moby.name)
            await user.send('Выбирай моба(просто введи его имя)')

            def check_msg(msg):
                for mob in Mobs.select():
                    if msg.content.lower() == mob.name:
                        return msg.content.lower() == mob.name

            m = await self.bot.wait_for('message', check=check_msg)
            being = {}
            for bei in Mobs.select().where(Mobs.name == m.content.lower()):
                being = {
                    'name': bei.name,
                    'health': bei.health,
                    'damage': bei.damage,
                    'experience': bei.experience,
                    'money': bei.money,
                }
            if m:
                await battle(message=m, user=user, mob=being, user_stats=user_stats)

        @self.bot.command(pass_context=True)
        async def heal(message):
            if await check_to_greeting(message):
                return
            if await check_to_private(message):
                sender = message.author
            else:
                sender = message.channel
            healing = InfoOnUsers.get(InfoOnUsers.user_id_discord == message.author.id)
            if healing.healing_potion == 0:
                await sender.send('Хилок нет, иди в жопу')
            else:
                healing.healing_potion -= 1
                healing.health += 500
                if healing.health > healing.max_health:
                    healing.health = healing.max_health
                healing.save()
                await sender.send('Ну теперь ты полон сил, поздравляю!')

        @self.bot.command(pass_context=True)
        async def boss(message):
            pass

        @self.bot.command(pass_context=True)
        async def commands(ctx):
            await ctx.channel.purge(limit=1)
            emb = discord.Embed(colour=discord.Color.blue(), title='Комманды')
            emb.add_field(name='commands', value='Команда для просмотра пользовательских комманд!')
            emb.add_field(name='fight', value='Команда для боя, используется в нужной локации!')
            emb.add_field(name='stats', value='Команда для просмотра своих статов и инвентаря')
            emb.add_field(name='heal', value='Команда для выхиливания до фулла')
            emb.add_field(name='me_class',
                          value='Команда для присвоения себе класса(используется 1 раз при отсутствии класса)!')
            emb.set_footer(text='Примеры выполнения => /stats')
            await ctx.send(embed=emb)

        async def user_health_update(user):
            health = await user_characteristics_calc(user=user, endurance=True)
            user_from_db = InfoOnUsers.get(InfoOnUsers.user_id_discord == user.id)
            user_from_db.max_health = health
            user_from_db.save()

        async def user_stats_update(user, sender):
            if user.experience >= 240 * (2 ** user.factor):
                stat = Stats.get(Stats.user_id == user.stats_id)
                stat.power += 1
                stat.endurance += 1
                stat.protection += 1
                stat.save()
                user.level += 1
                user.factor += 1
                user.save()
                await sender.send(f'Поздравляю, ты перешел на уровень {user.level}!')

        @self.bot.command(pass_context=True)
        async def shop(message):
            if message.channel.name == 'магазин':
                pass

        @self.bot.event
        async def on_message(message):
            await asyncio.sleep(1)
            await self.bot.process_commands(message)
            if await check_to_private(message):
                sender = message.author
            else:
                sender = message.channel
            for user in self.bot.users:
                if user.bot:
                    continue
                else:
                    try:
                        await user_health_update(user)
                    except Exception as exc:
                        print(exc)
            for user in InfoOnUsers.select():
                try:
                    await user_stats_update(user, sender)
                except Exception as exc:
                    print(exc)


if __name__ == "__main__":
    bot = RpgBot(settings['token'])
    bot.run()

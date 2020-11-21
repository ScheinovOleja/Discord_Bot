import peewee as pw

database = pw.SqliteDatabase('RPGDataBase.db', pragmas={'foreign_keys': 4})


class Table(pw.Model):
    class Meta:
        database = database


class Helmets(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Шлем бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)
    price = pw.IntegerField(default=100)

    def __str__(self):
        return f'{self.name}'


class Armours(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Броня бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)
    price = pw.IntegerField(default=100)

    def __str__(self):
        return f'{self.name}'


class Bracers(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Перчатки бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)
    price = pw.IntegerField(default=100)

    def __str__(self):
        return f'{self.name}'


class Boots(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Ботинки бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)
    price = pw.IntegerField(default=100)

    def __str__(self):
        return f'{self.name}'


class Weapons(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Палка бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)
    price = pw.IntegerField(default=100)

    def __str__(self):
        return f'{self.name}'


class Stats(Table):
    user_id = pw.CharField(max_length=20, unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)

    def __str__(self):
        return f'Сила - {self.power}\n' \
               f'Защита - {self.protection}\n' \
               f'Выносливость - {self.endurance}\n'


class InfoOnUsers(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=30)
    user_id_discord = pw.CharField(max_length=20, unique=True)
    health = pw.IntegerField(default=150)
    max_health = pw.IntegerField(default=0)
    experience = pw.IntegerField(default=0)
    money = pw.IntegerField(default=0)
    healing_potion = pw.IntegerField(default=5)
    level = pw.IntegerField(default=1)
    factor = pw.IntegerField(default=0)
    time_for_dead = pw.DateTimeField(null=True)
    stats = pw.ForeignKeyField(Stats, related_name='Характеристики', to_field='user_id', on_delete='cascade',
                               on_update='cascade')
    helmet = pw.ForeignKeyField(Helmets, related_name='Шлем', to_field='id', on_delete='cascade', on_update='cascade')
    armour = pw.ForeignKeyField(Armours, related_name='Броня', to_field='id', on_delete='cascade', on_update='cascade')
    bracer = pw.ForeignKeyField(Bracers, related_name='Перчатки', to_field='id', on_delete='cascade',
                                on_update='cascade')
    boots = pw.ForeignKeyField(Boots, related_name='Ботинки', to_field='id', on_delete='cascade', on_update='cascade')
    weapon = pw.ForeignKeyField(Weapons, related_name='Оружие', to_field='id', on_delete='cascade', on_update='cascade')

    def __str__(self):
        return f'Имя - {self.name}\n' \
               f'Здоровье - {self.health}|{self.max_health}\n' \
               f'Опыт - {self.experience}|{240 * (2 ** self.factor)}\n' \
               f'Монеты - {self.money}\n' \
               f'Хилок - {self.healing_potion}\n' \
               f'Уровень - {self.level}\n' \
               f'Шлем - {self.helmet}\n' \
               f'Броня - {self.armour}\n' \
               f'Перчатки - {self.bracer}\n' \
               f'Ботинки - {self.boots}\n' \
               f'Оружие - {self.weapon}\n'


class Mobs(Table):
    id = pw.PrimaryKeyField(null=False)
    location = pw.CharField(max_length=30)
    name = pw.CharField(max_length=30)
    health = pw.IntegerField(default=0)
    damage = pw.IntegerField(default=0)
    experience = pw.IntegerField(default=0)
    money = pw.IntegerField(default=0)
    boss = pw.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class Boss(Table):
    id = pw.PrimaryKeyField(null=False)
    location = pw.CharField(max_length=30)
    name = pw.CharField(max_length=30)
    health = pw.IntegerField(default=0)
    damage = pw.IntegerField(default=0)
    experience = pw.IntegerField(default=0)
    money = pw.IntegerField(default=0)

    def __str__(self):
        return f'{self.name}'

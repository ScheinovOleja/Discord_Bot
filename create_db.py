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

    def __str__(self):
        return f'{self.name}'


class Armours(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Броня бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)

    def __str__(self):
        return f'{self.name}'


class Boots(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Ботинки бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)

    def __str__(self):
        return f'{self.name}'


class Weapons(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20, default='Палка бомжа', unique=True)
    power = pw.IntegerField(default=1)
    protection = pw.IntegerField(default=1)
    endurance = pw.IntegerField(default=1)

    def __str__(self):
        return f'{self.name}'


class InfoOnUsers(Table):
    id = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=30)
    user_id_discord = pw.CharField(max_length=20, unique=True)
    experience = pw.IntegerField(default=0)
    money = pw.IntegerField(default=0)
    helmet = pw.ForeignKeyField(Helmets, related_name='Шлем', to_field='id', on_delete='cascade', on_update='cascade')
    armour = pw.ForeignKeyField(Armours, related_name='Броня', to_field='id', on_delete='cascade', on_update='cascade')
    boots = pw.ForeignKeyField(Boots, related_name='Ботинки', to_field='id', on_delete='cascade', on_update='cascade')
    weapon = pw.ForeignKeyField(Weapons, related_name='Оружие', to_field='id', on_delete='cascade', on_update='cascade')

    def __str__(self):
        return f'Имя - {self.name}\n' \
               f'Опыт - {self.experience}\n' \
               f'Монеты - {self.money}\n' \
               f'Шлем - {self.helmet}\n' \
               f'Броня - {self.armour}\n' \
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

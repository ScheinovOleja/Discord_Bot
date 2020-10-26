import peewee as pw

database = pw.SqliteDatabase('RPGDataBase.db', pragmas={'foreign_keys': 1})


class Table(pw.Model):
    class Meta:
        database = database


class Helmets(Table):
    name = pw.CharField(max_length=20)
    power = pw.IntegerField()
    protection = pw.IntegerField()
    endurance = pw.IntegerField()


class Armours(Table):
    name = pw.CharField(max_length=20)
    power = pw.IntegerField()
    protection = pw.IntegerField()
    endurance = pw.IntegerField()


class Boots(Table):
    name = pw.CharField(max_length=20)
    power = pw.IntegerField()
    protection = pw.IntegerField()
    endurance = pw.IntegerField()


class Weapons(Table):
    name = pw.CharField(max_length=20)
    power = pw.IntegerField()
    protection = pw.IntegerField()
    endurance = pw.IntegerField()


class Equipments(Table):
    helmet = pw.ForeignKeyField(Helmets, verbose_name='Шлем')
    armour = pw.ForeignKeyField(Armours, verbose_name='Броня')
    boots = pw.ForeignKeyField(Boots, verbose_name='Ботинки')
    weapon = pw.ForeignKeyField(Weapons, verbose_name='Оружие')


class InfoOnUsers(Table):
    id_user = pw.PrimaryKeyField(null=False)
    name = pw.CharField(max_length=20)
    experience = pw.IntegerField()
    money = pw.FloatField()
    equipments = pw.ForeignKeyField(Equipments, unique=True)


database.connect()
database.create_tables([Equipments, InfoOnUsers, Helmets, Armours, Boots, Weapons])

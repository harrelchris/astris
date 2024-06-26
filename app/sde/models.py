from django.db import models


class Hash(models.Model):
    value = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.date.isoformat()

    def is_current(self, remote_hash: str) -> bool:
        return self.value == remote_hash

    def update_hash(self, remote_hash: str):
        self.value = remote_hash
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class MarketGroup(models.Model):
    parent = models.ForeignKey("MarketGroup", null=True, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=256)
    volume = models.FloatField()
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    market_group = models.ForeignKey(MarketGroup, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class MetaGroup(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class MetaType(models.Model):
    type = models.ForeignKey(Type, on_delete=models.DO_NOTHING)
    parent = models.ForeignKey("MetaType", null=True, on_delete=models.DO_NOTHING)
    meta_group = models.ForeignKey(MetaGroup, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.type.name} - {self.meta_group.name}"

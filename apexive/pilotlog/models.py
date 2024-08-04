from django.db import models


class Row(models.Model):
    hash = models.CharField(max_length=64, unique=True, null=True)
    table = models.CharField(max_length=64, unique=False, null=True)

    def __str__(self):
        return f'{self.pk}'


class Attribute(models.Model):
    name = models.CharField(max_length=255)
    row = models.ForeignKey(Row, related_name="rows", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Atribute {self.name} for {self.row}'


class ChildAttribute(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    row = models.ForeignKey(Row, related_name="ch_a_rows", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'It is a Child {self.name}'


class AttributeValue(models.Model):
    row = models.ForeignKey(Row, related_name="row", on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, related_name="attribute", on_delete=models.CASCADE, null=True, blank=True)
    child_attribute = models.ForeignKey(
        ChildAttribute, related_name="child_attribute", on_delete=models.CASCADE, null=True, blank=True
    )
    value = models.CharField(max_length=2000)

    def __str__(self):
        return f'{self.row.pk} - {self.attribute.name}: {self.value}'

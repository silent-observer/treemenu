# Generated by Django 5.0.1 on 2024-02-01 13:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemenuapp', '0002_alter_menunode_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menunode',
            old_name='containing_menu',
            new_name='menu',
        ),
        migrations.AlterField(
            model_name='menu',
            name='root',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='treemenuapp.menunode', verbose_name='Root item'),
        ),
    ]
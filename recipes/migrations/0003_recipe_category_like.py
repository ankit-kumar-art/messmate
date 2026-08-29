# Generated for MessMate feature update

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_profile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='category',
            field=models.CharField(
                choices=[
                    ('breakfast', 'Breakfast'),
                    ('lunch', 'Lunch'),
                    ('dinner', 'Dinner'),
                    ('snacks', 'Snacks & Quick Bites'),
                ],
                default='dinner',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='recipes.recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_recipes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'recipe')},
            },
        ),
    ]

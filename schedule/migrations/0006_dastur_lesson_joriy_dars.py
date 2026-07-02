from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_botxabar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dastur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fan', models.CharField(choices=[('IT', 'IT'), ('AI', "Sun'iy intellekt"), ('FE', 'Frontend')], max_length=5)),
                ('dars_raqami', models.PositiveIntegerField()),
                ('sarlavha', models.TextField()),
            ],
            options={
                'ordering': ['fan', 'dars_raqami'],
                'unique_together': {('fan', 'dars_raqami')},
            },
        ),
        migrations.AddField(
            model_name='lesson',
            name='joriy_dars',
            field=models.PositiveIntegerField(default=1, verbose_name='Joriy dars raqami'),
        ),
    ]

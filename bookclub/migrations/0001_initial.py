# Generated by Django 3.2.11 on 2022-01-29 07:40

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import isbn_field.fields
import isbn_field.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('age', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('city', models.CharField(blank=True, max_length=50)),
                ('region', models.CharField(blank=True, max_length=50)),
                ('country', models.CharField(blank=True, max_length=50)),
                ('bio', models.CharField(blank=True, max_length=300)),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('theme', models.CharField(blank=True, max_length=100)),
                ('meeting_type', models.CharField(choices=[('IP', 'In-person'), ('OL', 'Online')], default='IP', max_length=2)),
                ('city', models.CharField(blank=True, max_length=50)),
                ('country', models.CharField(blank=True, max_length=50)),
                ('members', models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ISBN', isbn_field.fields.ISBNField(max_length=28, unique=True, validators=[isbn_field.validators.ISBNValidator], verbose_name='ISBN')),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('publisher', models.CharField(blank=True, max_length=100)),
                ('image_url', models.URLField(blank=True)),
                ('year', models.PositiveIntegerField(blank=True, default=2022, validators=[django.core.validators.MaxValueValidator(2022), django.core.validators.MinValueValidator(1)])),
                ('readers', models.ManyToManyField(related_name='readers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='books',
            field=models.ManyToManyField(related_name='books', to='bookclub.Book'),
        ),
        migrations.AddField(
            model_name='user',
            name='clubs',
            field=models.ManyToManyField(blank=True, to='bookclub.Club'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]

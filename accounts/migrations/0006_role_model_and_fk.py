from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    User = apps.get_model("accounts", "User")
    RoleModulePermission = apps.get_model("accounts", "RoleModulePermission")

    default_roles = {
        "EXAM_OFFICER": "Examination Officer",
        "DEPT_CONTROLLER": "Department Exam Controller",
        "INTERNAL_EXAM_CONTROLLER": "Department Internal Exam Controller",
        "STUDENT": "Student",
    }

    existing_codes = set(
        User.objects.exclude(role__isnull=True).values_list("role", flat=True)
    ) | set(
        RoleModulePermission.objects.exclude(role__isnull=True).values_list("role", flat=True)
    )
    if not existing_codes:
        existing_codes = set(default_roles.keys())

    for code in existing_codes:
        name = default_roles.get(code, code.replace("_", " ").title())
        Role.objects.get_or_create(
            code=code,
            defaults={"name": name, "is_system": code in default_roles, "is_active": True},
        )

    for user in User.objects.all():
        role_obj = Role.objects.filter(code=user.role).first()
        user.role_ref = role_obj
        user.save(update_fields=["role_ref"])

    for perm in RoleModulePermission.objects.all():
        role_obj = Role.objects.filter(code=perm.role).first()
        perm.role_ref = role_obj
        perm.save(update_fields=["role_ref"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_user_is_locked"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("is_system", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="user",
            name="role_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="accounts.role",
            ),
        ),
        migrations.AddField(
            model_name="rolemodulepermission",
            name="role_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="permissions",
                to="accounts.role",
            ),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name="rolemodulepermission",
            unique_together=set(),
        ),
        migrations.RemoveField(model_name="user", name="role"),
        migrations.RemoveField(model_name="rolemodulepermission", name="role"),
        migrations.RenameField(model_name="user", old_name="role_ref", new_name="role"),
        migrations.RenameField(model_name="rolemodulepermission", old_name="role_ref", new_name="role"),
        migrations.AlterField(
            model_name="rolemodulepermission",
            name="role",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="permissions", to="accounts.role"),
        ),
    ]

from django.db import migrations


def forwards(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    User = apps.get_model("accounts", "User")
    Group = apps.get_model("auth", "Group")
    UserGroups = apps.get_model("accounts", "User_groups")

    role_to_group = {}
    for role in Role.objects.all():
        group, _ = Group.objects.get_or_create(name=role.code)
        role_to_group[role.id] = group

    for user in User.objects.all():
        if user.role_id and user.role_id in role_to_group:
            group = role_to_group[user.role_id]
            UserGroups.objects.get_or_create(user_id=user.id, group_id=group.id)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_role_model_and_fk"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(model_name="user", name="role"),
        migrations.DeleteModel(name="RoleModulePermission"),
        migrations.DeleteModel(name="Role"),
    ]

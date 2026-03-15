from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed default users (exam officer, department controller, student)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="password123",
            help="Password for seeded users (default: password123)",
        )
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Reset password if user already exists",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        password = options["password"]
        reset_password = options["reset_password"]

        seed = [
            {"username": "exam_officer", "role": "EXAM_OFFICER"},
            {"username": "dept_controller", "role": "DEPT_CONTROLLER"},
            {"username": "student_user", "role": "STUDENT"},
        ]

        created = 0
        updated = 0

        from accounts.permissions import ensure_default_groups
        from django.contrib.auth.models import Group

        ensure_default_groups()

        for item in seed:
            user, was_created = User.objects.get_or_create(
                username=item["username"],
                defaults={},
            )
            if was_created:
                user.set_password(password)
                user.save(update_fields=["password"])
                group = Group.objects.filter(name=item["role"]).first()
                if group:
                    user.groups.add(group)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created {user.username}"))
            else:
                changed = False
                group = Group.objects.filter(name=item["role"]).first()
                if group and not user.groups.filter(id=group.id).exists():
                    user.groups.add(group)
                    changed = True
                if reset_password:
                    user.set_password(password)
                    changed = True
                if changed:
                    user.save()
                    updated += 1
                    self.stdout.write(self.style.WARNING(f"Updated {user.username}"))
                else:
                    self.stdout.write(f"Skipped {user.username} (already exists)")

        self.stdout.write(self.style.NOTICE(f"Done. Created: {created}, Updated: {updated}"))

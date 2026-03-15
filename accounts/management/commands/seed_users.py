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
            {"username": "internal_exam_controller", "role": "INTERNAL_EXAM_CONTROLLER"},
            {"username": "student_user", "role": "STUDENT"},
        ]

        created = 0
        updated = 0

        for item in seed:
            user, was_created = User.objects.get_or_create(
                username=item["username"],
                defaults={"role": item["role"]},
            )
            if was_created:
                user.set_password(password)
                user.save(update_fields=["password"])
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created {user.username} ({user.role})"))
            else:
                changed = False
                if user.role != item["role"]:
                    user.role = item["role"]
                    changed = True
                if reset_password:
                    user.set_password(password)
                    changed = True
                if changed:
                    user.save()
                    updated += 1
                    self.stdout.write(self.style.WARNING(f"Updated {user.username} ({user.role})"))
                else:
                    self.stdout.write(f"Skipped {user.username} (already exists)")

        self.stdout.write(self.style.NOTICE(f"Done. Created: {created}, Updated: {updated}"))

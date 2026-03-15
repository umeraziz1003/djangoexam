from .models import RoleModulePermission


DEFAULTS = {
    "EXAM_OFFICER": {"create": True, "read": True, "update": True, "delete": True},
    "DEPT_CONTROLLER": {"create": True, "read": True, "update": True, "delete": True},
    "INTERNAL_EXAM_CONTROLLER": {"create": True, "read": True, "update": True, "delete": False},
    "STUDENT": {"create": False, "read": False, "update": False, "delete": False},
}

STUDENT_READ_MODULES = {"RESULTS", "TRANSCRIPTS"}


def ensure_permissions():
    for role, perms in DEFAULTS.items():
        for module, _ in RoleModulePermission.MODULE_CHOICES:
            if role == "STUDENT":
                perms = {
                    "create": False,
                    "read": module in STUDENT_READ_MODULES,
                    "update": False,
                    "delete": False,
                }
            RoleModulePermission.objects.get_or_create(
                role=role,
                module=module,
                defaults={
                    "can_create": perms["create"],
                    "can_read": perms["read"],
                    "can_update": perms["update"],
                    "can_delete": perms["delete"],
                },
            )


def get_permission(role, module):
    ensure_permissions()
    perm = RoleModulePermission.objects.filter(role=role, module=module).first()
    if perm:
        return perm
    class _P:
        can_create = False
        can_read = False
        can_update = False
        can_delete = False
    return _P()


def can(role, module, action):
    perm = get_permission(role, module)
    return getattr(perm, f"can_{action}", False)

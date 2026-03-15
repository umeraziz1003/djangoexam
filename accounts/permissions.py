from django.contrib.auth.models import Group, Permission

MODULE_PERMS = {
    "DEPARTMENTS": ("academics", "department"),
    "BATCHES": ("academics", "batch"),
    "SEMESTERS": ("academics", "semester"),
    "SESSIONS": ("academics", "session"),
    "COURSES": ("courses", "course"),
    "COURSE_OFFERINGS": ("courses", "courseoffering"),
    "ENROLLMENTS": ("enrollments", "enrollment"),
    "EXAMS": ("exams", "marks"),
    "RESULTS": ("results", "result"),
    "TRANSCRIPTS": ("transcripts", "transcript"),
    "STUDENTS": ("admission", "student"),
}
MODULE_LABELS = {
    "DEPARTMENTS": "Departments",
    "BATCHES": "Batches",
    "SEMESTERS": "Semesters",
    "SESSIONS": "Sessions",
    "COURSES": "Courses",
    "COURSE_OFFERINGS": "Course Offerings",
    "ENROLLMENTS": "Enrollments",
    "EXAMS": "Exams/Marks",
    "RESULTS": "Results",
    "TRANSCRIPTS": "Transcripts",
    "STUDENTS": "Students",
}

ACTIONS = ("create", "read", "update", "delete")
ACTION_TO_CODENAME = {
    "create": "add",
    "read": "view",
    "update": "change",
    "delete": "delete",
}

DEFAULT_GROUPS = {
    "EXAM_OFFICER": {"create": True, "read": True, "update": True, "delete": True},
    "DEPT_CONTROLLER": {"create": True, "read": True, "update": True, "delete": True},
    "STUDENT": {"create": False, "read": False, "update": False, "delete": False},
}

STUDENT_READ_MODULES = {"RESULTS", "TRANSCRIPTS"}


def perm_codename(module, action):
    mapping = MODULE_PERMS.get(module)
    if not mapping:
        return None
    app_label, model = mapping
    action_code = ACTION_TO_CODENAME.get(action)
    if not action_code:
        return None
    return app_label, f"{action_code}_{model}"


def ensure_default_groups():
    for name in DEFAULT_GROUPS.keys():
        Group.objects.get_or_create(name=name)


def group_perm_set(group_name):
    if group_name == "INTERNAL_EXAM_CONTROLLER":
        group_name = "DEPT_CONTROLLER"
    perms = set()
    for module, _ in MODULE_PERMS.items():
        if group_name == "STUDENT":
            actions = ["read"] if module in STUDENT_READ_MODULES else []
        else:
            actions = [a for a, allowed in DEFAULT_GROUPS[group_name].items() if allowed]
        for action in actions:
            code = perm_codename(module, action)
            if code:
                perms.add(code)
    return perms


def reset_default_permissions():
    ensure_default_groups()
    group_names = list(DEFAULT_GROUPS.keys())
    internal_group = Group.objects.filter(name="INTERNAL_EXAM_CONTROLLER").first()
    if internal_group:
        group_names.append("INTERNAL_EXAM_CONTROLLER")

    for group_name in group_names:
        group = Group.objects.get(name=group_name)
        perms = group_perm_set(group_name)
        perm_objs = []
        for app_label, codename in perms:
            perm = Permission.objects.filter(
                content_type__app_label=app_label,
                codename=codename,
            ).first()
            if perm:
                perm_objs.append(perm)
        group.permissions.set(perm_objs)


def can(user, module, action):
    code = perm_codename(module, action)
    if not code:
        return False
    app_label, codename = code
    return user.has_perm(f"{app_label}.{codename}")

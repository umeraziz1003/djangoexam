from .custom_views.department_views import (
    create_department,
    delete_department,
    departments_view,
    edit_department,
)
from .custom_views.batch_views import (
    batches_view,
    create_batch,
    delete_batch,
    edit_batch,
)
from .custom_views.semester_views import (
    create_semester,
    delete_semester,
    edit_semester,
    semesters_view,
)
from .custom_views.session_views import (
    create_session,
    delete_session,
    edit_session,
    sessions_view,
)

__all__ = [
    "departments_view", "create_department", "edit_department", "delete_department",
    "batches_view", "create_batch", "edit_batch", "delete_batch",
    "semesters_view", "create_semester", "edit_semester", "delete_semester",
    "sessions_view", "create_session", "edit_session", "delete_session",
]

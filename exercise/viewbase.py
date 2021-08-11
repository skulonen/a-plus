from typing import List, Optional

from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from authorization.permissions import Permission
from authorization.protocols import SupportsGetPermissions
from course.viewbase import CourseModuleMixin
from lib.protocols import (
    SupportsGetCommonObjects,
    SupportsGetResourceObjects,
    SupportsNote,
)
from lib.viewbase import BaseTemplateView
from .cache.hierarchy import NoSuchContent
from .exercise_summary import UserExerciseSummary
from .permissions import (
    ExerciseVisiblePermission,
    BaseExerciseAssistantPermission,
    SubmissionVisiblePermission,
    ModelVisiblePermission,
)
from .models import (
    LearningObject,
    Submission,
)
from .protocols import (
    SupportsGetExerciseObject,
    SupportsGetSubmissionObject,
)


class ExerciseBaseMixin(
        SupportsGetExerciseObject,
        SupportsGetPermissions,
        SupportsGetResourceObjects,
        SupportsNote,
        ):
    exercise_kw = "exercise_path"
    exercise_permission_classes = (
        ExerciseVisiblePermission,
    )

    def get_permissions(self) -> List[Permission]:
        perms = super().get_permissions()
        perms.extend((Perm() for Perm in self.exercise_permission_classes))
        return perms

    def get_resource_objects(self) -> None:
        super().get_resource_objects()
        self.exercise = self.get_exercise_object()
        self.note("exercise")


class ExerciseMixin(
        ExerciseBaseMixin,
        CourseModuleMixin,
        SupportsGetCommonObjects,
        ):
    exercise_permission_classes = ExerciseBaseMixin.exercise_permission_classes + (
        BaseExerciseAssistantPermission,
    )

    def get_exercise_object(self) -> LearningObject:
        try:
            exercise_id = self.content.find_path(
                self.module.id,
                self.kwargs[self.exercise_kw]
            )
            return LearningObject.objects.get(id=exercise_id).as_leaf_class()
        except (NoSuchContent, LearningObject.DoesNotExist):
            raise Http404("Learning object not found")

    def get_common_objects(self) -> None:
        super().get_common_objects()
        self.now = timezone.now()
        cur, tree, prev, nex = self.content.find(self.exercise)
        self.previous = prev
        self.current = cur
        self.next = nex
        self.breadcrumb = tree[1:-1]
        self.note("now", "previous", "current", "next", "breadcrumb")

    def get_summary_submissions(self, profile: Optional[User] = None) -> None:
        self.summary = UserExerciseSummary(
            self.exercise, profile or self.request.user
        )
        self.submissions = self.summary.get_submissions()
        self.note("summary", "submissions")


class ExerciseBaseView(ExerciseMixin, BaseTemplateView):
    pass


class ExerciseTemplateBaseView(ExerciseMixin, BaseTemplateView):
    pass


class ExerciseModelMixin(ExerciseMixin):
    model_permission_classes = (
        ModelVisiblePermission,
    )

    def get_permissions(self) -> List[Permission]:
        perms = super().get_permissions()
        perms.extend((Perm() for Perm in self.model_permission_classes))
        return perms

class ExerciseModelBaseView(ExerciseModelMixin, BaseTemplateView):
    pass


class SubmissionBaseMixin(
        SupportsGetPermissions,
        SupportsGetResourceObjects,
        SupportsGetSubmissionObject,
        SupportsNote,
        ):
    submission_kw = "submission_id"
    submission_permission_classes = (
        SubmissionVisiblePermission,
    )

    def get_permissions(self) -> List[Permission]:
        perms = super().get_permissions()
        perms.extend((Perm() for Perm in self.submission_permission_classes))
        return perms

    def get_resource_objects(self) -> None:
        super().get_resource_objects()
        self.submission = self.get_submission_object()
        self.note("submission")


class SubmissionMixin(SubmissionBaseMixin, ExerciseMixin):

    def get_submission_object(self) -> Submission:
        return get_object_or_404(
            Submission,
            id=self.kwargs[self.submission_kw],
            exercise=self.exercise
        )

    def get_summary_submissions(self) -> None:
        if self.submission.is_submitter(self.request.user):
            profile = self.profile
        else:
            profile = self.submission.submitters.first()
        super().get_summary_submissions(profile.user)
        self.index = len(self.submissions) - list(self.submissions).index(self.submission)
        self.note("index")


class SubmissionBaseView(SubmissionMixin, BaseTemplateView):
    pass

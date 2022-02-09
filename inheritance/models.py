from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.managers import InheritanceManager


class ModelWithInheritanceManager(InheritanceManager):
    def get_queryset(self):
        return super().get_queryset().select_related('content_type').select_subclasses()


class ModelWithInheritance(models.Model):
    """
    BaseExercise is the base class for all exercise types.
    It contains fields that are shared among all types.
    """

    objects                 = ModelWithInheritanceManager()

    content_type            = models.ForeignKey(ContentType,
                                                on_delete=models.CASCADE,
                                                editable=False,
                                                null=True)

    class Meta:
        abstract = False
        # This ensures that ModelWithInheritanceManager.get_queryset is ALWAYS
        # used when fetching instances that inherit from ModelWithInheritance.
        # Otherwise, related object accesses (e.g. submission.exercise) would
        # not return subclass instances.
        # This causes a problem, see the delete method.
        base_manager_name = 'objects'

    def save(self, *args, **kwargs):
        """
        Overrides the default save method from Django. If the method is called for
        a new model, its content type will be saved in the database as well. This way
        it is possible to later determine if the model is an instance of the
        class itself or some of its subclasses.
        """

        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)

        super(ModelWithInheritance, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # We need to override the delete method so that it re-fetches the
        # object without using InheritanceQueryset. This is because the base
        # manager has been overridden to call select_subclasses, and because of
        # that, the parent one-to-one fields no longer work (e.g.
        # BaseExercise.learningobject_ptr just returns the BaseExercise again).
        # See also: https://github.com/jazzband/django-model-utils/issues/11
        base_object = models.QuerySet(ModelWithInheritance).get(id=self.id)
        return models.Model.delete(base_object, *args, **kwargs)

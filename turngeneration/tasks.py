import datetime

from django.conf import settings
from django.utils import timezone

from celery import shared_task, current_app
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


# TODO: implement signal listeners for changes to Generator, GenerationRule, and Ready


@shared_task(bind=True)
def timed_generation(self, pk):
    from . import models, plugins

    try:
        generator = models.Generator.objects.get(pk=pk)
        realm_type = generator.content_type
        realm = generator.realm
    except Exception as e:
        logger.exception(f"Failed timed_generation(pk={pk}).")
        raise

    logger.info(
        f"Beginning timed generation on {realm_type.app_label}.{realm_type.model}(pk={realm.pk})."
    )

    # Lock against another task generating on the same Generator.
    if not models.Generator.objects.filter(pk=pk, generating=False).update(generating=True):
        logger.warning(
            f"Generation already in progress on {realm_type.app_label}.{realm_type.model}(pk={realm.pk}), aborting."
        )
        # Any update of the generator or firing of a new task should
        # be dealt with by the task holding the lock.
        return

    if not generator.force_generate:
        logger.info(
            f"Force-generation is disabled on {realm_type.app_label}.{realm_type.model}(pk={realm.pk}), aborting."
        )
        # No need to fire off a new task, since force-generations will
        # be disabled until the boolean is cleared, and then the
        # overriden save method will handle it.
        models.Generator.objects.filter(pk=pk).update(generating=False,
                                                      task_id='',
                                                      generation_time=None)
        return

    if generator.allow_pauses and generator.pauses.exists():
        logger.info(
            f"Pauses in effect on {realm_type.app_label}.{realm_type.model}(pk={realm.pk}), aborting."
        )
        # If the generator is paused, don't bother creating a new timed task.
        # It'll get picked back up when the pause is cancelled.
        models.Generator.objects.filter(pk=pk).update(generating=False,
                                                      task_id='',
                                                      generation_time=None)
        return

    generate = True

    last = generator.last_generation
    if last and generator.minimum_between_generations:
        if last.timestamp + datetime.timedelta(seconds=generator.minimum_between_generations) > timezone.now():
            logger.info(
                f"Insufficient time since last generation on {realm_type.app_label}.{realm_type.model}(pk={realm.pk}), aborting."
            )
            generate = False

    if generate:
        try:
            plugin = plugins.get_plugin_for_model(realm)
            plugin.force_generate(realm)
        except Exception as e:
            # TODO: consider doing a transaction rollback here
            logger.exception(
                f"Generation failed on {realm_type.app_label}.{realm_type.model}(pk={realm.pk})."
            )
            generate = False
        else:
            generator.timestamps.create()
            generator.readies.all().delete()

    task_id = ''
    eta = generator.next_time()
    if eta is not None:
        task_id = timed_generation.apply_async((pk,), eta=eta).id

    models.Generator.objects.filter(pk=pk).update(generating=False,
                                                  task_id=task_id,
                                                  generation_time=eta)

    if generate:
        logger.info(
            f"Ending timed generation on {realm_type.app_label}.{realm_type.model}(pk={pk})."
        )


@shared_task(bind=True)
def ready_generation(self, pk):
    from . import models, plugins

    try:
        generator = models.Generator.objects.get(pk=pk)
        realm_type = generator.content_type
        realm = generator.realm
    except Exception as e:
        logger.exception(f"Failed ready_generation(pk={pk}).")
        raise

    logger.info(
        f"Beginning auto-generation on {realm_type.app_label}.{realm_type.model}(pk={realm.pk})."
    )

    # Lock against another task generating on the same Generator.
    if not models.Generator.objects.filter(
            pk=pk, generating=False).update(generating=True):
        logger.warning(
            f"Generation already in progress on {realm_type.app_label}.{realm_type.model}(pk={realm.pk}), aborting."
        )
        # Any update of the generator or firing of a new task should
        # be dealt with by the task holding the lock.
        return

    if not generator.autogenerate:
        logger.info(
            f"Auto-generation not permitted on {realm_type.app_label}.{realm_type.model}(pk={realm.pk}), aborting."
        )
        models.Generator.objects.filter(pk=pk).update(generating=False)
        return

    try:
        if not generator.is_ready():
            logger.info(
                f"Not ready for auto-generation on {realm_type.app_label}.{realm_type.model}(pk={realm.pk}), aborting."
            )
            models.Generator.objects.filter(pk=pk).update(generating=False)
            return

        plugin = plugins.get_plugin_for_model(realm)
        plugin.auto_generate(realm)
    except Exception as e:
        # TODO: consider doing a transaction rollback here
        logger.exception(
            f"Generation failed on {realm_type.app_label}.{realm_type.model}(pk={realm.pk})."
        )
        models.Generator.objects.filter(pk=pk).update(generating=False)
        return

    generator.timestamps.create()
    generator.readies.all().delete()

    task_id, eta = '', None
    if generator.force_generate:
        eta = generator.next_time()
        if eta is not None:
            task_id = timed_generation.apply_async((pk,), eta=eta).id

    current_app.control.revoke(generator.task_id)
    models.Generator.objects.filter(pk=pk).update(generating=False,
                                                  task_id=task_id,
                                                  generation_time=eta)
    logger.info(
        f"Ending auto-generation on {realm_type.app_label}.{realm_type.model}(pk={pk})."
    )

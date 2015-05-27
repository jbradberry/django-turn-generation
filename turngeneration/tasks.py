from django.conf import settings
from celery import shared_task, current_app
from celery.utils.log import get_task_logger

import datetime

from . import models, plugins

logger = get_task_logger(__name__)


# TODO: implement signal listeners for changes to Generator, GenerationRule, and Ready


@shared_task(bind=True)
def timed_generation(self, pk):
    try:
        generator = models.Generator.objects.get(pk=pk)
        realm_type = generator.content_type
        realm = generator.realm
    except Exception as e:
        logger.exception("Failed timed_generation(pk={pk}).".format(pk=pk))
        raise

    logger.info(
        "Beginning timed generation on {app}.{model}(pk={pk}).".format(
            app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
    )

    # Lock against another task generating on the same Generator.
    if not models.Generator.objects.filter(
            pk=pk, generating=False).update(generating=True):
        logger.warning(
            "Generation already in progress on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        # Any update of the generator or firing of a new task should
        # be dealt with by the task holding the lock.
        return

    if not generator.force_generate:
        logger.info(
            "Force-generation is disabled on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        # No need to fire off a new task, since force-generations will
        # be disabled until the boolean is cleared, and then the
        # signal handler will deal with it.
        models.Generator.objects.filter(pk=pk).update(generating=False,
                                                      task_id='',
                                                      generation_time=None)
        return

    if generator.allow_pauses and generator.pauses.exists():
        logger.info(
            "Pauses in effect on {app}.{model}(pk={pk}), aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        # If the generator is paused, don't bother creating a new timed task.
        # It'll get picked back up when the pause is cancelled.
        models.Generator.objects.filter(pk=pk).update(generating=False,
                                                      task_id='',
                                                      generation_time=None)
        return

    generate = True

    now = datetime.datetime.utcnow()
    last = generator.last_generation
    if last and last + generator.minimum_between_generations > now:
        logger.info(
            "Insufficient time since last generation on {app}.{model}(pk={pk})"
            ", aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        generate = False

    if generate:
        try:
            plugin = plugins.get_plugin_for_model(realm)
            plugin.force_generate(realm)
        except Exception as e:
            # TODO: consider doing a transaction rollback here
            logger.exception(
                "Generation failed on {app}.{model}(pk={pk}).".format(
                    app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
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
            "Ending timed generation on {app}.{model}(pk={pk}).".format(
                app=realm_type.app_label, model=realm_type.model, pk=pk)
        )


@shared_task(bind=True)
def ready_generation(self, pk):
    try:
        generator = models.Generator.objects.get(pk=pk)
        realm_type = generator.content_type
        realm = generator.realm
    except Exception as e:
        logger.exception("Failed timed_generation(pk={pk}).".format(pk=pk))
        raise

    logger.info(
        "Beginning auto-generation on {app}.{model}(pk={pk}).".format(
            app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
    )

    # Lock against another task generating on the same Generator.
    if not models.Generator.objects.filter(
            pk=pk, generating=False).update(generating=True):
        logger.warning(
            "Generation already in progress on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        # Any update of the generator or firing of a new task should
        # be dealt with by the task holding the lock.
        return

    if not generator.autogenerate:
        logger.info(
            "Auto-generation not permitted on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        models.Generator.objects.filter(pk=pk).update(generating=False)
        return

    try:
        plugin = plugins.get_plugin_for_model(realm)

        if not plugin.is_ready(generator):
            logger.info(
                "Not ready for auto-generation on {app}.{model}(pk={pk}),"
                " aborting.".format(
                    app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
            )
            models.Generator.objects.filter(pk=pk).update(generating=False)
            return

        plugin.auto_generate(realm)
    except Exception as e:
        # TODO: consider doing a transaction rollback here
        logger.exception(
            "Generation failed on {app}.{model}(pk={pk}).".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
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
        "Ending auto-generation on {app}.{model}(pk={pk}).".format(
            app=realm_type.app_label, model=realm_type.model, pk=pk)
    )

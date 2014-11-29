from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger

from . import models

logger = get_task_logger(__name__)


@shared_task
def timed_generation(pk):
    generator = Generator.objects.get(pk=pk)
    realm_type = generator.content_type
    realm = generator.content_object

    logger.info(
        "Beginning timed generation on {app}.{model}(pk={pk}).".format(
            app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
    )

    # Lock against another task generating on the same Generator.
    if not Generator.objects.filter(
            pk=pk, generating=False).update(generating=True):
        logger.warning(
            "Generation already in progress on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        return

    now = datetime.datetime.utcnow()
    delta = (now - generator.last_generation)
    if delta < generator.minimum_between_generations:
        logger.info(
            "Insufficient time since last generation on {app}.{model}(pk={pk})"
            ", aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        Generator.objects.filter(pk=pk).update(generating=False)
        return

    if generator.allow_pauses and generator.pauses.exists():
        logger.info(
            "Pauses in effect on {app}.{model}(pk={pk}), aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        Generator.objects.filter(pk=pk).update(generating=False)
        return

    try:
        plugin.force_generate(generator.realm)
    except Exception as e:
        logger.exception(
            "Generation failed on {app}.{model}(pk={pk}).".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        Generator.objects.filter(pk=pk).update(generating=False)
        return

    generator.generation_times.create(timestamp=timestamp)
    eta = generator.next_generation()
    timed_generation.apply_async(pk, eta=eta)

    generator.readies.clear()

    Generator.objects.filter(pk=pk).update(generating=False)
    logger.info(
        "Ending timed generation on {app}.{model}(pk={pk}).".format(
            app=obj_type.app_label, model=obj_type.model, pk=pk)
    )


@shared_task
def ready_generation(pk):
    generator = Generator.objects.get(pk=pk)
    realm_type = generator.content_type
    realm = generator.content_object

    logger.info(
        "Beginning auto-generation on {app}.{model}(pk={pk}).".format(
            app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
    )

    # Lock against another task generating on the same Generator.
    if not Generator.objects.filter(
            pk=pk, generating=False).update(generating=True):
        logger.warning(
            "Generation already in progress on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        return

    try:
        plugin.auto_generate(generator.realm)
    except Exception as e:
        logger.exception(
            "Generation failed on {app}.{model}(pk={pk}).".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        Generator.objects.filter(pk=pk).update(generating=False)
        return

    generator.generation_times.create(timestamp=timestamp)
    eta = generator.next_generation()
    timed_generation.apply_async(pk, eta=eta)

    generator.readies.clear()

    Generator.objects.filter(pk=pk).update(generating=False)
    logger.info(
        "Ending auto-generation on {app}.{model}(pk={pk}).".format(
            app=obj_type.app_label, model=obj_type.model, pk=pk)
    )

from django.conf import settings
from celery import shared_task, current_app
from celery.utils.log import get_task_logger

from . import models, plugins

logger = get_task_logger(__name__)


@shared_task(bind=True)
def timed_generation(self, pk):
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

    valid = True

    now = datetime.datetime.utcnow()
    last = generator.last_generation
    if last and last + generator.minimum_between_generations > now:
        logger.info(
            "Insufficient time since last generation on {app}.{model}(pk={pk})"
            ", aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        valid = False

    if generator.allow_pauses and generator.pauses.exists():
        logger.info(
            "Pauses in effect on {app}.{model}(pk={pk}), aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        valid = False

    if valid:
        try:
            plugin = plugins.get_plugin_for_model(realm)
            plugin.force_generate(realm)
        except Exception as e:
            logger.exception(
                "Generation failed on {app}.{model}(pk={pk}).".format(
                    app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
            )
            valid = False
        else:
            # TODO: create model for noting generation times
            generator.generation_times.create(timestamp=timestamp)
            generator.readies.clear()

    if generator.task_id == self.request.id:
        eta = generator.next_generation()
        result = timed_generation.apply_async(pk, eta=eta)

        Generator.objects.filter(pk=pk).update(generating=False,
                                               task_id=result.id,
                                               generation_time=eta)
    else:
        Generator.objects.filter(pk=pk).update(generating=False)

    if valid:
        logger.info(
            "Ending timed generation on {app}.{model}(pk={pk}).".format(
                app=obj_type.app_label, model=obj_type.model, pk=pk)
        )


@shared_task(bind=True)
def ready_generation(self, pk):
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

    if not generator.autogenerate:
        logger.info(
            "Auto-generation not permitted on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        Generator.objects.filter(pk=pk).update(generating=False)
        return

    if not plugin.is_ready(generator):
        logger.info(
            "Not ready for auto-generation on {app}.{model}(pk={pk}),"
            " aborting.".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        Generator.objects.filter(pk=pk).update(generating=False)
        return

    try:
        plugin = plugins.get_plugin_for_model(realm)
        plugin.auto_generate(realm)
    except Exception as e:
        logger.exception(
            "Generation failed on {app}.{model}(pk={pk}).".format(
                app=realm_type.app_label, model=realm_type.model, pk=realm.pk)
        )
        Generator.objects.filter(pk=pk).update(generating=False)
        return

    # TODO: create model for noting generation times
    generator.generation_times.create(timestamp=timestamp)
    generator.readies.clear()

    eta = generator.next_generation()
    result = timed_generation.apply_async(pk, eta=eta)

    current_app.control.revoke(generator.task_id)
    Generator.objects.filter(pk=pk).update(generating=False,
                                           task_id=result.id,
                                           generation_time=eta)
    logger.info(
        "Ending auto-generation on {app}.{model}(pk={pk}).".format(
            app=obj_type.app_label, model=obj_type.model, pk=pk)
    )

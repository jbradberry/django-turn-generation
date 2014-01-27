from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def trigger_generation(pk):
    try:
        gentime_type = ContentType.objects.get(app_label='turngeneration',
                                               model='generationtime')
        gentime = gentime_type.get_object_for_this_type(pk=pk)
        obj_type = gentime.content_type
        obj = gentime.content_object

        logger.info(
            "Beginning generation on {app}.{model}(pk={pk}).".format(
                app=obj_type.app_label, model=obj_type.model, pk=obj.pk)
        )

        # FIXME: make this a configurable callable
        result = instance.generate()
        if not result:
            logger.error(
                "Generation failed to return a result on"
                " GenerationTime(pk={pk}).".format(pk=pk, result=result)
            )
            raise self.retry()
        gentime.update_time()

        logger.info(
            "Finishing generation on {app}.{model}(pk={pk}).".format(
                app=obj_type.app_label, model=obj_type.model, pk=obj.pk)
        )
    except Exception as e:
        logger.error(
            "Generation failed on GenerationTime(pk={pk}): {e}".format(
                pk=pk, e=e)
        )
        raise self.retry(exc=e)

from rest_framework import permissions


class PluginPermissions(permissions.DjangoObjectPermissions):
    """
    The request is authenticated using Django's object-level permissions.
    It requires an object-permissions-enabled backend, usually
    turngeneration.backends.TurnGenerationBackend.

    It ensures that the user is authenticated, and has the appropriate
    `add`/`change`/`delete` permissions on the parent object (e.g. the agent
    for Pause views) using .has_perms.

    This permission can only be applied against view classes that
    provide a `.model` or `.queryset` attribute.

    """

    def has_permission(self, request, view):
        # Note that `.model` attribute on views is deprecated, although we
        # enforce the deprecation on the view `get_serializer_class()` and
        # `get_queryset()` methods, rather than here.
        model_cls = getattr(view, 'model', None)
        queryset = getattr(view, 'queryset', None)

        if model_cls is None and queryset is not None:
            model_cls = queryset.model

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if model_cls is None and getattr(view, '_ignore_model_permissions', False):
            return True

        assert model_cls, ('Cannot apply PluginPermissions on a view that'
                           ' does not have `.model` or `.queryset` property.')

        perms = self.get_required_permissions(request.method, model_cls)

        parent = view.get_parent_obj()

        return (
            request.user and
            (request.user.is_authenticated or not self.authenticated_users_only) and
            request.user.has_perms(perms, parent)
        )

    def has_object_permission(self, request, view, obj):
        model_cls = getattr(view, 'model', None)
        queryset = getattr(view, 'queryset', None)

        if model_cls is None and queryset is not None:
            model_cls = queryset.model

        perms = self.get_required_object_permissions(request.method, model_cls)
        user = request.user

        parent = view.get_parent_obj()

        if not user.has_perms(perms, parent):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in ('GET', 'OPTIONS', 'HEAD'):
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions('GET', model_cls)
            if not user.has_perms(read_perms, parent):
                raise Http404

            # Has read permissions.
            return False

        return True

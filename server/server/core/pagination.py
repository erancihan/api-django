from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class PagePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000

    page_query_param = 'page_number'

    def paginate_queryset(self, queryset, request, view=None):
        """
        > Handle ordering of queryset before directing to super
        """
        data_order = str(request.query_params.get('order', 'asc')).lower()
        data_order_params = request.query_params.get('order_by', 'id')

        def process_param(param: str):
            if data_order == "asc" and param.startswith("-"):
                param = param[1:]
            if data_order == "desc" and not param.startswith("-"):
                param = f"-{param}"

            return param

        ordering = [
            process_param(param.strip())
            for param in data_order_params.split(',')
        ]

        queryset = queryset.order_by(*ordering)
        queryset = queryset.distinct()

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data, *args, **kwargs):
        return Response(
            {
                'page_size': self.page.paginator.per_page,
                'page_count': self.page.paginator.num_pages,
                'data_count': self.page.paginator.count,
                'page_number': self.page.number,
                'results': data
            }
        )

class PagePaginationMixin(object):
    serializer_class = None
    pagination_class = PagePagination

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        !!! incase mixin is used on a non-GenericApiView
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        !!! incase mixin is used on a non-GenericApiView
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        !!! incase mixin is used on a non-GenericApiView
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def paginate(self, objects, **kwargs):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.serializer_class(page, many=True, **kwargs)
            response = self.get_paginated_response(serializer.data)

            # set data count
            response.data['data_count'] = objects.count()

            return response

        serializer = self.serializer_class(objects, many=True, **kwargs)
        return Response(serializer.data)

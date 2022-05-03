import json
import logging
import threading
import time
from collections import Counter

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.http import HttpResponseRedirect
from django.template.loader import select_template
from django.utils.functional import cached_property

logger = logging.getLogger(__name__)

_local = threading.local()


class QueryStats:
    def __init__(self):
        self.queries = []

    def __str__(self):
        s = f"{self.num_queries} queries in {self.total_time_display}"
        if self.duplicate_queries:
            s += f" ({self.num_duplicate_queries} duplicates)"
        return s

    def __call__(self, execute, sql, params, many, context):
        current_query = {"sql": sql, "params": params, "many": many}
        start = time.monotonic()

        result = execute(sql, params, many, context)

        # if many, then X times is len(params)

        current_query["result"] = result

        current_query["duration"] = time.monotonic() - start

        self.queries.append(current_query)
        return result

    @cached_property
    def total_time(self):
        return sum(q["duration"] for q in self.queries)

    @staticmethod
    def get_time_display(seconds):
        if seconds < 0.01:
            return "{:.0f} ms".format(seconds * 1000)
        return "{:.2f} seconds".format(seconds)

    @cached_property
    def total_time_display(self):
        return self.get_time_display(self.total_time)

    @cached_property
    def num_queries(self):
        return len(self.queries)

    # @cached_property
    # def models(self):
    #     # parse table names from self.queries sql
    #     table_names = [x for x in [q['sql'].split(' ')[2] for q in self.queries] if x]
    #     models = connection.introspection.installed_models(table_names)
    #     return models

    @cached_property
    def duplicate_queries(self):
        sqls = [q["sql"] for q in self.queries]
        duplicates = {k: v for k, v in Counter(sqls).items() if v > 1}
        return duplicates

    @cached_property
    def num_duplicate_queries(self):
        # Count the number of "excess" queries by getting how many there
        # are minus the initial one (and potentially only one required)
        return sum(self.duplicate_queries.values()) - len(self.duplicate_queries)

    def as_summary_dict(self):
        return {
            "summary": str(self),
            "total_time": self.total_time,
            "num_queries": self.num_queries,
            "num_duplicate_queries": self.num_duplicate_queries,
        }

    def as_context_dict(self):
        # If we don't create a dict, the instance of this class
        # is lost before we can use it in the template
        for query in self.queries:
            # Add some useful display info
            query["duration_display"] = self.get_time_display(query["duration"])
            query["sql_display"] = (
                query["sql"]
                .replace("FROM", "\n  FROM")
                .replace("\n  FROM", "\nFROM", 1)  # Unindent the first occurence
                .replace("WHERE", "\n  WHERE")
                .replace("\n  WHERE", "\nWHERE", 1)  # Unindent the first occurence
                .replace("ORDER BY", "\nORDER BY")
                .replace("LIMIT", "\nLIMIT")
            )
            duplicates = self.duplicate_queries.get(query["sql"], 0)
            if duplicates:
                query["duplicate_count"] = duplicates

        summary = self.as_summary_dict()

        return {
            **summary,
            "total_time_display": self.total_time_display,
            "queries": self.queries,
        }

    def as_server_timing(self):
        duration = self.total_time * 1000  # put in ms
        duration = round(duration, 2)
        description = str(self)
        return f'querystats;dur={duration};desc="{description}"'


class QueryStatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.GET.get("querystats") == "disable":
            return self.get_response(request)

        querystats = QueryStats()

        with connection.execute_wrapper(querystats):
            # Have to wrap this first call so it is included in the querystats,
            # but we don't have to wrap everything else unless we are staff or debug
            is_staff = self.is_staff_request(request)

        if settings.DEBUG or is_staff:
            # Persist it on the thread
            _local.querystats = querystats

            with connection.execute_wrapper(_local.querystats):
                response = self.get_response(request)

            if settings.DEBUG:
                # TODO logging settings
                logger.debug("Querystats: %s", _local.querystats)

            # Make current querystats available on the current page
            # by using the server timing API which can be parsed client-side
            response["Server-Timing"] = _local.querystats.as_server_timing()

            if request.GET.get("querystats") == "store":
                request.session["querystats"] = json.dumps(
                    _local.querystats.as_context_dict(), cls=DjangoJSONEncoder
                )
                return HttpResponseRedirect(
                    request.get_full_path().replace(
                        "querystats=store", "querystats=show"
                    )
                )

            del _local.querystats

            return response

        else:
            return self.get_response(request)

    @staticmethod
    def is_staff_request(request):
        return (
            hasattr(request, "user")
            and request.user.is_authenticated
            and request.user.is_staff
        )

    def process_template_response(self, request, response):
        # Template hasn't been rendered yet, so we can't include querystats themselves
        # unless we're pulling the previous page stats from the session storage
        if hasattr(_local, "querystats") and self.is_staff_request(request):
            response.context_data["querystats_enabled"] = True

            # Load the previous querystats from the session and display them
            if request.GET.get("querystats") == "show":
                stored_querystats = request.session.get(
                    "querystats"
                )  # Not popping so page can be reloaded
                if stored_querystats:
                    # dates won't come back as Python dates...
                    stored_querystats = json.loads(stored_querystats)
                    response.context_data["querystats"] = stored_querystats

                # Extend the original template and overlay our querystats on top
                response.context_data["querystats_extend_template"] = select_template(
                    response.template_name
                )

                # Additional context for the view
                response.context_data[
                    "querystats_resolver_match"
                ] = request.resolver_match

                # Show full template debug info
                response.context_data[
                    "querystats_template_name"
                ] = response.template_name

                response.template_name = "stafftoolbar/querystats.html"

        return response

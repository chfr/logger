import datetime
import operator

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from logger.utils import format_timedelta
from .models import Value, Datum


@login_required
def index(request):
    datums = Datum.objects.filter(user=request.user)
    context = {'datums': datums}
    return render(request, "logger/index.html", context)


@login_required
def datum(request, datum_id):
    datum = get_object_or_404(Datum, user=request.user, pk=datum_id)
    context = {'datum': datum}

    template = 'logger/datum.html'

    if datum.type == Datum.TIMESTAMP:
        template = 'logger/datum_timestamp.html'
        context = timestamp_datum(request, datum, context)

    return render(request, template, context)


def timestamp_datum(request, datum, context):
    values = Value.objects.filter(datum=datum)

    days = {}

    for value in values:
        day = value.timestamp.date()

        if day not in days:
            days[day] = []

        days[day].append(value)

    zero_delta = datetime.timedelta()

    for day, entries in days.items():
        start = None
        for entry in entries:
            if start is None:
                start = entry
                entry.diff = zero_delta
                continue
            else:
                diff = entry.timestamp - start.timestamp
                entry.diff = diff
                start = None

    days = sorted(days.items(), key=operator.itemgetter(0))
    sums = []
    for _, entries in days:
        sums.append(sum(entry.diff.total_seconds() for entry in entries))

    days_with_sums = []
    for i in range(len(days)):
        days_with_sums.append((days[i][0], days[i][1], format_timedelta(datetime.timedelta(seconds=sums[i]))))

    context['days'] = days_with_sums

    return context


def log_value(request, slug, value):
    datum = get_object_or_404(Datum, slug=slug)

    if datum.type == Datum.FLOAT:
        try:
            val = float(value)
        except Exception:
            return HttpResponse("bad val")
        value = Value(datum=datum, float_value=val)
        value.save()
    elif datum.type == Datum.TIMESTAMP:
        if value != "timestamp":
            return HttpResponse('timestamp datum but value was not "timestamp"')

        value = Value(datum=datum)
        value.save()
    else:
        raise NotImplementedError('handling for {} datums not implemented yet'.format(datum.type))

    return HttpResponse("saved: slug: {}, value: {}".format(slug, value))

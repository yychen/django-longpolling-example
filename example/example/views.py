from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse
from celery.result import AsyncResult
from celery.exceptions import TimeoutError

import tasks
import gevent
from gevent import Greenlet
from gevent.pool import Group
import json

# Create your views here.
def test(request):
    return render_to_response('test.html',
            {
            }, context_instance=RequestContext(request))

class CheckGreenlet(Greenlet):
    def __init__(self, id, group):
        Greenlet.__init__(self)
        self.id = id
        self.result = None
        self.done = False

        self.group = group
        self.task = AsyncResult(self.id)

        if self.task.ready():
            self.result = self.task.get()
            self.done = True
        else:
            self.group.add(self)
            self.start()

    def _run(self):
        try:
            self.result = self.task.get(timeout=3)
            self.done = True
            self.group.kill()
        except TimeoutError:
            pass

def poll(request):
    out = {}
    out['res'] = {}

    ids = request.GET.get('ids')
    done = True

    if ids:
        group = Group()
        greenlets = []
        split = ids.split(',')

        for id in split:
            greenlet = CheckGreenlet(id, group)
            greenlets.append(greenlet)

        group.join()

        for greenlet in greenlets:
            out['res'][greenlet.id] = greenlet.result

            if not greenlet.done:
                done = False

        out['done'] = done

    return HttpResponse(json.dumps(out), mimetype='application/json')

def trigger(request):
    timeouts = [4, 3, 2, 1]

    out = {}
    out['id'] = []

    for i in timeouts:
        result = tasks.timeout.delay('hihi: %d' % i, i)
        out['id'].append(result.task_id)

        print result.state

    out['msg'] = 'started'
    return HttpResponse(json.dumps(out), mimetype='application/json')

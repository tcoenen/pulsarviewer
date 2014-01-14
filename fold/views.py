from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.utils import simplejson

from django.http import HttpResponseRedirect, QueryDict, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from models import Bestprof, FoldedImage
from forms import ConstraintsForm, CandidateTagForm

OK_GET_PARAMETERS = set([
    'lo_dm',
    'hi_dm',
    'lo_p',
    'hi_p',
    'lo_redchisq',
    'hi_redchisq',
    'beam',
    'order',
])

CONSTRAINTS_KEYS = [
    'lo_p', 'hi_p', 'lo_redchisq', 'hi_redchisq', 'lo_dm', 'hi_dm']


def prepend_questionmark(s):
    if s:
        s = '?' + s
    return s


def check_parameters(get_pars):
    qd = get_pars.copy()
    for k in get_pars:
        if not k in OK_GET_PARAMETERS:
            del qd[k]
    return qd


class BestprofListView(ListView):
    model = Bestprof
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('format', 'html') == 'json':
            # Shortcut, we just want the primary keys as json
            tmp = list(self.get_queryset().values_list('pk', flat=True))
            return HttpResponse(simplejson.dumps(tmp, 'application/json'))
        else:
            return super(BestprofListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Bestprof.objects.with_constraints(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super(BestprofListView, self).get_context_data(**kwargs)
        context['selection'] = prepend_questionmark(
            check_parameters(self.request.GET).urlencode())
        return context


class CandidatePDMView(BestprofListView):
    template_name = 'fold/pdm_graph.html'
    paginate_by = 2000


class CandidatePChiView(BestprofListView):
    template_name = 'fold/pchi_graph.html'
    paginate_by = 2000


class CandidatePHistogramView(BestprofListView):
    template_name = 'fold/p_hist.html'
    paginate_by = None


class ConstraintsView(FormView):
    template_name = 'fold/constraints.html'
    form_class = ConstraintsForm
    CONSTRAINTS_KEYS = ['lo_p', 'hi_p', 'lo_redchisq', 'hi_redchisq', 'lo_dm',
                        'hi_dm']

    def get_context_data(self, **kwargs):
        context = super(ConstraintsView, self).get_context_data(**kwargs)
        context['selection'] = prepend_questionmark(
            check_parameters(self.request.GET).urlencode())
        return context

    def get_initial(self):
        tmp = {}
        for k, v in self.request.GET.iteritems():
            if k in CONSTRAINTS_KEYS:
                tmp[k] = v
        return tmp

    def form_valid(self, form):
        qd = QueryDict('').copy()
        # TODO : consider filtering this to a subset of the forms' values if
        # needed.
        tmp = {}
        for k, v in form.cleaned_data.iteritems():
            if k in CONSTRAINTS_KEYS and v is not None:
                tmp[k] = v
        qd.update(tmp)
        path = reverse('candidate_constraints') + '?' + qd.urlencode()
        return HttpResponseRedirect(path)


class BestprofDetailView(UpdateView):
    template_name = 'fold/tag.html'
    form_class = CandidateTagForm
    model = Bestprof

    # TODO: hack into dispatch to also handle xhr requests (both GET and POST)
    # using json.

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        print self.request.POST
        if self.request.GET.get('format', 'html') == 'json':
            # Shortcut, we just want the primary keys as json
            obj = self.get_object()
            img = FoldedImage.objects.get(bestprof=obj.pk).file.url
            tmp = {
                'pk': obj.pk,
                'tags': [t.name for t in obj.tags.all()],
                'img': img,
            }
            return HttpResponse(simplejson.dumps(tmp, 'application/json'))
        else:
            return super(BestprofDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BestprofDetailView, self).get_context_data(**kwargs)
        context['selection'] = prepend_questionmark(
            check_parameters(self.request.GET).urlencode())
        img = FoldedImage.objects.get(bestprof=context['object'].pk)
        context['img'] = img
        return context

    def get_success_url(self):
        return reverse('bestprof_detail', args=(self.object.pk,)) + '?' + \
            self.request.GET.urlencode()


class ClassifyView(TemplateView):
    template_name = 'fold/classify.html'

    def get_context_data(self, **kwargs):
        # include the constraints into the template (to be accessed through
        # java script in the page easily (without messing with the GET
        # parameters from Javascript).
        qd = self.request.GET.copy()
        tmp = simplejson.dumps(qd)
        return {'constraints': tmp}

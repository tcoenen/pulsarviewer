from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.utils import simplejson

from django.http import HttpResponseRedirect, QueryDict, HttpResponse

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
    'tag',
])

CONSTRAINTS_KEYS = [
    'lo_p', 'hi_p', 'lo_redchisq', 'hi_redchisq', 'lo_dm', 'hi_dm', 'tag'
]


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
        if request.is_ajax():
            # Shortcut, we just want the primary keys as json.
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

    def get_context_data(self, **kwargs):
        context = super(CandidatePDMView, self).get_context_data(**kwargs)

        # Add the current plot page to the context (so that the position in
        # the overall list of candidates is retained when switching from 
        # P-DM to P-CHI plot).
        page_no = self.request.GET.get(u'page', u'')
        if page_no:
            tmp = QueryDict('').copy()
            tmp.update({u'page': page_no})
            context['extra_page'] = tmp.urlencode()
        return context


class CandidatePChiView(BestprofListView):
    template_name = 'fold/pchi_graph.html'
    paginate_by = 2000

    def get_context_data(self, **kwargs):
        context = super(CandidatePChiView, self).get_context_data(**kwargs)

        # Add the current plot page to the context (so that the position in
        # the overall list of candidates is retained when switching from 
        # P-CHI to P-DM plot).
        page_no = self.request.GET.get(u'page', u'')
        if page_no:
            tmp = QueryDict('').copy()
            tmp.update({u'page': page_no})
            context['extra_page'] = tmp.urlencode()
        return context


class CandidatePHistogramView(BestprofListView):
    template_name = 'fold/p_hist.html'
    paginate_by = None


class ConstraintsView(FormView):
    template_name = 'fold/constraints.html'
    form_class = ConstraintsForm
    CONSTRAINTS_KEYS = ['lo_p', 'hi_p', 'lo_redchisq', 'hi_redchisq', 'lo_dm',
                        'hi_dm', 'tag']

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
            if k in CONSTRAINTS_KEYS and v:
                tmp[k] = v
        qd.update(tmp)
        path = reverse('candidate_constraints') + '?' + qd.urlencode()
        return HttpResponseRedirect(path)


class BestprofDetailView(UpdateView):
    template_name = 'fold/tag.html'
    form_class = CandidateTagForm
    model = Bestprof

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            obj = self.get_object()
            img = FoldedImage.objects.get(bestprof=obj.pk).file.url
            tmp = {
                'pk': obj.pk,
                'tags': [t.name for t in obj.tags.all()],
                'img': img,
            }
            return HttpResponse(simplejson.dumps(tmp, 'application/json'))
        else:
            return super(BestprofDetailView, self).post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # TODO: handle failures in the AJAX path better!
        # TODO: clean up!
        if request.is_ajax():
            target_pk = int(request.POST[u'pk'])
            tag = request.POST[u'tags[]']
            try:
                fi = FoldedImage.objects.get(bestprof=target_pk)
            except Exception, e:  # TODO: Clean this up!
                print 'Failure getting the FoldedImage instance from DB'
                print e
            else:
                if tag not in fi.bestprof.tags.all():
                    fi.bestprof.tags.add(tag)
                    fi.save()
            tmp = {}  # consider setting some success/failure message
            return HttpResponse(simplejson.dumps(tmp, 'application/json'))
        else:
            return super(BestprofDetailView, self).post(request, *args, **kwargs)

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
        # Include the constraints into the template (to be accessed through
        # java script in the page easily (without messing with the GET
        # parameters from Javascript).
        qd = self.request.GET.copy()
        tmp = simplejson.dumps(qd)
        context = {
            'constraints': tmp,
            'selection': prepend_questionmark(check_parameters(self.request.GET).urlencode())
        }

        return context

from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect, QueryDict

from models import Bestprof, FoldedImage
from forms import ConstraintsForm

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

    def get_queryset(self):
        return Bestprof.objects.with_constraints(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super(BestprofListView, self).get_context_data(**kwargs)
        context['selection'] = prepend_questionmark(
            check_parameters(self.request.GET).urlencode())
        return context


class BestprofDetailView(DetailView):
    model = Bestprof

    def get_context_data(self, **kwargs):
        context = super(BestprofDetailView, self).get_context_data(**kwargs)

        img = FoldedImage.objects.get(bestprof=context['object'].pk)

        context['selection'] = prepend_questionmark(
            check_parameters(self.request.GET).urlencode())
        context['img'] = img
        context['dm'] = '%.2f' % context['object'].best_dm
        context['p0'] = '%.2f' % context['object'].p_bary
        context['redchisq'] = '%.3f' % context['object'].reduced_chi_sq
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
    CONSTRAINTS_KEYS = ['lo_p', 'hi_p', 'lo_redchisq', 'hi_redchisq']

    def get_context_data(self, **kwargs):
        context = super(ConstraintsView, self).get_context_data(**kwargs)
        context['selection'] = prepend_questionmark(
            check_parameters(self.request.GET).urlencode())
        return context

    def get_initial(self):
        tmp = {}
        for k, v in self.request.GET.iteritems():
            if k in self.CONSTRAINTS_KEYS:
                tmp[k] = v
        return tmp

    def form_valid(self, form):
        qd = QueryDict('').copy()
        # TODO : consider filtering this to a subset of the forms' values if
        # needed.
        tmp = {}
        for k, v in form.cleaned_data.iteritems():
            if k in self.CONSTRAINTS_KEYS and v is not None:
                tmp[k] = v
        qd.update(tmp)
        path = reverse('candidate_constraints') + '?' + qd.urlencode()
        return HttpResponseRedirect(path)

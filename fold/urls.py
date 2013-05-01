from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from views import BestprofListView, CandidatePHistogramView, ConstraintsView
from views import CandidatePDMView, CandidatePChiView, ClassifyView
from views import BestprofDetailView

urlpatterns = patterns('',
    url(r'(?P<pk>\d+)/$', BestprofDetailView.as_view(), name='bestprof_detail'),
#    url(r'(?P<pk>\d+)/tag/', TempView.as_view(), name='bestprof_tag'),
    url(r'pdm/', CandidatePDMView.as_view(), name='candidate_pdm_graph'),
    url(r'pchi/', CandidatePChiView.as_view(), name='candidate_pchi_graph'),
    url(r'phist/', CandidatePHistogramView.as_view(),
        name='candidate_p_histogram'),
    url(r'constraints/', ConstraintsView.as_view(),
        name='candidate_constraints'),
    url(r'classify/', ClassifyView.as_view(), name='candidate_classify'),
    # 'Front page'
    url(r'home/', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'', BestprofListView.as_view(), name='bestprof_list'),

)

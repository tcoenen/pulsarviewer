from django import template
from django.core.urlresolvers import reverse
import StringIO
import copy

from brp.svg.base import SVGCanvas, PlotContainer, TextFragment
from brp.svg.plotters.scatter import ScatterPlotter
from brp.svg.plotters.gradient import GradientPlotter, RGBGradient
#from brp.svg.plotters.symbol import RADECSymbol
from brp.svg.plotters.histogram import HistogramPlotter, bin_data_log

register = template.Library()


class CandidateGraphNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):

        qs = context[self.var_name]
        tmp = StringIO.StringIO()

        cv = SVGCanvas(1000, 600, background_color='black')

        P = [c.p_bary for c in qs.all() if c.best_dm > 0]
        DM = [c.best_dm for c in qs.all() if c.best_dm > 0]
        REDCHISQ = [c.reduced_chi_sq for c in qs.all() if c.best_dm > 0]
        max_redchisq = max(REDCHISQ)
        min_redchisq = min(REDCHISQ)
        LINKS = [reverse('bestprof_detail', args=[c.pk])
                 for c in qs.all() if c.best_dm > 0]
        # TODO: add RA and DEC

        if P:
            # Main panel showing candidate period-DM scatter plot:
            pc = PlotContainer(0, 0, 910, 600, color='white', x_log=True,
                               y_log=True)
            pc.bottom.set_label('Period (ms)')
            pc.top.hide_label()
            pc.left.set_label('Dispersion Measure (cm^-3 pc)')
            pc.right.hide_label()
            gr = RGBGradient((min_redchisq, max_redchisq), (0, 0, 1),
                             (1, 0, 0))
            scp = ScatterPlotter(P, DM, REDCHISQ, gradient=gr, gradient_i=2,
                                 links=LINKS)
            pc.add_plotter(scp)
            cv.add_plot_container(pc)
            # Gradient:
            pc = PlotContainer(870, 0, 120, 600, color='white', data_padding=0)
            pc.top.hide_label()
            pc.top.hide_tickmarks()
            pc.left.hide_tickmarks()
            pc.bottom.hide_label()
            pc.bottom.hide_tickmarks()
            pc.left.hide_label()
            pc.right.set_label('Candidate Reduced Chi-Square')
            pc.add_plotter(GradientPlotter(copy.deepcopy(scp.gradient)))
            cv.add_plot_container(pc)
            # write number of candidates shown:
            tf = TextFragment(50, 590, '(Showing %d candidates.)' %
                              len(P), color='white', font_size=15)
            cv.add_plot_container(tf)
        else:
            tf = TextFragment(200, 200, 'No Candidates found.', color='red',
                              font_size=50)
            cv.add_plot_container(tf)

        cv.draw(tmp)
        return tmp.getvalue()


def do_candidate_graph(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        msg = '% tag requires a single queryset as argument' % \
            token.contenst.split()[0]

        raise template.TemplateSyntaxError(msg)
    return CandidateGraphNode(var_name)

register.tag('candidate_graph', do_candidate_graph)


class ChiSquareCandidateGraphNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        qs = context[self.var_name]

        P = [c.p_bary for c in qs.all() if c.best_dm > 0]
        DM = [c.best_dm for c in qs.all() if c.best_dm > 0]
        REDCHISQ = [c.reduced_chi_sq for c in qs.all() if c.best_dm > 0]
        LINKS = [reverse('bestprof_detail', args=[c.pk])
                 for c in qs.all() if c.best_dm > 0]
        # TODO: add RA and DEC
        lo_dm = min(DM)
        max_dm = max(DM)

        cv = SVGCanvas(1000, 600, background_color='black')
        if P:
            pc = PlotContainer(0, 0, 910, 600, color='white',
                               background_color='black', x_log=True,
                               y_log=True)
            gr = RGBGradient((lo_dm, max_dm), (0, 0, 1), (1, 0, 0))
            pc.add_plotter(ScatterPlotter(P, REDCHISQ, DM, gradient=gr,
                           gradient_i=2, links=LINKS))
            pc.top.hide_tickmarklabels()
            pc.top.hide_label()
            pc.right.hide_tickmarklabels()
            pc.right.hide_label()
            pc.left.set_label('Reduced Chi Square')
            pc.bottom.set_label('Period (ms)')
            cv.add_plot_container(pc)
            # Gradient:
            pc = PlotContainer(870, 0, 120, 600, color='white', data_padding=0)
            pc.top.hide_label()
            pc.top.hide_tickmarks()
            pc.left.hide_tickmarks()
            pc.bottom.hide_label()
            pc.bottom.hide_tickmarks()
            pc.left.hide_label()
            pc.right.set_label('Dispersion Measure cm^-3 pc')
            pc.add_plotter(GradientPlotter(gr))
            cv.add_plot_container(pc)
            # write number of candidates shown:
            tf = TextFragment(50, 590,
                              '(Showing %d candidates.)' % len(P),
                              color='white', font_size=15)
            cv.add_plot_container(tf)
        else:
            tf = TextFragment(200, 200, 'No Candidates found.', color='red',
                              font_size=50)
            cv.add_plot_container(tf)

        tmp = StringIO.StringIO()
        cv.draw(tmp)
        return tmp.getvalue()


def do_chi_square_candidate_graph(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        msg = '% tag requires a single queryset as argument' % \
            token.contenst.split()[0]

        raise template.TemplateSyntaxError(msg)
    return ChiSquareCandidateGraphNode(var_name)

register.tag('chi_square_candidate_graph', do_chi_square_candidate_graph)


class CandidatePHistogramNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        qs = context[self.var_name]
        tmp = StringIO.StringIO()

        P = [c.p_bary for c in qs.all() if c.p_bary > 0]
        binned = bin_data_log(P, 200)

        cv = SVGCanvas(1000, 600, background_color='black')
        if P:
            pc = PlotContainer(0, 0, 910, 600, color='white', x_log=True)
            pc.bottom.set_label('Period (ms)')
            pc.top.hide_label()
            pc.left.set_label('Count')
            pc.right.hide_label()
            hp = HistogramPlotter(binned, color='white')
            pc.add_plotter(hp)
            cv.add_plot_container(pc)
            # write number of candidates shown:
            tf = TextFragment(50, 590, '(Showing %d candidates.)' %
                              len(P), color='white', font_size=15)
            cv.add_plot_container(tf)
        else:
            tf = TextFragment(200, 200, 'No Candidates found.', color='red',
                              font_size=50)
            cv.add_plot_container(tf)

        tmp = StringIO.StringIO()
        cv.draw(tmp)
        return tmp.getvalue()


def do_candidate_histogram(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        msg = '% tag requires a single queryset as argument' % \
            token.contenst.split()[0]

        raise template.TemplateSyntaxError(msg)
    return CandidatePHistogramNode(var_name)

register.tag('candidate_histogram', do_candidate_histogram)

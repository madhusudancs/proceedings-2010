__all__ = ['writer']

import docutils.core as dc
import docutils.writers
from docutils import nodes

from docutils.writers.latex2e import (Writer, LaTeXTranslator,
                                      PreambleCmds)

from options import options

PreambleCmds.float_settings = '''
\\usepackage[font={small,it},labelfont=bf]{caption}
\\usepackage{float}
'''

class Translator(LaTeXTranslator):
    def __init__(self, *args, **kwargs):
        LaTeXTranslator.__init__(self, *args, **kwargs)

    # Handle author declarations

    current_field = ''

    author_names = []
    author_institutions = []
    author_emails = []
    paper_title = ''
    table_caption = []

    def visit_docinfo(self, node):
        pass

    def depart_docinfo(self, node):
        pass

    def visit_author(self, node):
        self.author_names.append(self.encode(node.astext()))
        raise nodes.SkipNode

    def depart_author(self, node):
        pass

    def visit_classifier(self, node):
        pass

    def depart_classifier(self, node):
        pass

    def visit_field_name(self, node):
        self.current_field = node.astext()
        raise nodes.SkipNode

    def visit_field_body(self, node):
        text = self.encode(node.astext())

        if self.current_field == 'email':
            self.author_emails.append(text)
        elif self.current_field == 'institution':
            self.author_institutions.append(text)

        self.current_field = ''

        raise nodes.SkipNode

    def depart_field_body(self, node):
        raise nodes.SkipNode

    def depart_document(self, node):
        LaTeXTranslator.depart_document(self, node)

        title = self.paper_title
        authors = ', '.join(self.author_names)

        author_notes = ['''
The corresponding author is with %s, e-mail: \protect\href{%s}{%s}.
''' % (self.author_institutions[0], self.author_emails[0],
       self.author_emails[0])]

        author_notes = ''.join('\\thanks{%s}' % n for n in author_notes)

        title_template = '\\title{%s}\\author{%s%s}\\maketitle'
        title_template = title_template % (title,
                                           authors,
                                           author_notes)

        marks = r'''
        \renewcommand{\leftmark}{%s}
        \renewcommand{\rightmark}{%s}
        ''' % (options['proceedings_title'], title.upper())
        title_template += marks

        self.body_pre_docinfo = [title_template]

    def visit_title(self, node):
        if self.section_level == 1:
            if self.paper_title:
                import warnings
                warnings.warn(RuntimeWarning("Title set twice--ignored. "
                                             "Could be due to ReST"
                                             "error.)"))
            else:
                self.paper_title = self.encode(node.astext())
            raise nodes.SkipNode

        elif node.astext() == 'References':
            raise nodes.SkipNode

        LaTeXTranslator.visit_title(self, node)

    def visit_paragraph(self, node):
        if 'abstract' in node['classes']:
            self.out.append('\\begin{abstract}')

    def depart_paragraph(self, node):
        if 'abstract' in node['classes']:
            self.out.append('\\end{abstract}')

    def visit_image(self, node):
        attrs = node.attributes
        node.attributes['width'] = '\columnwidth'
        node.attributes['align'] = 'left'

        LaTeXTranslator.visit_image(self, node)

    def visit_footnote(self, node):
        # Work-around for a bug in docutils where a
        # "%" is prepended to footnote text.
        LaTeXTranslator.visit_footnote(self, node)
        self.out[-1] = self.out[-1].strip('%')

    def visit_table(self, node):
        self.out.append(r'\begin{table}')
        LaTeXTranslator.visit_table(self, node)

    def depart_table(self, node):
        LaTeXTranslator.depart_table(self, node)

        self.out.append(r'\caption{%s}' % ''.join(self.table_caption))
        self.table_caption = []

        self.out.append(r'\end{table}')
        self.active_table.set('preamble written', 1)

    def visit_thead(self, node):
        # Store table caption locally and then remove it
        # from the table so that docutils doesn't render it
        # (in the wrong place)
        self.table_caption = self.active_table.caption
        self.active_table.caption = []

        LaTeXTranslator.visit_thead(self, node)

    def depart_thead(self, node):
        LaTeXTranslator.depart_thead(self, node)


writer = Writer()
writer.translator_class = Translator

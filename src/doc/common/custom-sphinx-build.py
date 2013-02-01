"""
This is Sage's version of the sphinx-build script

Enhancements are:

* import the Sage library to access the docstrings, otherwise doc
  buliding doesn't work.

* redirect stdout to our own logger, and remove some unwanted chatter.
"""

import os
import sys
import re


# override the fancy multi-line formatting
def term_width_line(text):
    return text + '\n'

import sphinx.util.console
sphinx.util.console.term_width_line = term_width_line




useless_chatter = (
    re.compile('^$'),
    re.compile('^Running Sphinx v'),
    re.compile('^loading intersphinx inventory from '),
    re.compile('^Compiling a sub-document'),
    re.compile('^updating environment: 0 added, 0 changed, 0 removed'),
    re.compile('^looking for now-outdated files... none found'),
    re.compile('^no targets are out of date.'),
    re.compile('^building \[.*\]: targets for 0 source files that are out of date'),
    re.compile('^loading pickled environment... done'),
    re.compile('^loading cross citations... done \([0-9]* citations\).')
    )


class SageSphinxLogger(object):
    """
    This implements the file object interface to serve as sys.stdout
    replacement.
    """
    ansi_color = re.compile(r'\x1b\[[0-9;]*m')
    ansi_reset = re.compile(r'\x1b\[39;49;00m')
    prefix_len = 9

    def __init__(self, stream, prefix):
        self._stream = stream
        self._color = stream.isatty()
        prefix = prefix[0:self.prefix_len]
        prefix = ('[{0:'+str(self.prefix_len)+'}]').format(prefix)
        color = { 1:'darkgreen', 2:'red' }
        color = color.get(stream.fileno(), 'lightgray')
        self._prefix = sphinx.util.console.colorize(color, prefix)


    def _filter_out(self, line):
        line = re.sub(self.ansi_color, '', line)
        for regex in useless_chatter:
            if regex.match(line) is not None:
                return True
        return False

    def _log_line(self, line):
        if self._filter_out(line):
            return
        line = self._prefix + ' ' + line.strip() + '\n'
        if not self._color:
            line = self.ansi_color.sub('', line)
        self._stream.write(line)
        self._stream.flush()

    _line_buffer = ''

    def _break_long_lines(self):
        """
        Break text that has been formated with string.ljust() back
        into individual lines.  Return partial output. Do nothing if
        the filter rule matches, otherwise subsequent lines would be
        not filtered out.
        """
        if self._filter_out(self._line_buffer):
            return
        cols = sphinx.util.console._tw
        lines = []
        buf = self._line_buffer
        while len(buf) > cols:
            lines.append(buf[0:cols])
            buf = buf[cols:]
        lines.append(buf)
        self._line_buffer = '\n'.join(lines)

    def _write(self, string):
        self._line_buffer += string
        #self._break_long_lines()
        lines = self._line_buffer.splitlines()
        for i, line in enumerate(lines):
            last = (i == len(lines)-1)
            if last and not self._line_buffer.endswith('\n'):
                self._line_buffer = line
                return
            self._log_line(line)
        self._line_buffer = ''


    # file object interface follows

    closed = False
    encoding = None
    mode = 'w'
    name = '<log>'
    newlines = None
    softspace = 0

    def isatty(self):
        return True

    def close(self):
        if self._line_buffer != '':
            self._log_line(self._line_buffer)
            self._line_buffer = ''

    def flush(self):
        self._stream.flush()

    def write(self, str):
        try:
            self._write(str)
        except:
            import traceback
            traceback.print_exc(file=self._stream)

    def writelines(self, sequence):
        for line in sequence:
            self.write(line)


output_dir = sys.argv[-1]
sys.stdout = SageSphinxLogger(sys.stdout, os.path.basename(output_dir))
sys.stderr = SageSphinxLogger(sys.stderr, os.path.basename(output_dir))



# pull in the Sage library
import sage.all

# Minimize GAP/libGAP RAM usage when we build the docs
from sage.interfaces.gap import set_gap_memory_pool_size
set_gap_memory_pool_size(0)  # will be rounded up to 1M

if __name__ == '__main__':
    from sphinx.cmdline import main
    sys.exit(main(sys.argv))

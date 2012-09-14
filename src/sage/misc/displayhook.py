"""
Implements a displayhook for Sage. The main improvement over the default
displayhook is a new facility for displaying lists of matrices in an easier to
read format.

AUTHORS:

- Bill Cauchois (2009): initial version
"""

import sys, __builtin__


# This is used to wrap lines when printing "tall" lists.
MAX_COLUMN = 70

def _check_tall_list_and_format(the_list):
    """
    First check whether a list is "tall" -- whether the reprs of the
    elements of the list will span multiple lines and cause the list
    to be printed awkwardly.  If not, this function returns None and
    does nothing; you should revert back to the normal method for
    printing an object (its repr). If so, return the string in the
    special format. Note that the special format isn't just for
    matrices. Any object with a multiline repr will be formatted.

    INPUT:

    - ``the_list`` - The list (or a tuple).

    TESTS::

        sage: from sage.misc.displayhook import format_obj

    We test _check_tall_list_and_format() indirectly by calling format_obj() on
    a list of matrices::

        sage: print sage.misc.displayhook.format_obj( \
                [matrix([[1, 2, 3, 4], [5, 6, 7, 8]]) for i in xrange(7)])
        [
        [1 2 3 4]  [1 2 3 4]  [1 2 3 4]  [1 2 3 4]  [1 2 3 4]  [1 2 3 4]
        [5 6 7 8], [5 6 7 8], [5 6 7 8], [5 6 7 8], [5 6 7 8], [5 6 7 8],
        <BLANKLINE>
        [1 2 3 4]
        [5 6 7 8]
        ]

    We return None if we don't have anything special to do::

        sage: format_obj('one-line string')
        sage: format_obj(matrix([[1,2,3]]))
    """
    # For every object to be printed, split its repr on newlines and store the
    # result in this list.
    split_reprs = []
    tall = False
    for elem in the_list:
        split_reprs.append(`elem`.split('\n'))
        if len(split_reprs[-1]) > 1:
            # Meanwhile, check to make sure the list is actually "tall".
            tall = True
    if not tall:
        return None
    # Figure out which type of parenthesis to use, based on the type of the_list.
    if isinstance(the_list, tuple):
        parens = '()'
    elif isinstance(the_list, list):
        parens = '[]'
    else:
        raise TypeError, 'expected list or tuple'

    # running_lines is a list of lines, which are stored as lists of strings
    # to be joined later. For each split repr, we add its lines to the
    # running_lines array. When current_column exceeds MAX_COLUMN, process
    # and output running_lines using _print_tall_list_row.
    running_lines = [[]]
    current_column = 0
    s = [parens[0]]
    for split_repr in split_reprs:
        width = max(len(x) for x in split_repr)
        if current_column + width > MAX_COLUMN and not (width > MAX_COLUMN):
            s.extend(_tall_list_row(running_lines))
            running_lines = [[]]
            current_column = 0
        current_column += width + 2
        # Add the lines from split_repr to the running_lines array. It may
        # be necessary to add or remove lines from either one so that the
        # number of lines matches up.
        for i in xrange(len(running_lines), len(split_repr)):
            running_lines.insert(0, [' ' * len(x) for x in running_lines[-1]])
        line_diff = len(running_lines) - len(split_repr)
        for i, x in enumerate(split_repr):
            running_lines[i + line_diff].append(x.ljust(width))
        for i in xrange(line_diff):
            running_lines[i].append(' ' * width)
    # Output any remaining entries.
    if len(running_lines[0]) > 0:
        s.extend(_tall_list_row(running_lines, True))
    s.append(parens[1])
    return "\n".join(s)

# This helper function for _print_tall_list processes and outputs the
# contents of the running_lines array.
def _tall_list_row(running_lines, last_row=False):
    s=[]
    for i, line in enumerate(running_lines):
        if i + 1 != len(running_lines):
            sep, tail = '  ', ''
        else:
            # The commas go on the bottom line of this row.
            sep, tail = ', ', '' if last_row else ','
        s.append(sep.join(line) + tail)
    # Separate rows with a newline to make them stand out.
    if not last_row:
        s.append("")
    return s

def format_obj(obj):
    """
    Return a string if we want to print it in a special way; otherwise, return None.

    EXAMPLES::

        sage: import sage.misc.displayhook

    For most objects, nothing is done (None is returned):

        sage: sage.misc.displayhook.format_obj('Hello, world!')
        sage: sage.misc.displayhook.format_obj((1, 2, 3, 4))

    We demonstrate the special format for lists of matrices::

        sage: sage.misc.displayhook.format_obj( \
                [matrix([[1], [2]]), matrix([[3], [4]])])
        '[\n[1]  [3]\n[2], [4]\n]'
    """
    # We only apply the special formatting to lists (or tuples) where the first
    # element is a matrix, or an ArithmeticSubgroupElement (a thin wrapper
    # around a matrix). This should cover most cases.
    if isinstance(obj, (tuple, list)):
        from sage.matrix.matrix import is_Matrix
        from sage.modular.arithgroup.arithgroup_element import ArithmeticSubgroupElement
        if len(obj) > 0 and (is_Matrix(obj[0]) or isinstance(obj[0], ArithmeticSubgroupElement)):
            return _check_tall_list_and_format(obj)
    return None

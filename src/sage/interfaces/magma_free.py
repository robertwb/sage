#*****************************************************************************
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

class MagmaExpr(str):
    def __repr__(self):
        return str(self)

def magma_free_eval(code, strip=True, columns=0):
    """
    Use the free online MAGMA calculator to evaluate the given
    input code and return the answer as a string.

    LIMITATIONS: The code must evaluate in at most 20 seconds
    and there is a limitation on the amount of RAM.

    EXAMPLES:
        sage: magma_free("Factorization(9290348092384)")  # optional - internet
        [ <2, 5>, <290323377887, 1> ]
    """
    import urllib, httplib
    from xml.dom.minidom import parseString
    from string import join

    server = "magma.maths.usyd.edu.au"
    processPath = "/xml/calculator.xml"
    refererPath = "/calc/"
    refererUrl = "http://%s%s" % ( server, refererPath)
    code = "SetColumns(%s);\n"%columns + code
    params = urllib.urlencode({'input':code})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept":"Accept: text/html, application/xml, application/xhtml+xml", "Referer": refererUrl}
    conn = httplib.HTTPConnection(server)
    conn.request("POST", processPath, params, headers)
    response = conn.getresponse()
    results = response.read()
    conn.close()

    xmlDoc = parseString(results)
    res = []
    reslutsNodeList = xmlDoc.getElementsByTagName('results')
    if len(reslutsNodeList) > 0:
        reslutsNode = reslutsNodeList[0]
        lines = reslutsNode.getElementsByTagName('line')
        if len(reslutsNodeList) > 0:
            for line in lines:
                textNode = line.childNodes[0]
                res.append(textNode.data)
    res = join(res, "\n")

    class MagmaExpr(str):
        def __repr__(self):
            return str(self)
    return MagmaExpr(res)

class MagmaFree:
    """
    Evaluate MAGMA code without requiring that MAGMA be installed
    on your computer by using the free online MAGMA calculator.

    EXAMPLES:
        sage: magma_free("Factorization(9290348092384)")  # optional - internet
        [ <2, 5>, <290323377887, 1> ]
    """
    def eval(self, x, **kwds):
        return magma_free_eval(x)
    def __call__(self, code, strip=True, columns=0):
        return magma_free_eval(code, strip=strip, columns=columns)

magma_free = MagmaFree()

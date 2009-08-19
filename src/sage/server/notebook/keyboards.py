"""
Keyboard maps for the Sage Notebook

AUTHORS:
    -- Tom Boothby
    -- William Stein
"""

#############################################################################
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
#############################################################################

"""
The functions below return a block of javascript code that defines
global variables for every key that we could think of that works in
(almost) all systems.  Keys intentionally not captured are escape,
insert, delete, and F1-F12.  Support for the capture of ctrl, alt,
and shift is spotty; however, checking for this is necessary for
proper behavior in IE.

This file contains keyboard layouts for the following systems:
Firefox 1.5 windows, mac, linux
Opera 9 windows, mac, linux (linux only tested on opera 8)
IE 6 windows
Safari
Konqueror

We are deaf to the complaints of users of the following systems:
AOL
IE mac
LYNX / other command line browsers (Sage has a command line interface!)
the browser your cousin wrote for your sister's birthday

If you think that your browser deserves support, go to the following page:

http://sage.math.washington.edu/home/boothby/modular.old/www/keys_capture.html

and follow the directions you see there.  Copy the output, and email
it to boothby@u.washington.edu
"""


def get_keyboard(s):
    # keyboard_map is a dictionary defined at the bottom of this
    # file that maps os/browser codes to functions that give the
    # corresponding keymaps.
    if keyboard_map.has_key(s):
        codes = keyboard_map[s]()
    else:
        # Default in case something goes wrong.  This should
        # never get called.
        codes = keyboard_map['mm']()


    defaults = {'KEY_CTRLENTER':'KEY_ENTER'}

    # We now add in each default keycode if it isn't already present.
    # The point of this is that it allows us to easily alias keys to
    # predefined keys, but doesn't overwrite anything.
    for key, val in defaults.iteritems():
        if '%s ='%key not in codes:
            codes += '\n%s = %s'%(key,val)

    return codes





def keyboard_moz_win():
    return """
KEY_SHIFT = "16,16!"
KEY_CTRL = "20,20"
KEY_ALT = "18,18"
KEY_ESC = "27,0"
KEY_HOME = "36,0"
KEY_END = "35,0"
KEY_PGUP = "33,0"
KEY_PGDN = "34,0"
KEY_BKSPC = "8,8"
KEY_SPC = "0,32"
KEY_ENTER = "13,13"
KEY_RETURN = "13,13"
KEY_TAB = "9,0"
KEY_Q = "0,113"
KEY_W = "0,119"
KEY_E = "0,101"
KEY_R = "0,114"
KEY_T = "0,116"
KEY_Y = "0,121"
KEY_U = "0,117"
KEY_I = "0,105"
KEY_O = "0,111"
KEY_P = "0,112"
KEY_QQ = "0,81!"
KEY_WW = "0,87!"
KEY_EE = "0,69!"
KEY_RR = "0,82!"
KEY_TT = "0,84!"
KEY_YY = "0,89!"
KEY_UU = "0,85!"
KEY_II = "0,73!"
KEY_OO = "0,79!"
KEY_PP = "0,80!"
KEY_A = "0,97"
KEY_S = "0,115"
KEY_D = "0,100"
KEY_F = "0,102"
KEY_G = "0,103"
KEY_H = "0,104"
KEY_J = "0,106"
KEY_K = "0,107"
KEY_L = "0,108"
KEY_AA = "0,65!"
KEY_SS = "0,68!"
KEY_DD = "0,70!"
KEY_FF = "0,70!"
KEY_GG = "0,71!"
KEY_HH = "0,72!"
KEY_JJ = "0,74!"
KEY_KK = "0,75!"
KEY_LL = "0,76!"
KEY_Z = "0,122"
KEY_X = "0,120"
KEY_C = "0,99"
KEY_V = "0,118"
KEY_B = "0,98"
KEY_N = "0,110"
KEY_M = "0,109"
KEY_ZZ = "0,90!"
KEY_XX = "0,88!"
KEY_CC = "0,67!"
KEY_VV = "0,86!"
KEY_BB = "0,66!"
KEY_NN = "0,78!"
KEY_MM = "0,77!"
KEY_1 = "0,49"
KEY_2 = "0,50"
KEY_3 = "0,51"
KEY_4 = "0,52"
KEY_5 = "0,53"
KEY_6 = "0,54"
KEY_7 = "0,55"
KEY_8 = "0,56"
KEY_9 = "0,57"
KEY_0 = "0,48"
KEY_BANG = "0,33!"
KEY_AT = "0,64!"
KEY_HASH = "0,35!"
KEY_DOLLAR = "0,36!"
KEY_MOD = "0,37!"
KEY_CARET = "0,94!"
KEY_AMP = "0,38!"
KEY_AST = "0,42!"
KEY_LPAR = "0,40!"
KEY_RPAR = "0,41!"
KEY_MINUS = "0,45"
KEY_UNDER = "0,95!"
KEY_PLUS = "0,43!"
KEY_EQ = "0,61"
KEY_LBRACE = "0,123!"
KEY_RBRACE = "0,125!"
KEY_LBRACK = "0,91"
KEY_RBRACK = "0,93"
KEY_PIPE = "0,124!"
KEY_SLASH = "0,92"
KEY_COLON = "0,58!"
KEY_SEMI = "0,59"
KEY_QUOTE = "0,34!"
KEY_APOS = "0,39"
KEY_BSLASH = "191,0"
KEY_QUEST = "191,0!"
KEY_COMMA = "0,44"
KEY_DOT = "0,46"
KEY_TILDE = "0,126!"
KEY_TICK = "0,96"
KEY_LT = "0,60!"
KEY_GT = "0,62!"
KEY_LEFT = "37,0"
KEY_UP = "38,0"
KEY_RIGHT = "39,0"
KEY_DOWN = "40,0"
    """



def keyboard_moz_lin():
    return """
KEY_SHIFT = "16,16"
KEY_CTRL = "17,17"
KEY_ALT = "18,18"
KEY_ESC = "27,0"
KEY_HOME = "36,0"
KEY_END = "35,0"
KEY_PGUP = "33,0"
KEY_PGDN = "34,0"
KEY_BKSPC = "8,8"
KEY_SPC = "0,32"
KEY_ENTER = "13,13"
KEY_RETURN = "13,13"
KEY_TAB = "9,0"
KEY_Q = "0,113"
KEY_W = "0,119"
KEY_E = "0,101"
KEY_R = "0,114"
KEY_T = "0,116"
KEY_Y = "0,121"
KEY_U = "0,117"
KEY_I = "0,105"
KEY_O = "0,111"
KEY_P = "0,112"
KEY_QQ = "0,81!"
KEY_WW = "0,87!"
KEY_EE = "0,69!"
KEY_RR = "0,82!"
KEY_TT = "0,84!"
KEY_YY = "0,89!"
KEY_UU = "0,85!"
KEY_II = "0,73!"
KEY_OO = "0,79!"
KEY_PP = "0,80!"
KEY_A = "0,97"
KEY_S = "0,115"
KEY_D = "0,100"
KEY_F = "0,102"
KEY_G = "0,103"
KEY_H = "0,104"
KEY_J = "0,106"
KEY_K = "0,107"
KEY_L = "0,108"
KEY_AA = "0,65!"
KEY_SS = "0,83!"
KEY_DD = "0,68!"
KEY_FF = "0,70!"
KEY_GG = "0,71!"
KEY_HH = "0,72!"
KEY_JJ = "0,74!"
KEY_KK = "0,75!"
KEY_LL = "0,76!"
KEY_Z = "0,122"
KEY_X = "0,120"
KEY_C = "0,99"
KEY_V = "0,118"
KEY_B = "0,98"
KEY_N = "0,110"
KEY_M = "0,109"
KEY_ZZ = "0,90!"
KEY_XX = "0,88!"
KEY_CC = "0,67!"
KEY_VV = "0,86!"
KEY_BB = "0,66!"
KEY_NN = "0,78!"
KEY_MM = "0,77!"
KEY_1 = "0,49"
KEY_2 = "0,50"
KEY_3 = "0,51"
KEY_4 = "0,52"
KEY_5 = "0,53"
KEY_6 = "0,54"
KEY_7 = "0,55"
KEY_8 = "0,56"
KEY_9 = "0,57"
KEY_0 = "0,48"
KEY_BANG = "0,33!"
KEY_AT = "0,64!"
KEY_HASH = "0,35!"
KEY_DOLLAR = "0,36!"
KEY_MOD = "0,37!"
KEY_CARET = "0,94!"
KEY_AMP = "0,38!"
KEY_AST = "0,42!"
KEY_LPAR = "0,40!"
KEY_RPAR = "0,41!"
KEY_MINUS = "0,45"
KEY_UNDER = "0,95!"
KEY_PLUS = "0,43!"
KEY_EQ = "0,61"
KEY_LBRACE = "0,123!"
KEY_RBRACE = "0,125!"
KEY_LBRACK = "0,91"
KEY_RBRACK = "0,93"
KEY_PIPE = "0,124!"
KEY_SLASH = "0,92"
KEY_COLON = "0,58!"
KEY_SEMI = "0,59"
KEY_QUOTE = "0,34!"
KEY_APOS = "0,39"
KEY_BSLASH = "0,47"
KEY_QUEST = "0,63!"
KEY_COMMA = "0,44"
KEY_DOT = "0,46"
KEY_TILDE = "0,126!"
KEY_TICK = "0,96"
KEY_LT = "0,60!"
KEY_GT = "0,62!"
KEY_LEFT = "37,0"
KEY_UP = "38,0"
KEY_RIGHT = "39,0"
KEY_DOWN = "40,0"
    """



def keyboard_moz_mac():
    return """
KEY_SHIFT = ""
KEY_CTRL = ""
KEY_ALT = ""
KEY_ESC = "27,0"
KEY_HOME = "36,0"
KEY_END = "35,0"
KEY_PGUP = "33,0"
KEY_PGDN = "34,0"
KEY_BKSPC = "8,8"
KEY_SPC = "0,32"
KEY_ENTER = "13,13"
KEY_RETURN = "13,13"
KEY_CTRLENTER = "77,0"
KEY_TAB = "9,0"
KEY_Q = "0,113"
KEY_W = "0,119"
KEY_E = "0,101"
KEY_R = "0,114"
KEY_T = "0,116"
KEY_Y = "0,121"
KEY_U = "0,117"
KEY_I = "0,105"
KEY_O = "0,111"
KEY_P = "0,112"
KEY_QQ = "0,81!"
KEY_WW = "0,87!"
KEY_EE = "0,69!"
KEY_RR = "0,82!"
KEY_TT = "0,84!"
KEY_YY = "0,89!"
KEY_UU = "0,85!"
KEY_II = "0,73!"
KEY_OO = "0,79!"
KEY_PP = "0,80!"
KEY_A = "0,97"
KEY_S = "0,115"
KEY_D = "0,100"
KEY_F = "0,102"
KEY_G = "0,103"
KEY_H = "0,104"
KEY_J = "0,106"
KEY_K = "0,107"
KEY_L = "0,108"
KEY_AA = "0,65!"
KEY_SS = "0,83!"
KEY_DD = "0,68!"
KEY_FF = "0,70!"
KEY_GG = "0,71!"
KEY_HH = "0,72!"
KEY_JJ = "0,74!"
KEY_KK = "0,75!"
KEY_LL = "0,76!"
KEY_Z = "0,122"
KEY_X = "0,120"
KEY_C = "0,99"
KEY_V = "0,118"
KEY_B = "0,98"
KEY_N = "0,110"
KEY_M = "0,109"
KEY_ZZ = "0,90!"
KEY_XX = "0,88!"
KEY_CC = "0,67!"
KEY_VV = "0,86!"
KEY_BB = "0,66!"
KEY_NN = "0,78!"
KEY_MM = "0,77!"
KEY_1 = "0,49"
KEY_2 = "0,50"
KEY_3 = "0,51"
KEY_4 = "0,52"
KEY_5 = "0,53"
KEY_6 = "0,54"
KEY_7 = "0,55"
KEY_8 = "0,56"
KEY_9 = "0,57"
KEY_0 = "0,48"
KEY_BANG = "0,33!"
KEY_AT = "0,64!"
KEY_HASH = "0,35!"
KEY_DOLLAR = "0,36!"
KEY_MOD = "0,37!"
KEY_CARET = "0,94!"
KEY_AMP = "0,38!"
KEY_AST = "0,42!"
KEY_LPAR = "0,40!"
KEY_RPAR = "0,41!"
KEY_MINUS = "0,45"
KEY_UNDER = "0,95!"
KEY_PLUS = "0,43!"
KEY_EQ = "0,61"
KEY_LBRACE = "0,123!"
KEY_RBRACE = "0,125!"
KEY_LBRACK = "0,91"
KEY_RBRACK = "0,93"
KEY_PIPE = "0,124!"
KEY_SLASH = "0,92"
KEY_COLON = "0,58!"
KEY_SEMI = "0,59"
KEY_QUOTE = "0,34!"
KEY_APOS = "0,39"
KEY_BSLASH = "0,47"
KEY_QUEST = "0,63!"
KEY_COMMA = "0,44"
KEY_DOT = "0,46"
KEY_TILDE = "0,126!"
KEY_TICK = "0,96"
KEY_LT = "0,60!"
KEY_GT = "0,62!"
KEY_LEFT = "37,0"
KEY_UP = "38,0"
KEY_RIGHT = "39,0"
KEY_DOWN = "40,0"
    """

def keyboard_op_win():
    return """
KEY_SHIFT = "16,16!"
KEY_CTRL = "20,20"
KEY_ALT = ""
KEY_ESC = "27,27"
KEY_HOME = "36,36"
KEY_END = "35,35"
KEY_PGUP = "33,0"
KEY_PGDN = "34,0"
KEY_BKSPC = "8,8"
KEY_SPC = "32,32"
KEY_ENTER = "13,13"
KEY_RETURN = "13,13"
KEY_TAB = "9,9"
KEY_Q = "81,81"
KEY_W = "87,87"
KEY_E = "69,69"
KEY_R = "82,82"
KEY_T = "84,84"
KEY_Y = "89,89"
KEY_U = "85,85"
KEY_I = "73,73"
KEY_O = "79,79"
KEY_P = "80,80"
KEY_QQ = "113,113!"
KEY_WW = "119,119!"
KEY_EE = "101,101!"
KEY_RR = "114,114!"
KEY_TT = "116,116!"
KEY_YY = "121,121!"
KEY_UU = "117,117!"
KEY_II = "105,105!"
KEY_OO = "111,111!"
KEY_PP = "112,112!"
KEY_A = "65,65"
KEY_S = "83,83"
KEY_D = "68,68"
KEY_F = "70,70"
KEY_G = "71,71"
KEY_H = "72,72"
KEY_J = "74,74"
KEY_K = "75,75"
KEY_L = "76,76"
KEY_AA = "97,97!"
KEY_SS = "115,115!"
KEY_DD = "100,100!"
KEY_FF = "102,102!"
KEY_GG = "103,103!"
KEY_HH = "104,104!"
KEY_JJ = "106,106!"
KEY_KK = "107,107!"
KEY_LL = "108,108!"
KEY_Z = "90,90"
KEY_X = "88,88"
KEY_C = "67,67"
KEY_V = "86,86"
KEY_B = "66,66"
KEY_N = "78,78"
KEY_M = "77,77"
KEY_ZZ = "122,122!"
KEY_XX = "120,120!"
KEY_CC = "99,99!"
KEY_VV = "118,118!"
KEY_BB = "98,98!"
KEY_NN = "110,110!"
KEY_MM = "109,109!"
KEY_1 = "49,49"
KEY_2 = "50,50"
KEY_3 = "51,51"
KEY_4 = "52,52"
KEY_5 = "53,53"
KEY_6 = "54,54"
KEY_7 = "55,55"
KEY_8 = "56,56"
KEY_9 = "57,57"
KEY_0 = "48,48"
KEY_BANG = "33,33!"
KEY_AT = "64,64!"
KEY_HASH = "35,35!"
KEY_DOLLAR = "36,36!"
KEY_MOD = "37,37!"
KEY_CARET = "94,94!"
KEY_AMP = "38,38!"
KEY_AST = "42,42!"
KEY_LPAR = "40,40!"
KEY_RPAR = "41,41!"
KEY_MINUS = "45,45"
KEY_UNDER = "95,95!"
KEY_PLUS = "43,43!"
KEY_EQ = "61,61"
KEY_LBRACE = "123,123!"
KEY_RBRACE = "125,125!"
KEY_LBRACK = "91,91"
KEY_RBRACK = "93,93"
KEY_PIPE = "124,124!"
KEY_SLASH = "92,92"
KEY_COLON = "58,58!"
KEY_SEMI = "59,59"
KEY_QUOTE = "34,34!"
KEY_APOS = "39,39"
KEY_BSLASH = "47,47"
KEY_QUEST = "63,63!"
KEY_COMMA = "44,44"
KEY_DOT = "46,46"
KEY_TILDE = "126,126!"
KEY_TICK = "96,96"
KEY_LT = "60,60!"
KEY_GT = "62,62!"
KEY_LEFT = "37,0"
KEY_UP = "38,0"
KEY_RIGHT = "39,0"
KEY_DOWN = "40,0"
    """




def keyboard_op_lin():
    return """
KEY_SHIFT = "0,0"
KEY_CTRL = "0,0"
KEY_ALT = "0,0"
KEY_ESC = "27,27"
KEY_HOME = ""
KEY_END = ""
KEY_PGUP = "33,0"
KEY_PGDN = "34,0"
KEY_BKSPC = "8,8"
KEY_SPC = "32,32"
KEY_ENTER = "13,13"
KEY_RETURN = "13,13"
KEY_TAB = "9,9"
KEY_Q = "113,113"
KEY_W = "119,119"
KEY_E = "101,101"
KEY_R = "114,114"
KEY_T = "116,116"
KEY_Y = "121,121"
KEY_U = "117,117"
KEY_I = "105,105"
KEY_O = "111,111"
KEY_P = "112,112"
KEY_QQ = "81,81!"
KEY_WW = "87,87!"
KEY_EE = "69,69!"
KEY_RR = "82,82!"
KEY_TT = "84,84!"
KEY_YY = "89,89!"
KEY_UU = "85,85!"
KEY_II = "73,73!"
KEY_OO = "79,79!"
KEY_PP = "80,80!"
KEY_A = "97,97"
KEY_S = "115,115"
KEY_D = "100,100"
KEY_F = "102,102"
KEY_G = "103,103"
KEY_H = "104,104"
KEY_J = "106,106"
KEY_K = "107,107"
KEY_L = "108,108"
KEY_AA = "65,65!"
KEY_SS = "83,83!"
KEY_DD = "68,68!"
KEY_FF = "70,70!"
KEY_GG = "71,71!"
KEY_HH = "72,72!"
KEY_JJ = "74,74!"
KEY_KK = "75,75!"
KEY_LL = "76,76!"
KEY_Z = "122,122"
KEY_X = "120,120"
KEY_C = "99,99"
KEY_V = "118,118"
KEY_B = "98,98"
KEY_N = "110,110"
KEY_M = "109,109"
KEY_ZZ = "90,90!"
KEY_XX = "88,88!"
KEY_CC = "67,67!"
KEY_VV = "86,86!"
KEY_BB = "66,66!"
KEY_NN = "78,78!"
KEY_MM = "77,77!"
KEY_1 = "49,49"
KEY_2 = "50,50"
KEY_3 = "51,51"
KEY_4 = "52,52"
KEY_5 = "53,53"
KEY_6 = "54,54"
KEY_7 = "55,55"
KEY_8 = "56,56"
KEY_9 = "57,57"
KEY_0 = "48,48"
KEY_BANG = "33,33!"
KEY_AT = "64,64!"
KEY_HASH = "35,35!"
KEY_DOLLAR = "36,36!"
KEY_MOD = "37,37!"
KEY_CARET = "94,94!"
KEY_AMP = "38,38!"
KEY_AST = "42,42!"
KEY_LPAR = "40,40!"
KEY_RPAR = "41,41!"
KEY_MINUS = "45,45"
KEY_UNDER = "95,95!"
KEY_PLUS = "43,43!"
KEY_EQ = "61,61"
KEY_LBRACE = "123,123!"
KEY_RBRACE = "125,125!"
KEY_LBRACK = "91,91"
KEY_RBRACK = "93,93"
KEY_PIPE = "124,124!"
KEY_SLASH = "92,92"
KEY_COLON = "58,58!"
KEY_SEMI = "59,59"
KEY_QUOTE = "34,34!"
KEY_APOS = "39,39"
KEY_BSLASH = "47,47"
KEY_QUEST = "63,63!"
KEY_COMMA = "44,44"
KEY_DOT = "46,46"
KEY_TILDE = "126,126!"
KEY_TICK = "96,96"
KEY_LT = "60,60!"
KEY_GT = "62,62!"
KEY_LEFT = "37,0"
KEY_UP = "38,0"
KEY_RIGHT = "39,0"
KEY_DOWN = "40,0"
    """

# You had KEY_CTRL = "20,20", but it's "0,0"
def keyboard_op_mac():
    return """
KEY_SHIFT = "16,16"
KEY_CTRL = "0,0"
KEY_ALT = "18,18"
KEY_ESC = "27,27"
KEY_HOME = "36,36"
KEY_END = "35,35"
KEY_PGUP = "33,0"
KEY_PGDN = "34,0"
KEY_BKSPC = "8,8"
KEY_SPC = "32,32"
KEY_ENTER = "13,13"
KEY_RETURN = "13,13"
KEY_TAB = "9,9"
KEY_Q = "113,113"
KEY_W = "119,119"
KEY_E = "101,101"
KEY_R = "114,114"
KEY_T = "116,116"
KEY_Y = "121,121"
KEY_U = "117,117"
KEY_I = "105,105"
KEY_O = "111,111"
KEY_P = "112,112"
KEY_QQ = "81,81!"
KEY_WW = "87,87!"
KEY_EE = "69,69!"
KEY_RR = "82,82!"
KEY_TT = "84,84!"
KEY_YY = "89,89!"
KEY_UU = "85,85!"
KEY_II = "73,73!"
KEY_OO = "79,79!"
KEY_PP = "80,80!"
KEY_A = "97,97"
KEY_S = "115,115"
KEY_D = "100,100"
KEY_F = "102,102"
KEY_G = "103,103"
KEY_H = "104,104"
KEY_J = "106,106"
KEY_K = "107,107"
KEY_L = "108,108"
KEY_AA = "65,65!"
KEY_SS = "83,83!"
KEY_DD = "68,68!"
KEY_FF = "70,70!"
KEY_GG = "71,71!"
KEY_HH = "72,72!"
KEY_JJ = "74,74!"
KEY_KK = "75,75!"
KEY_LL = "76,76!"
KEY_Z = "122,122"
KEY_X = "120,120"
KEY_C = "99,99"
KEY_V = "118,118"
KEY_B = "98,98"
KEY_N = "110,110"
KEY_M = "109,109"
KEY_ZZ = "90,90!"
KEY_XX = "88,88!"
KEY_CC = "67,67!"
KEY_VV = "86,86!"
KEY_BB = "66,66!"
KEY_NN = "78,78!"
KEY_MM = "77,77!"
KEY_1 = "49,49"
KEY_2 = "50,50"
KEY_3 = "51,51"
KEY_4 = "52,52"
KEY_5 = "53,53"
KEY_6 = "54,54"
KEY_7 = "55,55"
KEY_8 = "56,56"
KEY_9 = "57,57"
KEY_0 = "48,48"
KEY_BANG = "33,33!"
KEY_AT = "64,64!"
KEY_HASH = "35,35!"
KEY_DOLLAR = "36,36!"
KEY_MOD = "37,37!"
KEY_CARET = "94,94!"
KEY_AMP = "38,38!"
KEY_AST = "42,42!"
KEY_LPAR = "40,40!"
KEY_RPAR = "41,41!"
KEY_MINUS = "45,45"
KEY_UNDER = "95,95!"
KEY_PLUS = "43,43!"
KEY_EQ = "61,61"
KEY_LBRACE = "123,123!"
KEY_RBRACE = "125,125!"
KEY_LBRACK = "91,91"
KEY_RBRACK = "93,93"
KEY_PIPE = "124,124!"
KEY_SLASH = "92,92"
KEY_COLON = "58,58!"
KEY_SEMI = "59,59"
KEY_QUOTE = "34,34!"
KEY_APOS = "39,39"
KEY_BSLASH = "47,47"
KEY_QUEST = "63,63!"
KEY_COMMA = "44,44"
KEY_DOT = "46,46"
KEY_TILDE = "126,126!"
KEY_TICK = "96,96"
KEY_LT = "60,60!"
KEY_GT = "62,62!"
KEY_LEFT = "37,0"
KEY_UP = "38,0"
KEY_RIGHT = "39,0"
KEY_DOWN = "40,0"
    """

def keyboard_saf():
    return """
KEY_SHIFT = ""
KEY_CTRL = ""
KEY_ALT = ""
KEY_ESC = "27,27"
KEY_HOME = "63273,63273"
KEY_END = "63275,63275"
KEY_PGUP = "63276,63276"
KEY_PGDN = "63277,63277"
KEY_BKSPC = "8,8"
KEY_SPC = "32,32"
KEY_ENTER = "3,3"
KEY_RETURN = "13,13"
KEY_TAB = "9,9"
KEY_Q = "113,113"
KEY_W = "119,119"
KEY_E = "101,101"
KEY_R = "114,114"
KEY_T = "116,116"
KEY_Y = "121,121"
KEY_U = "117,117"
KEY_I = "105,105"
KEY_O = "111,111"
KEY_P = "112,112"
KEY_QQ = "81,81!"
KEY_WW = "87,87!"
KEY_EE = "69,69!"
KEY_RR = "82,82!"
KEY_TT = "84,84!"
KEY_YY = "89,89!"
KEY_UU = "85,85!"
KEY_II = "73,73!"
KEY_OO = "79,79!"
KEY_PP = "80,80!"
KEY_A = "97,97"
KEY_S = "115,115"
KEY_D = "100,100"
KEY_F = "102,102"
KEY_G = "103,103"
KEY_H = "104,104"
KEY_J = "106,106"
KEY_K = "107,107"
KEY_L = "108,108"
KEY_AA = "65,65!"
KEY_SS = "83,83!"
KEY_DD = "68,68!"
KEY_FF = "70,70!"
KEY_GG = "71,71!"
KEY_HH = "72,72!"
KEY_JJ = "74,74!"
KEY_KK = "75,75!"
KEY_LL = "76,76!"
KEY_Z = "122,122"
KEY_X = "120,120"
KEY_C = "99,99"
KEY_V = "118,118"
KEY_B = "98,98"
KEY_N = "110,110"
KEY_M = "109,109"
KEY_ZZ = "90,90!"
KEY_XX = "88,88!"
KEY_CC = "67,67!"
KEY_VV = "86,86!"
KEY_BB = "66,66!"
KEY_NN = "78,78!"
KEY_MM = "77,77!"
KEY_1 = "49,49"
KEY_2 = "50,50"
KEY_3 = "51,51"
KEY_4 = "52,52"
KEY_5 = "53,53"
KEY_6 = "54,54"
KEY_7 = "55,55"
KEY_8 = "56,56"
KEY_9 = "57,57"
KEY_0 = "48,48"
KEY_BANG = "33,33!"
KEY_AT = "64,64!"
KEY_HASH = "35,35!"
KEY_DOLLAR = "36,36!"
KEY_MOD = "37,37!"
KEY_CARET = "94,94!"
KEY_AMP = "38,38!"
KEY_AST = "42,42!"
KEY_LPAR = "40,40!"
KEY_RPAR = "41,41!"
KEY_MINUS = "45,45"
KEY_UNDER = "95,95!"
KEY_PLUS = "43,43!"
KEY_EQ = "61,61"
KEY_LBRACE = "123,123!"
KEY_RBRACE = "125,125!"
KEY_LBRACK = "91,91"
KEY_RBRACK = "93,93"
KEY_PIPE = "124,124!"
KEY_SLASH = "92,92"
KEY_COLON = "186,186!"
KEY_SEMI = "186,186"
KEY_QUOTE = "34,34!"
KEY_APOS = "39,39"
KEY_BSLASH = "47,47"
KEY_QUEST = "63,63!"
KEY_COMMA = "44,44"
KEY_DOT = "46,46"
KEY_TILDE = "126,126!"
KEY_TICK = "96,96"
KEY_LT = "60,60!"
KEY_GT = "62,62!"
KEY_LEFT = "37,37"
KEY_UP = "38,38"
KEY_RIGHT = "39,39"
KEY_DOWN = "40,40"
    """



def keyboard_konq():
    return """
KEY_SHIFT = "16,16"
KEY_CTRL = "20,20"
KEY_ALT = "18,18"
KEY_ESC = "27,27"
KEY_HOME = "36,36"
KEY_END = "35,35"
KEY_PGUP = "33,33"
KEY_PGDN = "34,34"
KEY_BKSPC = "8,8"
KEY_SPC = "32,32"
KEY_ENTER = "13,13"
KEY_RETURN = "13,13"
KEY_TAB = "9,9"
KEY_Q = "113,113"
KEY_W = "119,119"
KEY_E = "101,101"
KEY_R = "114,114"
KEY_T = "116,116"
KEY_Y = "121,121"
KEY_U = "117,117"
KEY_I = "105,105"
KEY_O = "111,111"
KEY_P = "112,112"
KEY_QQ = "81,81!"
KEY_WW = "87,87!"
KEY_EE = "69,69!"
KEY_RR = "82,82!"
KEY_TT = "84,84!"
KEY_YY = "89,89!"
KEY_UU = "85,85!"
KEY_II = "73,73!"
KEY_OO = "79,79!"
KEY_PP = "80,80!"
KEY_A = "97,97"
KEY_S = "115,115"
KEY_D = "100,100"
KEY_F = "102,102"
KEY_G = "103,103"
KEY_H = "104,104"
KEY_J = "106,106"
KEY_K = "107,107"
KEY_L = "108,108"
KEY_AA = "65,65!"
KEY_SS = "83,83!"
KEY_DD = "68,68!"
KEY_FF = "70,70!"
KEY_GG = "71,71!"
KEY_HH = "72,72!"
KEY_JJ = "74,74!"
KEY_KK = "75,75!"
KEY_LL = "76,76!"
KEY_Z = "122,122"
KEY_X = "120,120"
KEY_C = "99,99"
KEY_V = "118,118"
KEY_B = "98,98"
KEY_N = "110,110"
KEY_M = "109,109"
KEY_ZZ = "90,90!"
KEY_XX = "88,88!"
KEY_CC = "67,67!"
KEY_VV = "86,86!"
KEY_BB = "66,66!"
KEY_NN = "78,78!"
KEY_MM = "77,77!"
KEY_1 = "49,49"
KEY_2 = "50,50"
KEY_3 = "51,51"
KEY_4 = "52,52"
KEY_5 = "53,53"
KEY_6 = "54,54"
KEY_7 = "55,55"
KEY_8 = "56,56"
KEY_9 = "57,57"
KEY_0 = "48,48"
KEY_BANG = "33,33!"
KEY_AT = "64,64!"
KEY_HASH = "35,35!"
KEY_DOLLAR = "36,36!"
KEY_MOD = "37,37!"
KEY_CARET = "94,94!"
KEY_AMP = "38,38!"
KEY_AST = "42,42!"
KEY_LPAR = "40,40!"
KEY_RPAR = "41,41!"
KEY_MINUS = "45,45"
KEY_UNDER = "95,95!"
KEY_PLUS = "43,43!"
KEY_EQ = "61,61"
KEY_LBRACE = "123,123!"
KEY_RBRACE = "125,125!"
KEY_LBRACK = "91,91"
KEY_RBRACK = "93,93"
KEY_PIPE = "124,124!"
KEY_SLASH = "92,92"
KEY_COLON = "58,58!"
KEY_SEMI = "59,59"
KEY_QUOTE = "34,34!"
KEY_APOS = "39,39"
KEY_BSLASH = "47,47"
KEY_QUEST = "63,63!"
KEY_COMMA = "44,44"
KEY_DOT = "46,46"
KEY_TILDE = "126,126!"
KEY_TICK = "96,96"
KEY_LT = "60,60!"
KEY_GT = "62,62!"
KEY_LEFT = "37,37"
KEY_UP = "38,38"
KEY_RIGHT = "39,39"
KEY_DOWN = "40,40"
    """

def keyboard_ie():
    return """
KEY_SHIFT = "16,undefined!"
KEY_CTRL = "20,undefined"
KEY_ALT = "18,undefined"
KEY_ESC = "27,undefined"
KEY_HOME = "36,undefined"
KEY_END = "35,undefined"
KEY_PGUP = "33,undefined"
KEY_PGDN = "34,undefined"
KEY_BKSPC = "8,undefined"
KEY_SPC = "32,undefined"
KEY_ENTER = "13,undefined"
KEY_RETURN = "13,undefined"
KEY_TAB = "9,undefined"
KEY_Q = "81,undefined"
KEY_W = "87,undefined"
KEY_E = "69,undefined"
KEY_R = "82,undefined"
KEY_T = "84,undefined"
KEY_Y = "89,undefined"
KEY_U = "85,undefined"
KEY_I = "73,undefined"
KEY_O = "79,undefined"
KEY_P = "80,undefined"
KEY_QQ = "81,undefined!"
KEY_WW = "87,undefined!"
KEY_EE = "69,undefined!"
KEY_RR = "82,undefined!"
KEY_TT = "84,undefined!"
KEY_YY = "89,undefined!"
KEY_UU = "85,undefined!"
KEY_II = "73,undefined!"
KEY_OO = "79,undefined!"
KEY_PP = "80,undefined!"
KEY_A = "65,undefined"
KEY_S = "83,undefined"
KEY_D = "68,undefined"
KEY_F = "70,undefined"
KEY_G = "71,undefined"
KEY_H = "72,undefined"
KEY_J = "74,undefined"
KEY_K = "75,undefined"
KEY_L = "76,undefined"
KEY_AA = "65,undefined!"
KEY_SS = "83,undefined!"
KEY_DD = "68,undefined!"
KEY_FF = "70,undefined!"
KEY_GG = "71,undefined!"
KEY_HH = "72,undefined!"
KEY_JJ = "74,undefined!"
KEY_KK = "75,undefined!"
KEY_LL = "76,undefined!"
KEY_Z = "90,undefined"
KEY_X = "88,undefined"
KEY_C = "67,undefined"
KEY_V = "86,undefined"
KEY_B = "66,undefined"
KEY_N = "78,undefined"
KEY_M = "77,undefined"
KEY_ZZ = "90,undefined!"
KEY_XX = "88,undefined!"
KEY_CC = "67,undefined!"
KEY_VV = "86,undefined!"
KEY_BB = "66,undefined!"
KEY_NN = "78,undefined!"
KEY_MM = "77,undefined!"
KEY_1 = "49,undefined"
KEY_2 = "50,undefined"
KEY_3 = "51,undefined"
KEY_4 = "52,undefined"
KEY_5 = "53,undefined"
KEY_6 = "54,undefined"
KEY_7 = "55,undefined"
KEY_8 = "56,undefined"
KEY_9 = "57,undefined"
KEY_0 = "48,undefined"
KEY_BANG = "49,undefined!"
KEY_AT = "50,undefined!"
KEY_HASH = "51,undefined!"
KEY_DOLLAR = "52,undefined!"
KEY_MOD = "53,undefined!"
KEY_CARET = "54,undefined!"
KEY_AMP = "55,undefined!"
KEY_AST = "56,undefined!"
KEY_LPAR = "57,undefined!"
KEY_RPAR = "48,undefined!"
KEY_MINUS = "189,undefined"
KEY_UNDER = "189,undefined!"
KEY_PLUS = "187,undefined!"
KEY_EQ = "187,undefined"
KEY_LBRACE = "219,undefined!"
KEY_RBRACE = "221,undefined!"
KEY_LBRACK = "219,undefined"
KEY_RBRACK = "221,undefined"
KEY_PIPE = "220,undefined!"
KEY_SLASH = "220,undefined"
KEY_COLON = "186,undefined!"
KEY_SEMI = "186,undefined"
KEY_QUOTE = "222,undefined!"
KEY_APOS = "222,undefined"
KEY_BSLASH = "191,undefined"
KEY_QUEST = "191,undefined!"
KEY_COMMA = "188,undefined"
KEY_DOT = "190,undefined"
KEY_TILDE = "192,undefined!"
KEY_TICK = "192,undefined"
KEY_LT = "188,undefined!"
KEY_GT = "190,undefined!"
KEY_LEFT = "37,undefined"
KEY_UP = "38,undefined"
KEY_RIGHT = "39,undefined"
KEY_DOWN = "40,undefined"
    """

# Define mapping from 2-letter OS/Browser codes to the
# functions defined above.

keyboard_map = {'mw':keyboard_moz_win,
                'ml':keyboard_moz_lin,
                'mm':keyboard_moz_mac,
                'ow':keyboard_op_win,
                'ol':keyboard_op_lin,
                'om':keyboard_op_mac,
                'sm':keyboard_saf,
                'kl':keyboard_konq,
                'iw':keyboard_ie}

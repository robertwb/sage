/*
 *  jsMath-fallback-symbols.js
 *
 *  Part of the jsMath package for mathematics on the web.
 *
 *  This file makes changes needed to use image fonts for symbols
 *  but standard native fonts for letters and numbers.
 *
 *  ---------------------------------------------------------------------
 *
 *  Copyright 2004-2006 by Davide P. Cervone
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

jsMath.Add(jsMath.Img,{
  UpdateTeXFonts: function (change) {
    for (var font in change) {
      for (var code in change[font]) {
        jsMath.TeX[font][code] = change[font][code];
        jsMath.TeX[font][code].tclass = 'i' + font;
      }
    }
  }
});


jsMath.Img.UpdateTeXFonts({
  cmr10:  {
    '33': {c: '!', lig: {'96': 60}},
    '35': {c: '#'},
    '36': {c: '$'},
    '37': {c: '%'},
    '38': {c: '&amp;'},
    '40': {c: '(', d:.2},
    '41': {c: ')', d:.2},
    '42': {c: '*', d:-.3},
    '43': {c: '+', a:.1},
    '44': {c: ',', a:-.3},
    '45': {c: '-', a:0, lig: {'45': 123}},
    '46': {c: '.', a:-.25},
    '47': {c: '/'},
    '48': {c: '0'},
    '49': {c: '1'},
    '50': {c: '2'},
    '51': {c: '3'},
    '52': {c: '4'},
    '53': {c: '5'},
    '54': {c: '6'},
    '55': {c: '7'},
    '56': {c: '8'},
    '57': {c: '9'},
    '58': {c: ':'},
    '59': {c: ';'},
    '61': {c: '=', a:0, d:-.1},
    '63': {c: '?', lig: {'96': 62}},
    '64': {c: '@'},
    '65': {c: 'A', krn: {'116': -0.0278, '67': -0.0278, '79': -0.0278, '71': -0.0278, '85': -0.0278, '81': -0.0278, '84': -0.0833, '89': -0.0833, '86': -0.111, '87': -0.111}},
    '66': {c: 'B'},
    '67': {c: 'C'},
    '68': {c: 'D', krn: {'88': -0.0278, '87': -0.0278, '65': -0.0278, '86': -0.0278, '89': -0.0278}},
    '69': {c: 'E'},
    '70': {c: 'F', krn: {'111': -0.0833, '101': -0.0833, '117': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.111, '79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '71': {c: 'G'},
    '72': {c: 'H'},
    '73': {c: 'I', krn: {'73': 0.0278}},
    '74': {c: 'J'},
    '75': {c: 'K', krn: {'79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '76': {c: 'L', krn: {'84': -0.0833, '89': -0.0833, '86': -0.111, '87': -0.111}},
    '77': {c: 'M'},
    '78': {c: 'N'},
    '79': {c: 'O', krn: {'88': -0.0278, '87': -0.0278, '65': -0.0278, '86': -0.0278, '89': -0.0278}},
    '80': {c: 'P', krn: {'65': -0.0833, '111': -0.0278, '101': -0.0278, '97': -0.0278, '46': -0.0833, '44': -0.0833}},
    '81': {c: 'Q', d: 1},
    '82': {c: 'R', krn: {'116': -0.0278, '67': -0.0278, '79': -0.0278, '71': -0.0278, '85': -0.0278, '81': -0.0278, '84': -0.0833, '89': -0.0833, '86': -0.111, '87': -0.111}},
    '83': {c: 'S'},
    '84': {c: 'T', krn: {'121': -0.0278, '101': -0.0833, '111': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.0833, '117': -0.0833}},
    '85': {c: 'U'},
    '86': {c: 'V', ic: 0.0139, krn: {'111': -0.0833, '101': -0.0833, '117': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.111, '79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '87': {c: 'W', ic: 0.0139, krn: {'111': -0.0833, '101': -0.0833, '117': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.111, '79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '88': {c: 'X', krn: {'79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '89': {c: 'Y', ic: 0.025, krn: {'101': -0.0833, '111': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.0833, '117': -0.0833}},
    '90': {c: 'Z'},
    '91': {c: '[', d:.1},
    '93': {c: ']', d:.1},
    '97': {c: 'a', a:0, krn: {'118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '98': {c: 'b', krn: {'101': 0.0278, '111': 0.0278, '120': -0.0278, '100': 0.0278, '99': 0.0278, '113': 0.0278, '118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '99': {c: 'c', a:0, krn: {'104': -0.0278, '107': -0.0278}},
    '100': {c: 'd'},
    '101': {c: 'e', a:0},
    '102': {c: 'f', ic: 0.0778, krn: {'39': 0.0778, '63': 0.0778, '33': 0.0778, '41': 0.0778, '93': 0.0778}, lig: {'105': 12, '102': 11, '108': 13}},
    '103': {c: 'g', a:0, d:.2, ic: 0.0139, krn: {'106': 0.0278}},
    '104': {c: 'h', krn: {'116': -0.0278, '117': -0.0278, '98': -0.0278, '121': -0.0278, '118': -0.0278, '119': -0.0278}},
    '105': {c: 'i'},
    '106': {c: 'j', d:1},
    '107': {c: 'k', krn: {'97': -0.0556, '101': -0.0278, '97': -0.0278, '111': -0.0278, '99': -0.0278}},
    '108': {c: 'l'},
    '109': {c: 'm', a:0, krn: {'116': -0.0278, '117': -0.0278, '98': -0.0278, '121': -0.0278, '118': -0.0278, '119': -0.0278}},
    '110': {c: 'n', a:0, krn: {'116': -0.0278, '117': -0.0278, '98': -0.0278, '121': -0.0278, '118': -0.0278, '119': -0.0278}},
    '111': {c: 'o', a:0, krn: {'101': 0.0278, '111': 0.0278, '120': -0.0278, '100': 0.0278, '99': 0.0278, '113': 0.0278, '118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '112': {c: 'p', a:0, d:.2, krn: {'101': 0.0278, '111': 0.0278, '120': -0.0278, '100': 0.0278, '99': 0.0278, '113': 0.0278, '118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '113': {c: 'q', a:0, d:1},
    '114': {c: 'r', a:0},
    '115': {c: 's', a:0},
    '116': {c: 't', krn: {'121': -0.0278, '119': -0.0278}},
    '117': {c: 'u', a:0, krn: {'119': -0.0278}},
    '118': {c: 'v', a:0, ic: 0.0139, krn: {'97': -0.0556, '101': -0.0278, '97': -0.0278, '111': -0.0278, '99': -0.0278}},
    '119': {c: 'w', a:0, ic: 0.0139, krn: {'101': -0.0278, '97': -0.0278, '111': -0.0278, '99': -0.0278}},
    '120': {c: 'x', a:0},
    '121': {c: 'y', a:0, d:.2, ic: 0.0139, krn: {'111': -0.0278, '101': -0.0278, '97': -0.0278, '46': -0.0833, '44': -0.0833}},
    '122': {c: 'z', a:0}
  },
  cmmi10:  {
    '65': {c: 'A', krn: {'127': 0.139}},
    '66': {c: 'B', ic: 0.0502, krn: {'127': 0.0833}},
    '67': {c: 'C', ic: 0.0715, krn: {'61': -0.0278, '59': -0.0556, '58': -0.0556, '127': 0.0833}},
    '68': {c: 'D', ic: 0.0278, krn: {'127': 0.0556}},
    '69': {c: 'E', ic: 0.0576, krn: {'127': 0.0833}},
    '70': {c: 'F', ic: 0.139, krn: {'61': -0.0556, '59': -0.111, '58': -0.111, '127': 0.0833}},
    '71': {c: 'G', krn: {'127': 0.0833}},
    '72': {c: 'H', ic: 0.0812, krn: {'61': -0.0556, '59': -0.0556, '58': -0.0556, '127': 0.0556}},
    '73': {c: 'I', ic: 0.0785, krn: {'127': 0.111}},
    '74': {c: 'J', ic: 0.0962, krn: {'61': -0.0556, '59': -0.111, '58': -0.111, '127': 0.167}},
    '75': {c: 'K', ic: 0.0715, krn: {'61': -0.0556, '59': -0.0556, '58': -0.0556, '127': 0.0556}},
    '76': {c: 'L', krn: {'127': 0.0278}},
    '77': {c: 'M', ic: 0.109, krn: {'61': -0.0556, '59': -0.0556, '58': -0.0556, '127': 0.0833}},
    '78': {c: 'N', ic: 0.109, krn: {'61': -0.0833, '61': -0.0278, '59': -0.0556, '58': -0.0556, '127': 0.0833}},
    '79': {c: 'O', ic: 0.0278, krn: {'127': 0.0833}},
    '80': {c: 'P', ic: 0.139, krn: {'61': -0.0556, '59': -0.111, '58': -0.111, '127': 0.0833}},
    '81': {c: 'Q', d:.2, krn: {'127': 0.0833}},
    '82': {c: 'R', ic: 0.00773, krn: {'127': 0.0833}},
    '83': {c: 'S', ic: 0.0576, krn: {'61': -0.0556, '59': -0.0556, '58': -0.0556, '127': 0.0833}},
    '84': {c: 'T', ic: 0.139, krn: {'61': -0.0278, '59': -0.0556, '58': -0.0556, '127': 0.0833}},
    '85': {c: 'U', ic: 0.109, krn: {'59': -0.111, '58': -0.111, '61': -0.0556, '127': 0.0278}},
    '86': {c: 'V', ic: 0.222, krn: {'59': -0.167, '58': -0.167, '61': -0.111}},
    '87': {c: 'W', ic: 0.139, krn: {'59': -0.167, '58': -0.167, '61': -0.111}},
    '88': {c: 'X', ic: 0.0785, krn: {'61': -0.0833, '61': -0.0278, '59': -0.0556, '58': -0.0556, '127': 0.0833}},
    '89': {c: 'Y', ic: 0.222, krn: {'59': -0.167, '58': -0.167, '61': -0.111}},
    '90': {c: 'Z', ic: 0.0715, krn: {'61': -0.0556, '59': -0.0556, '58': -0.0556, '127': 0.0833}},
    '97': {c: 'a', a:0},
    '98': {c: 'b'},
    '99': {c: 'c', a:0, krn: {'127': 0.0556}},
    '100': {c: 'd', krn: {'89': 0.0556, '90': -0.0556, '106': -0.111, '102': -0.167, '127': 0.167}},
    '101': {c: 'e', a:0, krn: {'127': 0.0556}},
    '102': {c: 'f', d:.2, ic: 0.108, krn: {'59': -0.0556, '58': -0.0556, '127': 0.167}},
    '103': {c: 'g', a:0, d:.2, ic: 0.0359, krn: {'127': 0.0278}},
    '104': {c: 'h', krn: {'127': -0.0278}},
    '105': {c: 'i'},
    '106': {c: 'j', d:.2, ic: 0.0572, krn: {'59': -0.0556, '58': -0.0556}},
    '107': {c: 'k', ic: 0.0315},
    '108': {c: 'l', ic: 0.0197, krn: {'127': 0.0833}},
    '109': {c: 'm', a:0},
    '110': {c: 'n', a:0},
    '111': {c: 'o', a:0, krn: {'127': 0.0556}},
    '112': {c: 'p', a:0, d:.2, krn: {'127': 0.0833}},
    '113': {c: 'q', a:0, d:.2, ic: 0.0359, krn: {'127': 0.0833}},
    '114': {c: 'r', a:0, ic: 0.0278, krn: {'59': -0.0556, '58': -0.0556, '127': 0.0556}},
    '115': {c: 's', a:0, krn: {'127': 0.0556}},
    '116': {c: 't', krn: {'127': 0.0833}},
    '117': {c: 'u', a:0, krn: {'127': 0.0278}},
    '118': {c: 'v', a:0, ic: 0.0359, krn: {'127': 0.0278}},
    '119': {c: 'w', a:0, ic: 0.0269, krn: {'127': 0.0833}},
    '120': {c: 'x', a:0, krn: {'127': 0.0278}},
    '121': {c: 'y', a:0, d:.2, ic: 0.0359, krn: {'127': 0.0556}},
    '122': {c: 'z', a:0, ic: 0.044, krn: {'127': 0.0556}}
  },
  cmsy10: {
    '0': {c:'&#8211;', a:.1}
  },
  cmti10: {
    '33': {c: '!', lig: {'96': 60}},
    '35': {c: '#', ic: 0.0662},
    '37': {c: '%', ic: 0.136},
    '38': {c: '&amp;', ic: 0.0969},
    '40': {c: '(', d:.2, ic: 0.162},
    '41': {c: ')', d:.2, ic: 0.0369},
    '42': {c: '*', ic: 0.149},
    '43': {c: '+', a:.1, ic: 0.0369},
    '44': {c: ',', a:-.3, d:.2, w: 0.278},
    '45': {c: '-', a:0, ic: 0.0283, lig: {'45': 123}},
    '46': {c: '.', a:-.25},
    '47': {c: '/', ic: 0.162},
    '48': {c: '0', ic: 0.136},
    '49': {c: '1', ic: 0.136},
    '50': {c: '2', ic: 0.136},
    '51': {c: '3', ic: 0.136},
    '52': {c: '4', ic: 0.136},
    '53': {c: '5', ic: 0.136},
    '54': {c: '6', ic: 0.136},
    '55': {c: '7', ic: 0.136},
    '56': {c: '8', ic: 0.136},
    '57': {c: '9', ic: 0.136},
    '58': {c: ':', ic: 0.0582},
    '59': {c: ';', ic: 0.0582},
    '61': {c: '=', a:0, d:-.1, ic: 0.0662},
    '63': {c: '?', ic: 0.122, lig: {'96': 62}},
    '64': {c: '@', ic: 0.096},
    '65': {c: 'A', krn: {'110': -0.0256, '108': -0.0256, '114': -0.0256, '117': -0.0256, '109': -0.0256, '116': -0.0256, '105': -0.0256, '67': -0.0256, '79': -0.0256, '71': -0.0256, '104': -0.0256, '98': -0.0256, '85': -0.0256, '107': -0.0256, '118': -0.0256, '119': -0.0256, '81': -0.0256, '84': -0.0767, '89': -0.0767, '86': -0.102, '87': -0.102, '101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '66': {c: 'B', ic: 0.103},
    '67': {c: 'C', ic: 0.145},
    '68': {c: 'D', ic: 0.094, krn: {'88': -0.0256, '87': -0.0256, '65': -0.0256, '86': -0.0256, '89': -0.0256}},
    '69': {c: 'E', ic: 0.12},
    '70': {c: 'F', ic: 0.133, krn: {'111': -0.0767, '101': -0.0767, '117': -0.0767, '114': -0.0767, '97': -0.0767, '65': -0.102, '79': -0.0256, '67': -0.0256, '71': -0.0256, '81': -0.0256}},
    '71': {c: 'G', ic: 0.0872},
    '72': {c: 'H', ic: 0.164},
    '73': {c: 'I', ic: 0.158},
    '74': {c: 'J', ic: 0.14},
    '75': {c: 'K', ic: 0.145, krn: {'79': -0.0256, '67': -0.0256, '71': -0.0256, '81': -0.0256}},
    '76': {c: 'L', krn: {'84': -0.0767, '89': -0.0767, '86': -0.102, '87': -0.102, '101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '77': {c: 'M', ic: 0.164},
    '78': {c: 'N', ic: 0.164},
    '79': {c: 'O', ic: 0.094, krn: {'88': -0.0256, '87': -0.0256, '65': -0.0256, '86': -0.0256, '89': -0.0256}},
    '80': {c: 'P', ic: 0.103, krn: {'65': -0.0767}},
    '81': {c: 'Q', d:.2, ic: 0.094},
    '82': {c: 'R', ic: 0.0387, krn: {'110': -0.0256, '108': -0.0256, '114': -0.0256, '117': -0.0256, '109': -0.0256, '116': -0.0256, '105': -0.0256, '67': -0.0256, '79': -0.0256, '71': -0.0256, '104': -0.0256, '98': -0.0256, '85': -0.0256, '107': -0.0256, '118': -0.0256, '119': -0.0256, '81': -0.0256, '84': -0.0767, '89': -0.0767, '86': -0.102, '87': -0.102, '101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '83': {c: 'S', ic: 0.12},
    '84': {c: 'T', ic: 0.133, krn: {'121': -0.0767, '101': -0.0767, '111': -0.0767, '114': -0.0767, '97': -0.0767, '117': -0.0767, '65': -0.0767}},
    '85': {c: 'U', ic: 0.164},
    '86': {c: 'V', ic: 0.184, krn: {'111': -0.0767, '101': -0.0767, '117': -0.0767, '114': -0.0767, '97': -0.0767, '65': -0.102, '79': -0.0256, '67': -0.0256, '71': -0.0256, '81': -0.0256}},
    '87': {c: 'W', ic: 0.184, krn: {'65': -0.0767}},
    '88': {c: 'X', ic: 0.158, krn: {'79': -0.0256, '67': -0.0256, '71': -0.0256, '81': -0.0256}},
    '89': {c: 'Y', ic: 0.194, krn: {'101': -0.0767, '111': -0.0767, '114': -0.0767, '97': -0.0767, '117': -0.0767, '65': -0.0767}},
    '90': {c: 'Z', ic: 0.145},
    '91': {c: '[', d:.1, ic: 0.188},
    '93': {c: ']', d:.1, ic: 0.105},
    '97': {c: 'a', a:0, ic: 0.0767},
    '98': {c: 'b', ic: 0.0631, krn: {'101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '99': {c: 'c', a:0, ic: 0.0565, krn: {'101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '100': {c: 'd', ic: 0.103, krn: {'108': 0.0511}},
    '101': {c: 'e', a:0, ic: 0.0751, krn: {'101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '102': {c: 'f', ic: 0.212, krn: {'39': 0.104, '63': 0.104, '33': 0.104, '41': 0.104, '93': 0.104}, lig: {'105': 12, '102': 11, '108': 13}},
    '103': {c: 'g', a:0, d:.2, ic: 0.0885},
    '104': {c: 'h', ic: 0.0767},
    '105': {c: 'i', ic: 0.102},
    '106': {c: 'j', d:.2, ic: 0.145},
    '107': {c: 'k', ic: 0.108},
    '108': {c: 'l', ic: 0.103, krn: {'108': 0.0511}},
    '109': {c: 'm', a:0, ic: 0.0767},
    '110': {c: 'n', a:0, ic: 0.0767, krn: {'39': -0.102}},
    '111': {c: 'o', a:0, ic: 0.0631, krn: {'101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '112': {c: 'p', a:0, d:.2, ic: 0.0631, krn: {'101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '113': {c: 'q', a:0, d:.2, ic: 0.0885},
    '114': {c: 'r', a:0, ic: 0.108, krn: {'101': -0.0511, '97': -0.0511, '111': -0.0511, '100': -0.0511, '99': -0.0511, '103': -0.0511, '113': -0.0511}},
    '115': {c: 's', a:0, ic: 0.0821},
    '116': {c: 't', ic: 0.0949},
    '117': {c: 'u', a:0, ic: 0.0767},
    '118': {c: 'v', a:0, ic: 0.108},
    '119': {c: 'w', a:0, ic: 0.108, krn: {'108': 0.0511}},
    '120': {c: 'x', a:0, ic: 0.12},
    '121': {c: 'y', a:0, d:.2, ic: 0.0885},
    '122': {c: 'z', a:0, ic: 0.123}
  },
  cmbx10: {
    '33': {c: '!', lig: {'96': 60}},
    '35': {c: '#'},
    '36': {c: '$'},
    '37': {c: '%'},
    '38': {c: '&amp;'},
    '40': {c: '(', d:.2},
    '41': {c: ')', d:.2},
    '42': {c: '*'},
    '43': {c: '+', a:.1},
    '44': {c: ',', a:-.3, d:.2, w: 0.278},
    '45': {c: '-', a:0, lig: {'45': 123}},
    '46': {c: '.', a:-.25},
    '47': {c: '/'},
    '48': {c: '0'},
    '49': {c: '1'},
    '50': {c: '2'},
    '51': {c: '3'},
    '52': {c: '4'},
    '53': {c: '5'},
    '54': {c: '6'},
    '55': {c: '7'},
    '56': {c: '8'},
    '57': {c: '9'},
    '58': {c: ':'},
    '59': {c: ';'},
    '61': {c: '=', a:0, d:-.1},
    '63': {c: '?', lig: {'96': 62}},
    '64': {c: '@'},
    '65': {c: 'A', krn: {'116': -0.0278, '67': -0.0278, '79': -0.0278, '71': -0.0278, '85': -0.0278, '81': -0.0278, '84': -0.0833, '89': -0.0833, '86': -0.111, '87': -0.111}},
    '66': {c: 'B'},
    '67': {c: 'C'},
    '68': {c: 'D', krn: {'88': -0.0278, '87': -0.0278, '65': -0.0278, '86': -0.0278, '89': -0.0278}},
    '69': {c: 'E'},
    '70': {c: 'F', krn: {'111': -0.0833, '101': -0.0833, '117': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.111, '79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '71': {c: 'G'},
    '72': {c: 'H'},
    '73': {c: 'I', krn: {'73': 0.0278}},
    '74': {c: 'J'},
    '75': {c: 'K', krn: {'79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '76': {c: 'L', krn: {'84': -0.0833, '89': -0.0833, '86': -0.111, '87': -0.111}},
    '77': {c: 'M'},
    '78': {c: 'N'},
    '79': {c: 'O', krn: {'88': -0.0278, '87': -0.0278, '65': -0.0278, '86': -0.0278, '89': -0.0278}},
    '80': {c: 'P', krn: {'65': -0.0833, '111': -0.0278, '101': -0.0278, '97': -0.0278, '46': -0.0833, '44': -0.0833}},
    '81': {c: 'Q', d: 1},
    '82': {c: 'R', krn: {'116': -0.0278, '67': -0.0278, '79': -0.0278, '71': -0.0278, '85': -0.0278, '81': -0.0278, '84': -0.0833, '89': -0.0833, '86': -0.111, '87': -0.111}},
    '83': {c: 'S'},
    '84': {c: 'T', krn: {'121': -0.0278, '101': -0.0833, '111': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.0833, '117': -0.0833}},
    '85': {c: 'U'},
    '86': {c: 'V', ic: 0.0139, krn: {'111': -0.0833, '101': -0.0833, '117': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.111, '79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '87': {c: 'W', ic: 0.0139, krn: {'111': -0.0833, '101': -0.0833, '117': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.111, '79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '88': {c: 'X', krn: {'79': -0.0278, '67': -0.0278, '71': -0.0278, '81': -0.0278}},
    '89': {c: 'Y', ic: 0.025, krn: {'101': -0.0833, '111': -0.0833, '114': -0.0833, '97': -0.0833, '65': -0.0833, '117': -0.0833}},
    '90': {c: 'Z'},
    '91': {c: '[', d:.1},
    '93': {c: ']', d:.1},
    '97': {c: 'a', a:0, krn: {'118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '98': {c: 'b', krn: {'101': 0.0278, '111': 0.0278, '120': -0.0278, '100': 0.0278, '99': 0.0278, '113': 0.0278, '118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '99': {c: 'c', a:0, krn: {'104': -0.0278, '107': -0.0278}},
    '100': {c: 'd'},
    '101': {c: 'e', a:0},
    '102': {c: 'f', ic: 0.0778, krn: {'39': 0.0778, '63': 0.0778, '33': 0.0778, '41': 0.0778, '93': 0.0778}, lig: {'105': 12, '102': 11, '108': 13}},
    '103': {c: 'g', a:0, d:.2, ic: 0.0139, krn: {'106': 0.0278}},
    '104': {c: 'h', krn: {'116': -0.0278, '117': -0.0278, '98': -0.0278, '121': -0.0278, '118': -0.0278, '119': -0.0278}},
    '105': {c: 'i'},
    '106': {c: 'j', d:1},
    '107': {c: 'k', krn: {'97': -0.0556, '101': -0.0278, '97': -0.0278, '111': -0.0278, '99': -0.0278}},
    '108': {c: 'l'},
    '109': {c: 'm', a:0, krn: {'116': -0.0278, '117': -0.0278, '98': -0.0278, '121': -0.0278, '118': -0.0278, '119': -0.0278}},
    '110': {c: 'n', a:0, krn: {'116': -0.0278, '117': -0.0278, '98': -0.0278, '121': -0.0278, '118': -0.0278, '119': -0.0278}},
    '111': {c: 'o', a:0, krn: {'101': 0.0278, '111': 0.0278, '120': -0.0278, '100': 0.0278, '99': 0.0278, '113': 0.0278, '118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '112': {c: 'p', a:0, d:.2, krn: {'101': 0.0278, '111': 0.0278, '120': -0.0278, '100': 0.0278, '99': 0.0278, '113': 0.0278, '118': -0.0278, '106': 0.0556, '121': -0.0278, '119': -0.0278}},
    '113': {c: 'q', a:0, d:1},
    '114': {c: 'r', a:0},
    '115': {c: 's', a:0},
    '116': {c: 't', krn: {'121': -0.0278, '119': -0.0278}},
    '117': {c: 'u', a:0, krn: {'119': -0.0278}},
    '118': {c: 'v', a:0, ic: 0.0139, krn: {'97': -0.0556, '101': -0.0278, '97': -0.0278, '111': -0.0278, '99': -0.0278}},
    '119': {c: 'w', a:0, ic: 0.0139, krn: {'101': -0.0278, '97': -0.0278, '111': -0.0278, '99': -0.0278}},
    '120': {c: 'x', a:0},
    '121': {c: 'y', a:0, d:.2, ic: 0.0139, krn: {'111': -0.0278, '101': -0.0278, '97': -0.0278, '46': -0.0833, '44': -0.0833}},
    '122': {c: 'z', a:0}
  }
});


if (jsMath.browser == 'MSIE' && navigator.platform == 'MacPPC') {
  jsMath.Setup.Styles({
    '.typeset .math':       'font-style: normal',
    '.typeset .typeset':    'font-style: normal',
    '.typeset .icmr10':     'font-family: Times',
    '.typeset .icmmi10':    'font-family: Times; font-style: italic',
    '.typeset .icmbx10':    'font-family: Times; font-weight: bold',
    '.typeset .icmti10':    'font-family: Times; font-style: italic'
  });
} else {
  jsMath.Setup.Styles({
    '.typeset .math':       'font-style: normal',
    '.typeset .typeset':    'font-style: normal',
    '.typeset .icmr10':     'font-family: serif',
    '.typeset .icmmi10':    'font-family: serif; font-style: italic',
    '.typeset .icmbx10':    'font-family: serif; font-weight: bold',
    '.typeset .icmti10':    'font-family: serif; font-style: italic'
  });
}


jsMath.Add(jsMath.Img,{
  symbols: [
      0,  1,  2,  3,  4,  5,  6,  7,    8,  9, 10, 11, 12, 13, 14, 15,
     16, 17, 18, 19, 20, 21, 22, 23,   24, 25, 26, 27, 28, 29, 30, 31,
     32,     34,                 39,
                                                       60,     62,

                                                       92,     94, 95,
     96,
                                                  123,124,125,126,127
  ]
});

/*
 *  for now, use images for everything
 */
jsMath.Img.SetFont({
   cmr10:  jsMath.Img.symbols,
   cmmi10: [
      0,  1,  2,  3,  4,  5,  6,  7,    8,  9, 10, 11, 12, 13, 14, 15,
     16, 17, 18, 19, 20, 21, 22, 23,   24, 25, 26, 27, 28, 29, 30, 31,
     32, 33, 34, 35, 36, 37, 38, 39,   40, 41, 42, 43, 44, 45, 46, 47,
     48, 49, 50, 51, 52, 53, 54, 55,   56, 57, 58, 59, 60, 61, 62, 63,
     64,
                                                   91, 92, 93, 94, 95,
     96,
                                                  123,124,125,126,127
   ],
   cmsy10: [
          1,  2,  3,  4,  5,  6,  7,    8,  9, 10, 11, 12, 13, 14, 15,
     16, 17, 18, 19, 20, 21, 22, 23,   24, 25, 26, 27, 28, 29, 30, 31,
     32, 33, 34, 35, 36, 37, 38, 39,   40, 41, 42, 43, 44, 45, 46, 47,
     48, 49, 50, 51, 52, 53, 54, 55,   56, 57, 58, 59, 60, 61, 62, 63,
     64, 65, 66, 67, 68, 69, 70, 71,   72, 73, 74, 75, 76, 77, 78, 79,
     80, 81, 82, 83, 84, 85, 86, 87,   88, 89, 90, 91, 92, 93, 94, 95,
     96, 97, 98, 99,100,101,102,103,  104,105,106,107,108,109,110,111,
    112,113,114,115,116,117,118,119,  120,121,122,123,124,125,126,127
   ],
   cmex10: ['all'],
   cmti10: jsMath.Img.symbols.concat(36),
   cmbx10: jsMath.Img.symbols
});

jsMath.Img.LoadFont('cm-fonts');

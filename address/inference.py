import chardet
import datetime
import json
import logging
import lxml.html
import math
import operator
import urllib.request
import urllib.parse

from django.utils import timezone

import MeCab
from .models import WebCache

default_logger = logging.getLogger(__name__)

def detect_encoding(content):
    detect = chardet.detect(content)
    encoding = detect['encoding']
    return encoding

BLOCK_TAGS = [
  'body', 'header', 'footer', 'article', 'section', 'div', 'p',
  'form', 'fieldset', 'select',
  'ul', 'ol', 'li', 'dl', 'dt', 'dd',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
]
INLINE_TAGS = [
  # 'a', for support to www.yukoyuko.net
  'span', 'strong', 'em', 's', 'input', 'button', 'textarea', 'legend'
]
ACCEPT_TAGS = BLOCK_TAGS + INLINE_TAGS

def text(t):
    if t is None: return ''
    else: return t.strip()

# Custom itertext
def itertext(elem):
    queue = []
    for e in elem:
        # skip trees out of body
        if e.tag == 'body': queue.append(e)
    while len(queue) > 0:
        e0 = queue.pop(0) # breadth first search
        t = text(e0.text)
        children = filter(lambda e: e.tag in ACCEPT_TAGS, list(e0))
        for e in children:
            if e.tag not in INLINE_TAGS:
                queue.append(e)
                break
            t += text(e.text_content()) + text(e.tail)
        tail = list(children)
        if len(tail) == 0:
           # concatinate all texts when all of children are in INLINE_TAGS
           t += text(e0.tail)
           if len(t) > 0: yield t
        else:
           if len(t) > 0: yield t
           t = text(e0.tail)
           if len(t) > 0: yield t
        queue += tail

# 住所一覧読込
def load_address_list(csv):
    with open(csv, "r") as file:
        line = file.readline()
        while line:
            line = line.strip()
            cols = line.split(",")
            yield cols
            line = file.readline()

def load_all_address(csv):
    address_list = {}
    for cols in load_address_list(csv):
        if len(cols) > 1:
            address_list[cols[0]] = cols[1:]
    return address_list

def load_reversed_address(csv):
    address_list = {}
    for cols in load_address_list(csv):
        if len(cols) > 1:
            for muni in cols[1:]:
                address_list[muni] = cols[0]
    return address_list

def is_xml(content):
    return -1 < content.find("<?xml") < 50

def pre_normalize(t):
    t = t.replace("０", "0")
    t = t.replace("１", "1")
    t = t.replace("２", "2")
    t = t.replace("３", "3")
    t = t.replace("４", "4")
    t = t.replace("５", "5")
    t = t.replace("６", "6")
    t = t.replace("７", "7")
    t = t.replace("８", "8")
    t = t.replace("９", "9")
    t = t.replace("ー", "-")
    t = t.replace("－", "-")
    return t

class WordFeature:
    def __init__(self, surface, partOfSpeech, detail1, detail2, detail3, yomi):
        self.surface = surface
        self.partOfSpeech = partOfSpeech
        self.detail1 = detail1
        self.detail2 = detail2
        self.detail3 = detail3
        self.yomi = yomi

class AreaName():
    def __init__(self, words):
        self.words = words
    
    def get_tail(self):
        return self.words[-1]
    
    def __str__(self):
        return '-'.join(w.surface for w in self.words)
    
    def str_surface(self):
        return ''.join(w.surface for w in self.words)
    
    def str_yomi(self):
        def yomi(w):
            if w.yomi is not None:
                return w.yomi
            return w.surface
        return ''.join(yomi(w) for w in self.words)

class Address:
    def __init__(self):
        self.prefecture = None
        self.prefecture_yomi = None
        self.municipality = []
        self.municipality_yomi = []
        self.address = []
        self.address_yomi = []
    
    def __str__(self):
        return self.get_address()
    
    def set_prefecture(self, area):
        self.prefecture = area.str_surface()
        self.prefecture_yomi = area.str_yomi()
    
    def append_municipality(self, area):
        self.municipality.append(area.str_surface())
        self.municipality_yomi.append(area.str_yomi())

    def clear_detail(self):
        self.address = []
        self.address_yomi = []
    
    def append_detail(self, area):
        def yomi(w):
            if w.yomi is not None:
                return w.yomi
            else:
                return w.surface
        for w in area.words:
            if w.partOfSpeech == '名詞' and \
               w.detail1 == '接尾':
                if w.surface in ['丁目', '番', '番地']:
                    self.address.append('-')
                    self.address_yomi.append('-')
                elif w.surface in ['号']:
                    pass
                else:
                    self.address.append(w.surface)
                    self.address_yomi.append(yomi(w))
            else:
                self.address.append(w.surface)
                self.address_yomi.append(yomi(w))
    
    def complete(self, address_list):
        if self.prefecture is None and \
           len(self.municipality) > 0:
            name = ''.join(self.municipality)
            if name in address_list:
                self.prefecture = address_list[name]
                self.prefecture_yomi = address_list[name]
    
    def ok(self):
        return self.prefecture is not None and \
            len(self.municipality) > 0 and \
            len(self.address) > 0
    
    def get_address(self):
        ws = []
        if self.prefecture is not None:
            ws.append(self.prefecture)
        ws += self.municipality
        ws += self.address
        return ''.join(ws)
    
    def get_yomi(self):
        ws = []
        if self.prefecture is not None:
            ws.append(self.prefecture_yomi)
        ws += self.municipality_yomi
        ws += self.address_yomi
        return ''.join(ws)

def is_noun(w):
    return w.partOfSpeech == '名詞'

def morphological_analyze(tagger, sentence):
    node = tagger.parse(sentence)
    for node in node.split('\n'):
        cols = node.split('\t')
        if len(cols) < 2: continue
        surface = cols[0]
        feature = cols[1]
        out = feature.split(',')
        if out[0] != 'BOS/EOS':
            if len(out) > 7:
                yomi = out[7]
            else:
                yomi = None
            yield WordFeature(surface, out[0], out[1], out[2], out[3], yomi)

# utility for syntax analyzer
def is_head(w):
    return \
        (is_noun(w) and w.detail1 in ['固有名詞', '数', '一般']) or \
        w.partOfSpeech == '接頭詞'

# utility for syntax analyzer
def is_tail(w):
    # 'サ変接続' contains symbols such a '-'.
    return is_noun(w) and w.detail1 in ['接尾', 'サ変接続']

def syntax_analyze(words):
    """
    syntax analyzer for address.
    This converts morphological analyzed words to list of AreaName and
    returns it.
    """
    status = 'b'
    names = []
    result = []
    
    words = list(words)
    i = 0
    while i < len(words):
        w = words[i]
        if status == 'b':
            # search head
            if is_head(w):
                status = 'h' # start collecting '接尾詞's
                names = [w]
            else:
                result.append(None)
        elif status == 'h':
            if is_tail(w):
                # collect sequential '接尾詞's
                names.append(w)
            else:
                # '接尾詞' sequence ended
                result.append(AreaName(names))
                status = 'b'
                continue
        i += 1
    if status == 'h':
        result.append(AreaName(names))        
    return result

def is_prefecture(area):
    # 北海道のみ固有名詞として解析されるので、特別扱い
    if area is None: return False
    w = area.get_tail()
    return \
        w.partOfSpeech == '名詞' and \
        ((w.surface in ['北海道']) or
         (w.detail1 == '接尾' and \
          w.surface in '都道府県'))

def is_municipality(area):
    if area is None: return False
    w = area.get_tail()
    return w.partOfSpeech == '名詞' and \
        w.detail1 == '接尾' and \
        w.surface in '市区郡町村'

def build_address(areas):
    address = Address()
    level = 1
    
    for area in areas:
        if level < 2 and is_prefecture(area):
            address.set_prefecture(area)
            address.clear_detail()
            level = 2
        elif level < 3 and is_municipality(area):
            address.append_municipality(area)
            address.clear_detail()
            level = 3
        elif 1 < level:
            if area is None: break
            address.append_detail(area)
            level = 4
    return address            

def test_extract(text):
    tagger = MeCab.Tagger('')
    text  = pre_normalize(text)
    words = morphological_analyze(tagger, text)
    areas = syntax_analyze(words)
    addr  = build_address(areas)
    return addr

def calc_point(i):
    return pow(0.5, math.log(i+1, 3))

def calc_confidence(candidates):
    """
    (addr, point) list -> (addr, confidence) list
    """
    lst = sorted(candidates, key=operator.itemgetter(1))
    lst.reverse()
    s = sum(v for (k, v) in lst)
    conf = [ (k, v / s) for k, v in lst ]
    return conf

def url_excludelist_filter(urls, excludelist):
    def f(url):
        for p in excludelist:
            if url.find(p) >= 0: return False
        return True
    return list(filter(f, urls))

class Inference:
    def __init__(self, address_list_csv, excludelist,
                 bing_client_id, bing_account_key, logger=None):
        self.logger = logger or default_logger
        self.bing_client_id = bing_client_id
        self.bing_account_key = bing_account_key
        self.excludelist = excludelist
        self.address_list_csv = address_list_csv
        self.tagger = MeCab.Tagger('')
    
    def address_of(self, name):
        urls = self.search_bing(name)
        address_list = load_reversed_address(self.address_list_csv)
        addrs = self.collect_address(address_list, urls)
        return addrs

    def load_cache(self, url, expire):
        caches = WebCache.objects.filter(url__exact=url)
        if len(caches) == 0:
            return None
        cache = caches[0]
        if cache.is_expired(expire):
            cache.delete()
            return None
        return cache

    def search_bing(self, query, n=20):
        """
        Search Bing by query and return hitted urls.
        """
        BASEURL = "https://api.datamarket.azure.com/Bing/Search/Web"
        client_id = self.bing_client_id
        account_key = self.bing_account_key
        encoding = 'utf-8'
    
        def make_url(query):
            params0 = {
                "Query": "'{}'".format(query),
                "Market": "'ja-JP'"
		    }
            params1 = {
                "$format": "json",
                "$top": str(n)
            }
            query = '&'.join([urllib.parse.urlencode(params0)] +
                             [k + "=" + v for k, v in params1.items()])
            return BASEURL + '?' + query

        def setup_request(url, client_id, account_key):
            pm = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            pm.add_password(None, BASEURL, client_id, account_key)
            handler = urllib.request.HTTPBasicAuthHandler(pm)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        def request_get(url, encoding):
            response = urllib.request.urlopen(url)
            response = response.read()
            content = response.decode(encoding)
            return content

        setup_request(BASEURL, client_id, account_key)
        url = make_url(query)

        cache = self.load_cache(url, datetime.timedelta(days=1))
        self.logger.debug('bing url={} cache={}'.format(url, cache))    
        if cache is None:
            content = request_get(url, encoding)
            cache = WebCache(url=url, encoding=encoding, content=content,
                             created=timezone.now())
            cache.save()
        else:
            content = cache.content
        rsp = json.loads(content)

        urls = [ r["Url"] for r in rsp["d"]["results"] ]
        return urls

    def collect_address(self, address_list, urls):
        candidates = {}
        urls = url_excludelist_filter(urls, self.excludelist)
        urls = urls[0:min(len(urls), 10)]
        for i in range(0, len(urls)):
            url = urls[i]
            point = calc_point(i)
            docroot = self.get_page(url)
            if docroot is None: continue
            addrs = self.find_address(address_list, docroot)
            for addr in addrs:
                key = addr.get_address()
                if key in candidates:
                    addr0, point0 = candidates[key]
                    point += point0
                candidates[key] = (addr, point)
        confidences = calc_confidence(candidates.values())
        return confidences

    def get_page(self, url):
        cache = self.load_cache(url, datetime.timedelta(days=7))
        self.logger.debug('get page url={} cache={}'.format(url, cache))
        if cache is None:
            encoding = None # for logging
            try:
                headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.48 Safari/537.36 Vivaldi/1.3.537.5' }
                request = urllib.request.Request(url, None, headers)
                response = urllib.request.urlopen(request)
                content = response.read()
                encoding = detect_encoding(content)
                content = content.decode(encoding)
                cache = WebCache(url=url, encoding=encoding, content=content,
                                 created=timezone.now())
                cache.save()
            except UnicodeDecodeError as e:
                self.logger.error('decode error url={}, encoding={}'
                                  .format(url, encoding))
                return None
            except Exception as e:
                self.logger.error(e)
                return None
        else:
            # cache hitted!!
            content = cache.content
        # delete <?xml...> declaration as workaround of xml parsing error
        if is_xml(content):
            content = content[content.find("?>") + 3:]
        docroot = lxml.html.fromstring(content)
        return docroot

    def find_address(self, address_list, element):
        result = []
        addrs = []
        for t in itertext(element):
            self.logger.debug('t={}'.format(t))
            # prefiltering
            if len(t) < 4: continue
            if 300 < len(t): continue
            # run extractor
            addr = self.extract_address(address_list, t)
            if len(str(addr)) > 0:
                self.logger.debug('addr={}, ok={}'.format(addr, addr.ok()))
            if addr.ok() and addr.get_address() not in addrs:
                addrs.append(addr.get_address())
                result.append(addr)
        return result

    def extract_address(self, address_list, text):
        """
        extract address from text on natural language
        """
        text  = pre_normalize(text)
        words = morphological_analyze(self.tagger, text)
        areas = syntax_analyze(words)
        addr  = build_address(areas)
        addr.complete(address_list)
        return addr

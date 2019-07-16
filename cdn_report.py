import sys
import json
from qiniu import Auth
from qiniu import http


access_key = ''
secret_key = ''

at = Auth(access_key, secret_key)


def domain_info(domain):
    json_data, response_info = http._get('http://api.qiniu.com/domain/%s' % domain, None, at)
    if response_info.status_code != 200:
        raise Exception("get domain info error")
    return json_data

class DomainInfo:
    def __init__(self, json_data):
        self.json_data = json_data

    def domain_name(self):
        return self.json_data['name']

    def test_url_path(self):
        return self.json_data['testURLPath']

    def advanced_domain_sources(self):
        for s in self.json_data['source']['advancedSources']:
            addr = s['addr']
            weight = s['weight']
            backup = s['backup']
            yield Source(self.domain_name(), addr, weight, backup)

    def advanced_domain_sources_manager(self):
        return AdvancedDomainSources(self.advanced_domain_sources())


class AdvancedDomainSources:
    def __init__(self, sources):
        self.master = []
        self.backup = []

        for s in sources:
            if s.is_backup() :
                self.backup.append(s)
            else:
                self.master.append(s)

    def master_sources(self):
        return self.master

    def backup_sources(self):
        return self.backup


class Source:
    def __init__(self, name, addr, weight, typ):
        self.name = name
        self.addr = addr
        self.weight = weight
        self.typ = typ

    def domain_name(self):
        return self.name

    def is_backup(self):
        return self.typ == True

    def __str__(self):
        return 'addr: %s, weight: %d, typ: %s' % (self.addr, self.weight, self.typ)


def domain_list():
    params = {
        'marker': '',
        'limit': 100
    }
    json_data, response_info = http._get('http://api.qiniu.com/domain', params, at)
    if response_info.status_code != 200:
        raise Exception("get domain list error")
    for d in json_data['domains']:
        yield d['name']

def get_path(year, month):
    return '解放军报域名巡检报告-%d-%d.csv' % (year, month)

def cdn_report(year, month):
    path = get_path(year, month)
    with open(path, 'w+') as fw:
        fw.writelines(['序号,域名,主源,备源1,备源2,备源3,边缘遍历是否正常\n'])
        for ind, d in enumerate(domain_list()):
            dinfo = DomainInfo(domain_info(d))
            dm = dinfo.advanced_domain_sources_manager()
            mss = dm.master_sources()
            assert len(mss) == 1, dinfo.domain_name() + str(len(mss))
            bss = dm.backup_sources()
            assert len(bss) <= 3
            suf = ',' * (3 - len(bss))
            left_part = ','.join([str(ind+1), dinfo.domain_name(), mss[0].addr])
            right_part = ','.join([bs.addr for bs in bss]) + suf + ',正常'
            line = left_part + ',' + right_part + '\n'
            fw.writelines([line])

def domains_have_no_master():
    for ind, d in enumerate(domain_list()):
        dinfo = DomainInfo(domain_info(d))
        dm = dinfo.advanced_domain_sources_manager()
        mss = dm.master_sources()
        if len(mss) <= 0:
            print(dinfo.domain_name())



source_info = {
    'www.81rc.mil.cn':	     ["111.203.147.63",	["211.166.76.63"], ""],
    'i12.chinamil.com.cn':	 ["111.203.147.63",	["211.166.76.63"], ""],
    '81rc.81.cn':	         ["111.203.147.63",	["211.166.76.63"], ""],
    'tv.81.cn':	             ["111.203.147.6",	["61.183.245.35","111.203.149.26","211.166.76.6"], ""],
    'photo.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'cz.81.cn':	             ["111.203.148.1",	["211.166.76.1","61.183.245.36","111.203.149.28"], ""],
    'longmarch.81.cn':	     ["111.203.148.1",	["211.166.76.1","61.183.245.36","111.203.149.28"], ""],
    'changzheng.81.cn':	     ["111.203.148.1",	["211.166.76.1","61.183.245.36","111.203.149.28"], ""],
    'bbs.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'jz.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'sy.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'gz.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'lz.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'xblj.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'xb.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'nb.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'db.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'zb.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'bblj.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'bb.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'rocket.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'zf.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'hq.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'zlzy.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'army.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'zh.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'kj.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'nj.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'ep.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'bj.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'jn.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'cd.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'zz.81.cn':	             ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'navy.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'wj.81.cn':	             ["111.203.147.6",	["61.183.245.35","111.203.149.26"], ""],
    'www.81.cn':	         ["111.203.147.1",	["211.166.76.1","61.183.245.35","111.203.149.26"], ""],
    'i10.81.cn':	         ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'wpns.mod.gov.cn':	     ["111.203.148.11",	["61.183.245.35","111.203.149.27"], ""],
    'eimg.mod.gov.cn':	     ["111.203.148.23",	["211.166.76.2","61.183.245.35","111.203.149.27"], ""],
    'eng.mod.gov.cn':	     ["111.203.148.21",	["211.166.76.2","61.183.245.35","111.203.149.27"], ""],
    'img.mod.gov.cn':	     ["111.203.148.15",	["211.166.76.2","61.183.245.35","111.203.149.27"], ""],
    'news.mod.gov.cn':	     ["111.203.148.13",	["211.166.76.2","61.183.245.35","111.203.149.27"], ""],
    'www.mod.gov.cn':	     ["111.203.148.11",	["211.166.76.2","61.183.245.35","111.203.149.27"], ""],
    'i9.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'i8.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'i7.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'i4.chinamil.com.cn':	 ["111.203.147.6",	["61.183.245.35","111.203.149.26","211.166.76.6"], ""],
    'i3.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'i2.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'i1.chinamil.com.cn':	 ["111.203.147.1",	["211.166.76.1","61.183.245.35","111.203.149.26"], ""],
    'chn.chinamil.com.cn':	 ["111.203.147.1",	["211.166.76.1","61.183.245.35","111.203.149.26"], ""],
    'photo.chinamil.com.cn': ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'txjs.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'youth.chinamil.com.cn': ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'jz.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'sq.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'eng.chinamil.com.cn':	 ["111.203.147.6",	["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'english.chinamil.com.cn':	["111.203.147.6",["211.166.76.6","61.183.245.35","111.203.149.26"], ""],
    'www.chinamil.com.cn':	["111.203.147.1",["211.166.76.1","61.183.245.35","111.203.149.26"], ""],
    'defenseimg.81.cn':	["111.203.147.96", ["211.166.76.96"], ""],
    'vr.81.cn':   ["111.203.147.88",["211.166.76.88"], ""],
    'vv.chinamil.com.cn':	["111.203.147.36",["211.166.76.36",	"61.183.245.35", "111.203.149.27"], ""],
    'yspvv.81.cn':	["111.203.147.83", ["211.166.76.83"], ""],
}

def advanced_sources(domain, source_port=80):
    addrs = []
    master = {
        'addr': source_info[domain][0],
        'weight': 1,
        'backup': False,
    }
    addrs.append(master)

    for addr in source_info[domain][1]:
        backup = {
            'addr': addr,
            'weight': 1,
            'backup': True,
        }
        addrs.append(backup)
    return addrs


# 更新域名的源站
# 解放军报源站分为主源和备源， 平时只需要配置一个主源
# 但是需要有一键切换的能力， 可以根据解放军报的指令切换到备源， 或者主备源
#
# @use 可以为"both", "master_only", "slave_only"
# 当@use为"both"是表示使用七牛高级回源，同时配置主备源
# 当@use为"master_only"时， 表示只配置主源
# 当@use为"slave_only"时，表示只配置备源
# @index仅当@use="slave_only"是有效, 为多个备份源站的索引位置, -1使用所有的备源站
def update_source(domain, use="both", index=-1):
    assert domain in source_info
    assert len(source_info[domain]) == 3

    if source_info[domain][2] == "":
        test_url_path = "qiniu_do_not_test.gif"
    else:
        test_url_path = source_info[domain][2]

    source_config = {
        'sourceURLScheme': 'http',
        'testURLPath': test_url_path
    }
    if use=="both": # 高级回源
        source_type = "advanced"
        source_config['advancedSources'] = advanced_sources(domain)
    elif use == "master_only":
        source_type = "ip"
        source_config['sourceIPs'] = [source_info[domain][0]]
    else: # 解放军报回源用的都是ip, slave_only
        source_type = "ip"
        if index == -1:
            source_config['sourceIPs'] = source_info[domain][1]
        else:
            assert 0 <= index <= 2
            source_config['sourceIPs'] = [source_info[domain][1][index]]
    source_config['sourceType'] = source_type

    json_data, response_info = http._put('http://api.qiniu.com/domain/%s/source' % domain, source_config, at)
    if response_info.status_code != 200:
        print(json.dumps(source_config))
        print(response_info)
        raise Exception("update domain source error: %s" % response_info.text_body)



def check_args():
    if len(sys.argv) != 3:
        usage()

def usage():
    print('''Usage:
    python3.6 cdn_report.py <year> <month>
    ''')


if __name__ == '__main__':
    #check_args()
    #cdn_report(int(sys.argv[1]), int(sys.argv[2]))

    update_source('chn.chinamil.com.cn', use="both")

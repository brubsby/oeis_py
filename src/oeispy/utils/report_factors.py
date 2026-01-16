import urllib.request
import urllib.parse


def report(composite_to_factor_tuples):
    payload = "\n".join(["{}={}".format(composite, factor) for composite, factor in composite_to_factor_tuples])
    payload = 'report=' + urllib.parse.quote(payload, safe='') + '&format=0'
    payload = payload.encode('utf-8')
    temp2 = urllib.request.urlopen('http://factordb.com/report.php', payload)
    if temp2.status != 200:
        raise Exception(temp2)

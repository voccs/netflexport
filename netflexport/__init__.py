from oauth import oauth
from oauth.oauth import OAuthRequest, OAuthToken
from netflix import *

from os.path import exists

import simplejson as json

class Netflexport(object):
    def __init__(self, config):
        self._config = config
        self._paging = int(self._config.get('app', 'paging'))
        self._flix = Netflix(key=self._config.get('app', 'key'),
                             secret=self._config.get('app', 'secret'))
        self._token = OAuthToken(key=self._config.get('user', 'key'),
                                 secret=self._config.get('user', 'secret'))

    def _user_url(self, stub_url):
        """where stub_url is the part after /users/user_id/"""
        return '/users/%s/%s' % (self._config.get('user', 'id'), stub_url)

    def _title_url(self, id):
        return 'http://api.netflix.com/catalog/titles/movies/%s' % id

    def request(self, url, user=True, verb=None, filename=None, **args):
        args['expand'] = u'@title,@synopsis,@box_art,@cast,@directors,@awards'
        args['v'] = u'2.0'
        if user:
            url = self._user_url(url)
        if verb is not None:
            return self._flix.request(url,
                                      token=self._token,
                                      verb=verb,
                                      filename=filename,
                                      **args)
        else:
            return self._flix.request(url,
                                      token=self._token,
                                      filename=filename,
                                      **args)

    def whoami(self):
        print self.request('/users/current', user=False)
        return

    def _pager(self, result_key, method, **args):
        initial = method(**args)
        if initial['meta'].has_key('number_of_results'):
            size = initial['meta']['number_of_results']
        elif initial['meta'].has_key('queue_length'):
            size = initial['meta']['queue_length']
        if size > self._paging:
            iters = int(size / self._paging) + 1
            for i in range(1, iters):
                new_set = method(start=i*self._paging, **args)
                initial[result_key] += new_set[result_key]
        return initial

    def export_all_recommendations(self):
        return self._pager('recommendations',
                           self._export_recommendations)

    def _export_recommendations(self, start=0):
        return self.request('recommendations',
                            start_index=start,
                            max_results=self._paging)

    def export_all_queue(self, **args):
        return self._pager('queue',
                           self._export_queue,
                           **args)

    def _export_queue(self, mode="disc", start=0):
        return self.request('queues/%s' % mode,
                            sort='queue_sequence',
                            start_index=start,
                            max_results=self._paging)

    def export_ratings(self, filename=None):
        ratings = self._read_ratings(filename)
        size = len(ratings)
        all = {'ratings':[]}
        if size > self._paging:
            iters = int(size / self._paging) + 1
            for i in range(0, iters):
                end = ((i+1) * self._paging) - 1
                if end >= size:
                    end = size - 1
                refs = ratings[(i * self._paging):end]
                refs = [ self._title_url(id) for id in refs ]
                new_set = self.request('ratings/title',
                                       start_index=i * self._paging,
                                       max_results=self._paging,
                                       title_refs=','.join(refs))
                all['ratings'] += new_set['ratings']
        return all

    def _read_ratings(self, filename=None):
        ratings = []
        if filename is None:
            filename = self._config.get('user', 'ratings')

        if filename is not None and exists(filename):
            fn = open(filename)
            for line in fn:
                args = line.split('|')
                ratings.append(args[0])
            fn.close()

        return ratings

    def export(self, filename=None):
        iq    = self.export_all_queue(mode="instant")
        dq    = self.export_all_queue(mode="disc")
        rates = self.export_ratings(filename)
        recs  = self.export_all_recommendations()
        all   = {'instant_queue': iq['queue'],
                 'disc_queue': dq['queue'],
                 'ratings': rates['ratings'],
                 'recommendations': recs['recommendations'] }
        s = json.dumps(all, sort_keys=True, indent=4*' ')
        print '\n'.join([l.rstrip() for l in s.splitlines()])

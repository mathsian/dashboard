from collections import deque
from urllib.parse import urlparse, parse_qs


class History(deque):

    def get_match(self, pathname, search):
        return False
        match = False
        max_path_match = 0
        max_search_match = 0

        path_list = pathname.split('/')
        search_dict = parse_qs(search.removeprefix('?'))
        for url in self.reverse():
            parse_object = urlparse(url)
            url_list = parse_object.split('/')
            path_match = len([1 for p,h in zip(path_list, url_list) if p == h])
            if path_match > max_path_match:
                match = url
                max_path_match = path_match
            elif path_match == max_path_match:
                url_dict = parse_qs(parse_object.query)
                search_match = len([1 for qk, qv in search_dict.items() if qk in url_dict.keys() and url_dict.get(qk) == qv])
                if search_match > max_search_match:
                    match = url
                    max_search_match = search_match
        if match:
            self.remove(match)
            self.append(match)
        return match

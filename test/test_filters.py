from filters import ReFilter, DateFilter
from datetime import datetime

def test_re_filter():
    uri_filter = [r'\.epfl\.ch/(js|styles|images)/', r'^search-api']
    filters = ReFilter(uri_filter)

    for uri in ['search-2012.epfl.ch/api/ldap/csv', 'search-api.epfl.ch/api/cse', 'search-2012.epfl.ch/styles/']:
        print(f"{uri}:")
        print(f"> AND = {filters.matches(uri, ReFilter.AND)}, OR = {filters.matches(uri, ReFilter.OR)}")


def test_date_filter():
    date_filter = DateFilter('2021-10-13', '2021-10-20')
    for day in [12, 14, 16, 18, 20, 22]:
        request_time = datetime(2021, 10, day, 0, 30, 10)
        print(f" between({request_time}): {DateFilter.between(date_filter, request_time)}")


if __name__ == '__main__':
    # test_re_filter()
    test_date_filter()

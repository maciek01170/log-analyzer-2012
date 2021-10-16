from filters import ReFilter

if __name__ == '__main__':
    uri_filter = [r'\.epfl\.ch/(js|styles|images)/', r'^search-api']
    filters = ReFilter(uri_filter)

    for uri in ['search-2012.epfl.ch/api/ldap/csv', 'search-api.epfl.ch/api/cse', 'search-2012.epfl.ch/styles/']:
        print(f"{uri}:")
        print(f"> AND = {filters.matches(uri, ReFilter.AND)}, OR = {filters.matches(uri, ReFilter.OR)}")

from django.shortcuts import render
import requests

def getCategoryList(request):
    '''
    Retrieves category listing via eventbrite api, builds a mapping of category id to category name into
    the user's session.
    :return: a list of categories in JSON format.
    '''
    # request each of the categories via the eventbrite api
    raw_response = requests.get("https://www.eventbriteapi.com/v3/categories", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

    # decode the response in JSON
    response = raw_response.json()

    # build the dictionary for mapping id to category name in user session
    request.session['categories'] = {cat['id']: cat['name'] for cat in response['categories']}

    # return the categories list
    return response['categories']


def getEventList(request, **args):
    '''
    Retrieves event listing via eventbrite api and returns event list. If optional argument 'filter' supplied, only
    events that match a category id in 'filter' argument will be returned.
    :param **args: optional argument 'filter' - a list of category ids.
    :return: a list of events in JSON format
    '''

    # if there was no page specified, default to 1
    if not 'page' in args:
        args['page'] = 1

    # check for the filter argument
    if 'filter' in args:
        # if the user's searched for the page already, return the cached page
        if str(args['page']) in request.session['rel_events']:
            return request.session['rel_events'][str(args['page'])]

        # get the relevant ids
        rel_ids = args['filter']

        # make the query for events of a certain category and page
        raw_response = requests.get("https://www.eventbriteapi.com/v3/events/search/", params={'token': 'BKKRDKVUVRC5WG4HAVLT',
                                                                                               'categories': rel_ids,
                                                                                               'page': args['page']})
        # decode the response in JSON
        response = raw_response.json()

        # verify the user didn't go out of page range
        if response['pagination']['page_number'] > response['pagination']['page_count']:
            # the user did go out of range, so we need to query for the last page
            raw_response = requests.get("https://www.eventbriteapi.com/v3/events/search/",
                                        params={'token': 'BKKRDKVUVRC5WG4HAVLT',
                                                'categories': rel_ids,
                                                'page': response['pagination']['page_count']})
            # decode the new response in JSON
            response = raw_response.json()

        # if necessary, store relevant response information for events and pagination in the user's session
        if not str(args['page']) in request.session['rel_events']:
            request.session['rel_events'][str(args['page'])] = response['events'], response['pagination']
            request.session['rel_events_list'].extend(str(args['page']))
        else:
            # the visited page is already in cache, so move it to the back of our "queue"
            request.session['rel_events_list'].insert(len(request.session['rel_events_list']),
                                                      request.session['rel_events_list'].pop(request.session['rel_events_list'].index(str(args['page']))))

        # remove cached pages if necessary
        if len(request.session['rel_events']) > 3:
            # get the first page number from the list and use it as a key to our event dictionary cache
            del request.session['rel_events'][request.session['rel_events_list'].pop(0)]

    else:
        # if the user's searched for the page already, return the cached page
        if str(args['page']) in request.session['all_events']:
            return request.session['all_events'][str(args['page'])]

        # request the event listing via the eventbrite api
        raw_response = requests.get("https://www.eventbriteapi.com/v3/events/search/", params={'token': 'BKKRDKVUVRC5WG4HAVLT',
                                                                                               'page': args['page']})
        # decode the response in JSON
        response = raw_response.json()

        # verify the user didn't go out of page range
        if response['pagination']['page_number'] > response['pagination']['page_count']:
            # the user did go out of range, so we need to query for the last page
            raw_response = requests.get("https://www.eventbriteapi.com/v3/events/search/",
                                        params={'token': 'BKKRDKVUVRC5WG4HAVLT',
                                                'page': response['pagination']['page_count']})
            # decode the new response in JSON
            response = raw_response.json()

        # if necessary, store relevant response information for events and pagination in the user's session
        if not str(args['page']) in request.session['all_events']:
            request.session['all_events'][str(args['page'])] = (response['events'], response['pagination'])
            request.session['all_events_list'].extend(str(args['page']))
        else:
            # the visited page is already in cache, so move it to the back of our "queue"
            request.session['all_events_list'].insert(len(request.session['all_events_list']),
                                                      request.session['all_events_list'].pop(request.session['all_events_list'].index(str(args['page']))))

        # remove cached pages if necessary
        if len(request.session['all_events']) > 3:
            # get the first page number from the list and use it as a key to our event dictionary cache
            del request.session['all_events'][request.session['all_events_list'].pop(0)]

    # let Django know to save the session
    request.session.modified = True

    # return:
    # 1. a list of all events
    # 2. a dictionary containing pagination information
    return response['events'], response['pagination']


def index(request):
    '''
    Renders the homepage of the application with all available categories.

    :param      request: an http/https request.
    :return:    the rendered homepage with a listing of categories.
    '''

    # delete prior session variables
    request.session.flush()

    # build and store dictionary for mapping id to category name in user session
    categories = getCategoryList(request)

    # create caching facilities
    request.session['rel_events'] = {}
    request.session['rel_events_list'] = []
    request.session['all_events'] = {}
    request.session['all_events_list'] = []
    request.session.modified = True

    # render the homepage with a listing of the retrieved categories
    return render(request, 'EventSearch/index.html', {'categories': categories})


def display_events(request):

    print request.session.items()

    # verify the presence of any category selections
    if any(cat in request.GET for cat in ('cat1', 'cat2', 'cat3')):
        # View triggered with category selections
        # (example: eventbrite.com/events/?cat1=103&cat2=101&cat3=110)

        # verify that each category selection exists
        if not 'cat1' in request.GET or not 'cat2' in request.GET or not 'cat3' in request.GET:
            return render(request, 'EventSearch/index.html', {'categories': request.session['categories'],
                                                              'form_error': 'Error: You must select 3 categories.'})

        # make a list of the relevant category ids
        rel_ids = [request.GET['cat1'], request.GET['cat2'], request.GET['cat3']]

        # verify that each category selection is unique
        if len(rel_ids) != len(set(rel_ids)):
            return render(request, 'EventSearch/index.html', {'categories': request.session['categories'],
                                                              'form_error': 'Error: Selections must be unique.'})

        # verify that each category exists in the categories session variable
        if not all(cat in request.session['categories'] for cat in rel_ids):
            # retrieve updated listing
            categories = getCategoryList(request)

            return render(request, 'EventSearch/index.html', {'categories': categories,
                                                              'form_error': 'Error: One or more of the selected '
                                                                            'categories no longer exists.'})

        # check if the user requested a specific page number
        if 'page' in request.GET:
            # query for page number of relevant events via Eventbrite API and store relevant information
            rel_events, pagination = getEventList(request, filter=rel_ids, page=request.GET['page'])
        else:
            # query for first page of relevant events via Eventbrite API and store relevant information
            rel_events, pagination = getEventList(request, filter=rel_ids)

        # compute number of events in previous pages
        prior_count = (pagination['page_number']-1)*pagination['page_size']

        # render with the relevant events with the names and ids of the categories
        return render(request, 'EventSearch/results.html', {'events': rel_events,
                                                            'event_count': pagination['object_count'],
                                                            'page_number': pagination['page_number'],
                                                            'num_pages':   pagination['page_count'],
                                                            'prior_count': prior_count,
                                                            'cat1_name': request.session['categories'][rel_ids[0]],
                                                            'cat2_name': request.session['categories'][rel_ids[1]],
                                                            'cat3_name': request.session['categories'][rel_ids[2]],
                                                            'cat1_id': rel_ids[0],
                                                            'cat2_id': rel_ids[1],
                                                            'cat3_id': rel_ids[2]})

    else:
        # View triggered by direct URL access
        # (example: eventbrite.com/events)

        # retrieve all the events
        if 'page' in request.GET:
            all_events, pagination = getEventList(request, page=request.GET['page'])
        else:
            all_events, pagination = getEventList(request)

        # compute number of events in previous pages
        prior_count = (pagination['page_number']-1)*pagination['page_size']

        # render with all events
        return render(request, 'EventSearch/results.html', {'events': all_events,
                                                            'event_count': pagination['object_count'],
                                                            'page_number': pagination['page_number'],
                                                            'num_pages':   pagination['page_count'],
                                                            'prior_count': prior_count})
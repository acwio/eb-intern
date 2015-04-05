from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests

def index(request):
    '''
    Renders the homepage of the application with all available categories.

    :param      request: an http/https request.
    :return:    the rendered homepage with a listing of categories.
    '''

    # request each of the categories via the eventbrite api
    raw_response = requests.get("https://www.eventbriteapi.com/v3/categories", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

    # decode the response in JSON
    response = raw_response.json()

    # delete prior rel_events session variable if it exists
    if 'rel_events' in request.session:
        del request.session['rel_events']

    # delete prior all_events session variable if it exists
    if 'all_events' in request.session:
        del request.session['all_events']

    # delete prior categories session variable if it exists
    if 'categories' in request.session:
        del request.session['categories']

    # build and store dictionary for mapping id to category name in user session
    request.session['categories'] = {cat['id']: cat['name'] for cat in response['categories']}

    # render the homepage with a listing of the retrieved categories
    return render(request, 'EventSearch/index.html', {'categories': response['categories']})


def display_events(request):
    # verify the presence of any category selections
    if any(cat in request.GET for cat in ('cat1', 'cat2', 'cat3')):
        # View triggered with category selections
        # (example: eventbrite.com/events/?cat1=103&cat2=101&cat3=110)

        # verify that each category selection exists
        if not request.GET['cat1'] or not request.GET['cat2'] or not request.GET['cat3']:
            return render(request, 'EventSearch/index.html', {'form_error': 'Error: Invalid selection.'})

        # verify that each category selection is unique
        if request.GET['cat1'] == request.GET['cat2'] or request.GET['cat1'] == request.GET['cat3']\
                or request.GET['cat2'] == request.GET['cat3']:
            return render(request, 'EventSearch/index.html', {'form_error': 'Error: Selections must be unique.'})

        # if a rel_events session variable exists, retrieve the relevant events via API
        if not 'rel_events' in request.session:
            # request the event listing via the eventbrite api
            raw_response = requests.get("https://www.eventbriteapi.com/v3/events", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

            # decode the response in JSON
            response = raw_response.json()

            # filter relevant events in the response by category id
            rel_ids = [request.GET['cat1'], request.GET['cat2'], request.GET['cat3']]
            rel_events_list = [event for id in rel_ids for event in response['events'] if id == event['category_id']]

            # store the filtered list in the user's session
            request.session['rel_events'] = rel_events_list

        # get the specified page number
        page = request.GET.get('page')

        # set-up the paginator to display 5 relevant events per page
        paginator = Paginator(request.session['rel_events'], 5)

        # try to paginate the list of relevant events
        try:
            rel_events = paginator.page(page)
        except PageNotAnInteger:
            # if the specified page number isn't a number, render the first page.
            rel_events = paginator.page(1)
        except EmptyPage:
            # if the specified page number is out of range, render last page.
            rel_events = paginator.page(paginator.num_pages)

        # render with the relevant events with the names and ids of the categories
        return render(request, 'EventSearch/results.html', {'events': rel_events,
                                                            'event_count': paginator.count,
                                                            'cat1_name': request.session['categories'][request.GET['cat1']],
                                                            'cat2_name': request.session['categories'][request.GET['cat2']],
                                                            'cat3_name': request.session['categories'][request.GET['cat3']],
                                                            'cat1_id': request.GET['cat1'],
                                                            'cat2_id': request.GET['cat2'],
                                                            'cat3_id': request.GET['cat3']})

    else:
        # View triggered by direct URL access
        # (example: eventbrite.com/events)

        if not 'all_events' in request.session:
            # request each of the categories via the eventbrite api
            raw_response = requests.get("https://www.eventbriteapi.com/v3/events", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

            # decode the response in JSON
            response = raw_response.json()

            # store the events in the user's session
            request.session['all_events'] = response['events']

        # set-up the paginator to display 5 events per page
        paginator = Paginator(request.session['all_events'], 5)

        # get the specified page number
        page = request.GET.get('page')

        # try to paginate the list of relevant events
        try:
            all_events = paginator.page(page)
        except PageNotAnInteger:
            # if the specified page number isn't a number, render the first page.
            all_events = paginator.page(1)
        except EmptyPage:
            # if the specified page number is out of range, render last page.
            all_events = paginator.page(paginator.num_pages)


        # render with all events
        return render(request, 'EventSearch/results.html', {'events': all_events,
                                                            'event_count': paginator.count})
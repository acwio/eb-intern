from django.shortcuts import render
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

    # render the homepage with a listing of the retrieved categories
    return render(request, 'EventSearch/index.html', {'categories': response['categories']})


def display_events(request):
    # verify the type of request
    if request.GET:
        # View triggered with category selections
        # (example: eventbrite.com/events/?cat1=103&cat2=101&cat3=110)

        # verify that each category selection exists
        if not request.GET['cat1'] or not request.GET['cat2'] or not request.GET['cat3']:
            return render(request, 'EventSearch/index.html', {'form_error': 'Error: Invalid selection.'})

        # verify that each category selection is unique
        if request.GET['cat1'] == request.GET['cat2'] or request.GET['cat1'] == request.GET['cat3']\
                or request.GET['cat2'] == request.GET['cat3']:
            return render(request, 'EventSearch/index.html', {'form_error': 'Error: Selections must be unique.'})

        # request each of the categories via the eventbrite api
        raw_response = requests.get("https://www.eventbriteapi.com/v3/events", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

        # decode the response in JSON
        response = raw_response.json()

        # render with all events
        return render(request, 'EventSearch/results.html', {'events': response['events']})

    elif request.POST:
        print 'It is a POST'

    else:
        # View triggered by direct URL access
        # (example: eventbrite.com/events)

        # request each of the categories via the eventbrite api
        raw_response = requests.get("https://www.eventbriteapi.com/v3/events", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

        # decode the response in JSON
        response = raw_response.json()

        # render with all events
        return render(request, 'EventSearch/results.html', {'events': response['events']})
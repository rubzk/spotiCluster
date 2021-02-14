# spotiCluster

The mission of this web app is to help you understand your taste in music. __Still WIP__

### How it works:

The app extracts your spotify data with [their public API](https://developer.spotify.com/documentation/web-api/), and then apply the famous clustering method [K-means](https://en.wikipedia.org/wiki/K-means_clustering) and plot some insights with [Plotly](https://plotly.com/python/).

### Composition:

The is a Flask web app with Celery to paralellize tasks and Plotly to create the plots.

### To-DO:

- PEP8 Refactor (__Currently Working on__)
- Automate number of clusters based on error.
- Fix responsive
- Refactor some celery stuff(bathces of requests)
- Add last trends in music plot
- Store data in Amazon S3 bucket.

## How to build:

Simplest way to run the project is by `docker-compose up`

For doing this you will need to create a `credentials.py` with the following variables:

 - __client_id__ 
 - __client_secret__ 
 - __redirect_uri__
 
After that you are free to go.









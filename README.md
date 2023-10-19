# spotiCluster

## Background of the project

I started this project a few years ago to get better with my coding skills. At that time I wanted to learn OOP. I got so involved and enjoy it so much that I started to use it to apply new things I wanted to learn. 

 - I started building a simple app that fetched data from spotify's API and clustered the data using  K-means.
 - Then I added a web app with simple Flask and some super simple Front-end with JS.
 - I learned about docker and I build a Docker Image and a Docker Compose.
 - Later I wanted to parallelize the whole workflow, I found Celery and implemented it.
 - I wasn't happy with the super simple frontend anymore so I learned how to use TailwindCSS to give it a better look.
 - I also wasn't happy with Plotly (The library I was using for Plots) and I learned how to build more interactive plots with ChartJS

### What am I working now? 

I found Pydantic library and I thought it will elevate the readability and the robustness of my code. So I'm learning on how to implement this to my pipeline.


### How it works:

The app extracts your spotify data with [their public API](https://developer.spotify.com/documentation/web-api/), and then apply the famous clustering method [K-means](https://en.wikipedia.org/wiki/K-means_clustering) and plot some insights with [ChartJS](https://www.chartjs.org/docs/latest/).


### To-DO:

- PEP8 Refactor (__Currently Working on__)
- Implement Pydantic (__Currently Working on__)
- Store data in Amazon S3 bucket.


## How to build:

Simplest way to run the project is by `docker-compose up`

For doing this you will need to add your credentials to the `config.cfg` file:

 - __client_id__ 
 - __client_secret__ 
 - __redirect_uri__
 
After that you are free to go.









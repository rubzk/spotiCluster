# spotiCluster

## Project Overview

This project was initiated several years ago with the primary goal of enhancing coding skills and mastering Object-Oriented Programming (OOP). Over time, it evolved into a dynamic platform for implementing various technologies and concepts. Here's the journey:

1. **Data Fetching and Clustering:** The project began with the development of a simple application that interfaced with Spotify's API to fetch data and applied K-means clustering to organize the information effectively.

2. **Web Application Integration:** The project expanded to include a web application using Flask, complemented by a clean and user-friendly front-end created with JavaScript, providing a seamless user experience.

3. **Containerization with Docker:** The introduction of Docker played a pivotal role in the project's architecture. It enabled the creation of a Docker Image and a Docker Compose setup, making the project more portable and easier to manage.

4. **Workflow Parallelization with Celery:** Recognizing the need for optimization, the project leveraged Celery to parallelize the entire workflow. This enhancement significantly improved the project's efficiency and responsiveness.

5. **Enhanced Front-End Aesthetics with Tailwind CSS:** To provide an appealing and modern user interface, the project embraced Tailwind CSS, giving the web app a polished and visually appealing design.

6. **Interactive Data Visualization with Chart.js:** While working on data visualization, the project transitioned from Plotly to Chart.js. This transition enabled the creation of more interactive and engaging visualizations to better convey insights from the data.

7. **Code Refactoring with Pydantic Models:** In a recent makeover, I refactored the code using Pydantic models to make it more readable and scalable. This change not only improved code clarity but also set the stage for future expansion and enhancements.

This project has been a wild ride of learning, trial, and error. It's proof that you can turn a small coding endeavor into a playground for all kinds of cool implementations


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









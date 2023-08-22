# MQTT to Kibana

As the title says. If you'd rather follow elasticsearch's guides:
- Elasticsearch
    - guide: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
    - docker install: https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
- Kibana:
    - guide: https://www.elastic.co/guide/en/kibana/current/index.html
    - docker install: https://www.elastic.co/guide/en/kibana/current/docker.html
- Logstash
    - guide: https://www.elastic.co/guide/en/logstash/current/introduction.html

## Steps to Reproduce

1. Install Docker Desktop (https://docs.docker.com/desktop/install/ubuntu/)
2. Pull the [kibana](https://hub.docker.com/_/kibana) and [elasticsearch](https://hub.docker.com/_/elasticsearch) docker containers (just enter these keywords in the search bar at the top). It's important that your versions match, the version I downloaded was 8.8.1.

![kibana download from docker desktop](images/kibana-download-docker-desktop.jpg)

3. In the "images" tab, run the `elastic` container. Set a name and make sure to specify the host ports. Do the same thing with your `kibana` image.

![create elasticsearch container](images/run-container.jpg)

4. Now you should be able to view your container instances of kibana and elasticsearch in the "Containers" tab. I named my elasticsearch instance "es01" and my kibana instance "funny_hofst"

![container listing](images/container-listing.jpg)

5. Start your elastic container first from the "Containers" tab. If you don't see a port mapping listed in the ports tab, delete the container and go back to step 3. If you click on the name, you should see the tabs named  "logs", "inspect", "bind mounts", "terminal", "files", "stats" 

6. In the "logs" tab of your elastic container, there should be an enrollment token and user password printed to the log. If you're like me and didn't notice, you can open the "terminal" tab and run the following script:

```
cd /usr/share/elasticsearch/bin
./elasticsearch-reset-password -u elastic
./elasticsearch-create-enrollment-token -s kibana
```

7. Before you start your kibana container, download the `http_ca.crt` to your local machine from `/usr/share/elasticsearch/config/certs/http_ca.crt` within your elasticsearch container. You can find this file by browsing to the "files" tab of the elasticsearch container. If you don't have one, in the elasticsearch container terminal:

```
cd /usr/share/elasticsearch/bin
./elasticsearch-certutil ca
```

To verify the ca cert is good, run the following command. You may have to enter the password generated in step #6. 

```
curl --cacert http_ca.crt -u elastic https://localhost:9200
```

A successful output looks like:

![good curl](images/good-curl.jpg)

8. Start your kibana container. The logs might print out a URL to browse to; otherwise browse to `127.0.0.1:5601` and enter the information that you just created, username `elastic`. You should now be able to log in to Kibana.

![kibana splash](images/kibana-splash.jpg)

9. Now is time to get MQTT set up. I used the Mosquitto MQTT broker because it is natively installed on [DragonOS](https://cemaxecuter.com/). You can [download Mosquitto MQTT broker here](https://mosquitto.org/download/). Run the following commands after install

```
sudo systemctl start mosquitto.service
sudo systemctl status mosquitto
```

Here's a good status report:

![good mqtt status](images/mqtt-status.jpg)

10. Enter your `username:password` in the `.passwords` file that is at the same level as `subscriber.py`. For example, `.passwords` should look like:

```
elastic:mYSup3rs3cr3tp@$$w0rd!
```

11. If you're a pip purist and don't want to pollute your system with a [elasticsearch Python package](https://pypi.org/project/elasticsearch/) and [paho mqtt](https://pypi.org/project/paho-mqtt/) for MQTT  Python implementation, you can run a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```

In either case, run the following to install necessary requirements

```
pip3 install -r requirements.txt
```

12. Start the publisher. Edit the location of your `http_ca.crt` in `subscriber.py`, then start the subscriber (yes I will make this more user friendly in the future). You should see no error messages and the output is populating roughly every two seconds in the terminal window

13. Back in Kibana on the home screen, scroll down until you see a cog wheel next to blue highlighted text "stack management". Click on that, then on the left side, click on "data view".

![data view config](images/data-view-editor.jpg)

14. Create a new data view. If we're successful, you should see `mqtt_data` in the right of the screen. This is from line 11 of `subscriber.py` where the `es_index` variable is set. Use regex to match the source name, for example `mqtt*` or `mqtt_data`. Save the data view to kibana.

![add new data view](images/create-data-view.jpg)

15. Back from the home page, go to the "Discover" tab

![kibana discover](images/discover-tab.jpg)

16. Select your new data view. 

![select data view](images/select-data-view.jpg)

17. Congrats! You should now be able to visualize the data that the Python client is sending around. It might take a minute to appear in Kibana if you are just starting, let the publisher & subscriber run for a couple of minutes before refreshing kibana.

## Todo

- [ ] use [logstash](https://www.elastic.co/guide/en/logstash/current/first-event.html) (you can pull the [logstash docker](https://hub.docker.com/_/logstash) just as you did with kibana and elasticsearch) to parse data from `publisher.py` and ingest it into Kibana via Elastic. I spent a lot of time trying to figure out [filebeat](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-overview.html) but it didn't work.
- [ ] parameterize the publisher and subscriber so that there isn't any need to edit the source
- [ ] figure out mapping features:
   - https://www.elastic.co/guide/en/kibana/current/maps-getting-started.html
   - https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html
   - Instead of "discover" go to "dashboard", create a new dashboard, then select the "maps" button that is 3 icons to the right of "create visualization"

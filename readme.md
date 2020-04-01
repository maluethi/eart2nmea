A little script to fuse [google earth pro][1] (desktop edition) and [xcsoar][2] together.

![demot_image](https://imgur.com/JarFK2f.png)

## Experimental Installation and Usage
1. The script has no external dependencies, it was written for python3.*
1. Make the cgi script executable:
    ```bash
    $ chmod +x cgi-bin/out_pos.py
    ```
3. Start a simple http server using python with cgi enabled, do this in the project base directory.
    ```bash
    $ python -m http.server --cgi 8000
    ```
1. Add the link.kml to your google earth pro and activate it. Now you should see output on the http server:
    ```bash
    127.0.0.1 - - [01/Apr/2020 17:49:52] "GET /cgi-bin/out_pos.py?CAMERA=7.479937580087384,46.32363475209464,7252.86;VIEW=17.813,-0.893 HTTP/1.1" 200 - 
    ```
5. Configure a new device on XCsoar. It should listen for UDP packets on port 10110, select FLARM as a driver.
6. Enjoy the views!

\* Optionally you can setup the python environment using the `requirements.txt` or totally by yourself. In this case you have to be careful about which python interpreter is used in the cgi script. You might want to adapt the first line of the script (i.e. `#!/bin/$PATH_TO_PYTHON/python`)

### Debuging & Issues
* If the http server dies, google earth pauses accessing the cgi-script. After you bring your server up again you have to manually tell google earth to send data again by refreshing the "Network Link" (right click on the element in the places tab)

[1]: https://www.google.ch/intl/de_ALL/earth/versions/#earth-pro
[2]: https://www.xcsoar.org/

# Minimal python CMS

## Configuration options:
````
[Webserver]
Host:        127.0.0.1
Port:        8080
Debug:       True
SSL:         False
Certificate: ./ssl/ssl.crt 
Key:         ./ssl/ssl.key
[Logging]
Logging:     True
Logfile:     ./log/webserver.log
MaxSize:     100MB
Backlog:     5
````

## Routes File
You can set which pages need to be loaded when a route is fetched in the `web/Routes.py file`

The `ROOT` is the route that should be used when page `/` is fetched. (e.g index.html)

The `ROUTES` variable is a list of routes that are accessible. Each route is a dictionary with the following keys:

| key | meaning                       | required/optional       |
|-----|-------------------------------|-------------------------|
| r   | route to be accessed          | required                |
| p   | path to the jinja file        | required                |
| c   | content generators to be used | optional                |
| h   | helper (content generator)    | required when c is used |
| s   | settings for the helper       | optional                |
 
Look at `web/Routes.py` for examples.

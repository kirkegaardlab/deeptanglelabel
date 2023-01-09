# DeepTangle-Label

Ensure you have a database, or create one using
```
python manage.py migrate
```

To run a local server
```
python manage.py runserver
```

To run a production server, you can use the provided dockerfile as:
```
(sudo) docker-compose build  # first time
(sudo) docker-compose up     # start server (add -d for detached)
(sudo) docker-compose down   # stop server
```


## Images
Images to be labelled should be placed in separate folders
(folder name will be stored in database) in
```
label/static/
```
The image should be named `w.png`.
If you want to include surrounding frames (e.g. from a video)
these should be named in the fashion of
```
w_-2.png
w_-1.png
w.png
w_+1.png
w_+2.png
w_+3.png
```
See `label/static/001/` for an example.

## Development
Relevant files to change, if need be:
```
label/views.py
labels/templates/main.html
labels/templates/show.html
label/models.py
label/urls.py
```

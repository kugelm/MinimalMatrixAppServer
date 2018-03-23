# MinimalMatrixAppServer

Implementation of the example from the matrix.org web site using the twisted framework.
(if you installed the matrix-synapse server you have the twisted framework installed already...):
* TwistedMinimalMatrixAppicationServer.py
* appserver-twiminmatas.yaml (example config file for this app server)

Additional shell scripts for some basic functions using curl on the console (tested under MacOS:
* upload_media.sh: POST a media file and use the mxc URI in the response later
* get_room_id.sh: very simple... translate #room_id to internal id
* set_power_level_100.sh: get admin level for individual users in AS generated rooms 
* kick_user.sh: get rid of not invited users in the role of AS admin
* set_room_avatar.sh: self explaining

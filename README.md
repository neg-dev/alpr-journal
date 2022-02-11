# Russian license plate detection service(ALPR journal service)
Recieve jpg image from ip-cam, if numberplate detected, draw rectangle and store detected Licence plates as JPG images in folder with DATE,CAM_NUMBER,DETECTED_LP in filename.

Write DATE,CAM_NUMBER,DETECTED_LP,PATH_TO_IMAGE in CSV file in same folder.

# Run python script as service
To run python script as service on Ubuntu 18

Create .service file in folder /lib/systemd/system/
<pre>
sudo nano /lib/systemd/system/alpr-cam1.service
</pre>
With content:
<pre>
[Unit]
Description=Numbers detection Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
User=NAME_OF_USER
Group=users
WorkingDirectory=/PATH_TO_WORKING_DIRECTORY

Type=simple
ExecStart=/usr/bin/python3.6 /PATH_TO_SCRIPT_DIRECTORY/alpr-cam1.py
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
</pre>

After any changes restart daemon:
<pre>
sudo systemctl daemon-reload
</pre>
Enabling start on boot:
<pre>
sudo systemctl enable alpr-cam1.service
</pre>
For service status:
<pre>
sudo systemctl status alpr-cam1.service
</pre>

<pre>
sudo systemctl stop dummy.service          #To stop running service 
sudo systemctl start dummy.service         #To start running service 
sudo systemctl restart dummy.service       #To restart running service
</pre> 


# Simple web access
install python module:
<pre>
sudo pip3 browsepy
</pre>
Create service config:
<pre>
sudo nano /lib/systemd/system/webfolder.service
</pre>
Content:
<pre>
[Unit]
Description=WebFolders service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
User=NAME_OF_USER
Group=users
WorkingDirectory=/PATH_TO_WORKING_DIRECTORY

Type=simple
ExecStart=/bin/bash -c "/usr/bin/python3.6 -m browsepy 0.0.0.0 5000 --directory /PATH_TO_MAIN_IMAGES_DIRECTORY/"
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
</pre>

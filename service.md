# Make systemd service
First of all, we are going to write a small python script which print "Hello World" every 60 seconds. This is going to be our service script (hello_world.py):
Code: Select all
```python
#!/usr/bin/python
 
from time import sleep

try:
    while True:
        print "Hello World"
        sleep(60)
except KeyboardInterrupt, e:
    logging.info("Stopping...")
```
You can execute it by python hello_world.py. If you get boring reading so many hello worlds, press Ctrl+C (or Cmd+C on OSX) to stop it. Save this file as hello_world.py in your home folder (home/pi/). Now we're going to define the service to run this script:
Code: Select all
```bash
cd /lib/systemd/system/
sudo nano hello.service
```

The service definition must be on the /lib/systemd/system folder. Our service is going to be called "hello.service":
Code: Select all
```bash
[Unit]
Description=Hello World
After=multi-user.target
 
[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/hello_world.py
Restart=on-abort
 
[Install]
WantedBy=multi-user.target
```

Here we are creating a very simple service that runs our hello_world script and if by any means is aborted is going to be restarted automatically. You can check more on service's options in the next wiki: https://wiki.archlinux.org/index.php/systemd.

Now that we have our service we need to activate it:
Code: Select all
```bash
sudo chmod 644 /lib/systemd/system/hello.service
chmod +x /home/pi/hello_world.py
sudo systemctl daemon-reload
sudo systemctl enable hello.service
sudo systemctl start hello.service


sudo chmod 644 /lib/systemd/system/hello.service
chmod +x /home/pi/hello_world.py
sudo systemctl daemon-reload
sudo systemctl enable hello.service
sudo systemctl start hello.service
```

For every change that we do on the /lib/systemd/system folder we need to execute a daemon-reload (third line of previous code). If we want to check the status of our service, you can execute:
Code: Select all
```bash
sudo systemctl status hello.service
```
In general:
Code: Select all
```bash
# Check status
sudo systemctl status hello.service

# Start service
sudo systemctl start hello.service

# Stop service
sudo systemctl stop hello.service

# Check service's log
sudo journalctl -f -u hello.service
```
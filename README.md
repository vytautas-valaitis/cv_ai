sudo su  
apt install zsh neovim  
apt install nginx git python3-dev python3-venv build-essential poppler-utils  
git clone git@github.com:vytautas-valaitis/cv\_ai.git  
  
cd /var/www/cv\_ai/  
python3 -m venv venv  
source venv/bin/activate  
python -m pip install wheel  
python -m pip install -r requirements.txt  
deactivate  

useradd srv  
mkdir /home/srv  
chown srv:srv /home/srv  

mkdir /tmp/cv-server  
chown -R srv:www-data /tmp/cv-server  
chown -R srv:www-data /var/www  

vi /etc/nginx/nginx.conf
```
user srv;  
        fastcgi_buffers 8 16k;  
        fastcgi_buffer_size 32k;  
        
        client_max_body_size 24M;  
        client_body_buffer_size 128k;  
  
        client_header_buffer_size 5120k;  
        large_client_header_buffers 16 5120k;  
```  
vi /etc/nginx/sites-available/cv\_ai  
```
server {  
    listen 80;  
  
    location / {  
        include proxy_params;  
        proxy_pass http://unix:/tmp/cv-server/ipc.sock;  
    }  
}  
```  
ln -s /etc/nginx/sites-available/cv\_ai /etc/nginx/sites-enabled/cv\_ai  
  
vi /etc/systemd/system/cv-server.service  
```
[Unit]  
Description=CV AI  
After=network.target  
 
[Service]  
User=srv  
Group=www-data  
WorkingDirectory=/var/www/cv_ai  
Environment="PATH=/var/www/cv_ai/venv/bin:/usr/bin" # cia panasu i saugumo spraga  
ExecStart=/bin/bash -c 'source /var/www/cv_ai/venv/bin/activate; gunicorn -w 3 --bind unix:/tmp/cv-server/ipc.sock wsgi:app  
Restart=always  
  
[Install]  
WantedBy=multi-user.target  
```  
rm /etc/nginx/sites-enabled/default  
systemctl start nginx  
  
(get vision\_api.json)  
  
systemctl status cv-server  
systemctl start cv-server  
systemctl stop cv-server  
  

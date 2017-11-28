# WeTwo

## 简易配置教程

本教程为使用Gunicorn和Nginx将此WeTwo Flask APP配置到Ubuntu 16.04上，详细教程可参考[How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 16.04 | DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-16-04)。

### 安装依赖

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-dev nginx
```

### 创建Python虚拟环境

```bash
sudo pip3 install virtualenv
```

```bash
cd ~/wetwo-server
virtualenv wetwoenv
```

### 安装Flask依赖

```bash
source myprojectenv/bin/activate
```

```bash
pip install gunicorn flask
```

```bash
pip install flask_login pymysql
```

```bash
deactivate
```

### 创建WSGI入口

```bash
nano ~/wetwo-server/wsgi.py
```

写入内容为：

```python
from Server import app

if __name__ == "__main__":
    app.run()
```

### 配置systemd

```bash
sudo nano /etc/systemd/system/wetwo.service
```

写入内容为（此处当前用户名为`ubuntu`，酌情修改）：

```
[Unit]
Description=Gunicorn instance to serve WeTwo
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/wetwo-server
Environment="PATH=/home/ubuntu/wetwo-server/wetwoenv/bin"
ExecStart=/home/ubuntu/wetwo-server/wetwoenv/bin/gunicorn --workers 2 --bind unix:wetwo.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start wetwo
sudo systemctl enable wetwo
```

### 配置Nginx

```bash
sudo nano /etc/nginx/sites-available/wetwo
```

写入内容为（需修改`server_domain_or_IP`；此处当前用户名为`ubuntu`，酌情修改）：

```
server {
    listen 80;
    server_name server_domain_or_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/wetwo-server/wetwo.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/wetwo /etc/nginx/sites-enabled
```

```bash
sudo systemctl restart nginx
```

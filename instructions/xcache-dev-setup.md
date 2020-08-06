# Setting Up Development XCache with Origin Server

This guide uses [Riccardo's Docker Image](https://github.com/riccardodimaria/containers). Clone the container code first.

```
$ git clone https://github.com/riccardodimaria/containers
$ cd containers
```

## Building Docker images
Follow the instructions on the repo page on how to build the images.
```
$ docker build -t containers/origin_xrootd_stable origin/origin_xrootd_stable
$ docker build -t containers/origin_xrootd_stable xcache/xcache_xrootd_stable_standalone
```

## Running the Docker containers
### Create a shared network
```
$ docker network create xrd
```

### Run the Origin
```
$ docker run -dit \
    -v /path/to/hostcert.pem:/tmp/container_cert/hostcert.pem \
    -v /path/to/hostkey.pem:/tmp/container_cert/hostkey.pem \
    -v /path/to/ca.pem:/etc/grid-security/certificates/<certhash>.0 \
    -v /path/to/mockstorage/data:/data/xrd \
    -h origin \
    --name origin \
    --network xrd \
    -p 12139:1213 -p 10949:1094 containers/origin_xrootd_stable
```

### Run the Xcache
```
$ docker run -dit \
    -v /path/to/hostcert.pem:/tmp/container_cert/hostcert.pem \
    -v /path/to/hostkey.pem:/tmp/container_cert/hostkey.pem \
    -v /path/to/xrdcert.pem:/tmp/container_cert/xrdcert.pem \
    -v /path/to/xrdkey.pem:/tmp/container_cert/xrdkey.pem \
    -v /path/to/ca.pem:/etc/grid-security/certificates/<certhash>.0 \
    -h xcache \
    --name xcache \
    --network xrd \
    -p 12133:1213 -p 10943:1094 containers/xcache_xrootd_stable_standalone
```

## Configuring the Docker containers
### Origin
1. Populate a mock file on your `/path/to/mockstorage`.
2. Execute a shell on the origin container.
```
$ docker exec -it origin /bin/bash
```
3. Modify `/etc/xrootd/Authfile` to your needs. A quick catch-all configuration to allow everyone to access anything is `u * / a`.
4. Restart container
```
$ docker restart origin
```

### Xcache
1. Execute a shell on the origin container.
```
$ docker exec -it xcache /bin/bash
```
2. Modify `/etc/xrootd/Authfile` to your needs. A quick catch-all configuration to allow everyone to access anything is `u * / a`.
3. Generate a proxy certificate to authorize XCache to access origin. Run this every 12 hours.
```
$ sudo -u xrootd voms-proxy-init -cert /etc/grid-security/xrd/xrdcert.pem -key /etc/grid-security/xrd/xrdkey.pem
```
4. Restart container
```
$ docker restart xcache
```
# diavlos

<p align="center"> <img src="resources/logo.jpg?raw=true"/> </p>

## API for Diavlos - Greece's National Service Registry

### Install:
```bash
./make
```

### Set credentials:

Edit the following files under diavlos/data/in/ (first remove the `.sample` suffix):
```
english_site_config.yaml
eparavolo_credentials.yaml
greek_site_config.yaml
```

### Serve API locally
```bash
cd scripts
./serve_api --generate-new-schemas
```

### Visit API UI docs
```bash
http://localhost:5000/v1/ui/
```

## Docker

Build the image using:

```bash
docker-compose build
```

After setting the credentials as described above, execute the service using:

```bash
docker-compose up
```


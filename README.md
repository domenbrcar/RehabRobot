# Zagon interaktivne beležke:

``` go to vaje_ws

```bash
rocker --devices /dev/dri --x11 --pulse --user --network=host --env-file .env -e NOTEBOOK_ROOT_DIR=~/vaje_ws --home --volume ./jupyter_entrypoint.sh:/entrypoint.sh --image-name vaje_rocker rbs-docker-vaje:latest                    
```

# Namestitev

```
git clone https://repo.ijs.si/msimonic/hri-franka ~/vaje_ws
cd ~/vaje_ws

# Če rbs-docker še ni nameščen.
# git clone https://repo.ijs.si/hcr/rbs-docker
# cd rbs-docker
# docker build . -t rbs-docker

docker build . -t rbs-docker-vaje
```

#!/bin/bash
urle() {
    [[ "${1}" ]] || return 1
    local LANG=C i x
    for ((i = 0; i < ${#1}; i++)); do
        x="${1:i:1}"
        [[ "${x}" == [a-zA-Z0-9.~-] ]] && echo -n "${x}" || printf '%%%02X' "'${x}"
    done
    echo
}
COLOR='\033[0;32m'

# username and password input
echo -e "\nIf you do not have an account you can register at https://flame.is.tue.mpg.de/ following the installation instruction."

# Load the FLAME_USERNAME and FLAME_PASSWORD from the .env environment variables file if it exists
if [ -f ".env" ]; then
    source .env
fi

# If FLAME_USERNAME and FLAME_PASSWORD are not set, prompt the user for them
if [ -z "$FLAME_USERNAME" ] || [ -z "$FLAME_PASSWORD" ]; then
    echo -e "\n${COLOR}Please enter your FLAME credentials:"
    read -p "Username (FLAME): " FLAME_USERNAME
    read -sp "Password (FLAME): " FLAME_PASSWORD
    echo
fi

# If FLAME_USERNAME and FLAME_PASSWORD are set, use them
if [ -n "$FLAME_USERNAME" ] && [ -n "$FLAME_PASSWORD" ]; then
    username=$FLAME_USERNAME
    password=$FLAME_PASSWORD
else
    echo -e "\n${COLOR}Please enter your FLAME credentials:"
    read -p "Username (FLAME): " username
    read -sp "Password (FLAME): " password
    username=$(urle $username)
    password=$(urle $password)
fi

echo -e "\n${COLOR}Downloading FLAME..."
mkdir -p data/FLAME2020/
wget --post-data "username=$username&password=$password" 'https://download.is.tue.mpg.de/download.php?domain=flame&sfile=FLAME2020.zip&resume=1' -O './FLAME2020.zip' --no-check-certificate --continue
unzip FLAME2020.zip -d data/FLAME2020/
rm -rf FLAME2020.zip
mv data/FLAME2020/Readme.pdf data/FLAME2020/Readme_FLAME.pdf

wget --post-data "username=$username&password=$password" 'https://download.is.tue.mpg.de/download.php?domain=flame&resume=1&sfile=TextureSpace.zip' -O './TextureSpace.zip' --no-check-certificate --continue
unzip TextureSpace.zip -d data/FLAME2020/
rm -rf TextureSpace.zip

wget 'https://files.is.tue.mpg.de/tbolkart/FLAME/FLAME_masks.zip' -O './FLAME_masks.zip' --no-check-certificate --continue
unzip FLAME_masks.zip -d data/FLAME2020/
rm -rf FLAME_masks.zip

echo -e "\n${COLOR}Downloading Mesh..."
wget -O mesh.zip "https://keeper.mpdl.mpg.de/f/f158a430ef754edba5ec/?dl=1"
unzip mesh.zip -d data/
mv data/mesh/* data/
rm -rf data/mesh
rm -rf mesh.zip

source configure_environment.sh
echo -e "\n${COLOR}Installing micromamba env..."
micromamba env create -f environment.yml

echo -e "\n${COLOR}Installation has finished!"

# Reset the terminal color
echo -e "\033[0m"

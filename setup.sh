sudo apt-get install python3 docker
tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
cd $tmp_dir
git clone https://github.com/amir656/btExperiment.git
cd btExperiment
cp -r ~/torrents torrents
cp ~/*.sh .
sudo docker build -t kraken .

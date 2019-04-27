sudo apt-get update -y
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository -y \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo apt-get install -y python
tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
touch dir.txt
echo "$tmp_dir" > dir.txt
cd $tmp_dir
git clone https://github.com/amir656/btExperiment.git
cd btExperiment
cp -r ~/torrents torrents
cp ~/*.sh .
sudo docker build -t kraken .

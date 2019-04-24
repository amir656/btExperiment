# Bittorrent Experiment

## Getting Started

Install python and docker

`sudo apt-get install python2.7 docker`

### Setup

Specify the setup of your experiment in a json file. A template is provided in default.json:

```
{
    Identity_file you would like to use. Leave this blank to use default.
    "identity_file":     ".ssh/id_rsa.pub",
    Host that you want to run your tracker on
    "tracker_host":      "localhost",

    Hosts that you want to run your seeders on
    "seeder_hosts":      ["localhost"],

    How many seeders to spin up on each seederHost.
    "seeders_per_host":  2,

    Hosts that you want to run your leechers on
    "leecher_hosts":     ["localhost", "localhost"],

    How many leechers to spin up on each leecherHost.
    "leechers_per_host": 1,

    A list of torrent sizes you'd like each seeder/leecher to download/upload
    "torrent_sizes":     [1024, 5120, 10240, 20480],

    In kb/second
    "upload_rate": 200,
    "download_rate": 300
}
```

## Running the experiment

Once you've set up your hosts, and your .json file, you can run your experiment with

`python run_experiment.py --config {fileName}.json`

## Fetching logs
`run_experiment.py` stores the locations of the logs by each host and run. You can fetch them by running:

`python agg_logs.py -f log_locations/{HostName}{timeStamp}.json`

This stores the logs under `logs/{HostName}{timeStamp}.txt`.

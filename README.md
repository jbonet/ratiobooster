# ratiobooster
Boost your ratio in Private Trackers by being an early bird

## How does it work?
Ratiobooster checks the trackers specified in the config file looking for the torrents which meet the seeders, leechers and completed conditions. This way you can choose to only download a torrent when there is a single seed and no one has completed it yet, being able to seed way more than if there were already other seeds.

## Will I get banned? 
Ratiobooster acts as a Web Browser to get the torrent list from the trackers website and relies on your cookie session to perform authentication. This way the tracker can only know that you are accessing the website just as if you were doing it for real. In short, no, it is very unlikely.

In any case, I do not take responsibility for any problems it may cause. Use at your own risk.

### Requirements

In order to work, ratiobooster depends on:

```
joblib==0.11
lxml==3.5.0
PyYAML==3.12
requests==2.18.3
```

These dependencies can easily be installed by running:

```
pip install -r requirements.txt
```

Also, lxml needs some packages of its own to be installed before it can compile:

- libxml2
- libxslt1

To install them in **Ubuntu >=14.04** run:

```
sudo apt-get install libxml2-dev libxslt1-dev
```

Check online for the package names in other distros.

### Config & Running

Once the requirements are met, the script will run. But first we need to specify a config. Create a file called **config.yml** and follow the structure specified in the sample config provided.

Consider this:
- The tracker name has to match the parser file name in the **modules folder**
- Cookie and enabled are the only required params for a tracker.
- Every other param will override the global param for the tracker.

Now we are in place to run the script.

Just run:
```
python ratiobooster.py
```
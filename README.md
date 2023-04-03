# evo_traffic

This project is about using evolutionary algorithms to improve road traffic.

## Folders
1. inputs: simulation inputs, such as maps, routes, and configuration files;
2. outputs: simulation outputs, such as information of trips and routes;
3. scripts: python scripts using traci to control the simulation dynamically.

## Configure SUMO on macOS
Step 1a. Install Homebrew:
```bash
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Step 1b. If you have installed Homebrew, make sure it is up-to-date:
```bash
brew update
```

Step 2. Install SUMO stable:
```bash
brew tap dlr-ts/sumo
brew install sumo
```

Step 3. To enable ``sumo-tools`` (e.g. traci, sumolib, ...), download the full version of SUMO: 

https://sourceforge.net/projects/sumo/files/sumo/version%201.2.0/sumo-all-1.2.0.zip/download

Step 4. Configure the environment variable: ``SUMO_HOME``. E.g.:
```bash
export SUMO_HOME="/Users/shenwang/Downloads/sumo-1.2.0"
```

## Grid Scenario Generation
This is to show how ``8x8`` scenario is generated:

Step 1. Generate grid map:
```bash
netgenerate --grid --grid.number=2 --grid.length=400 --output-file=test_8x8_400.net.xml
```

Step 2. Generate uniformly distributed traffic:
```bash
python /Users/shenwang/Downloads/sumo-1.2.0/tools/randomTrips.py -n test_8x8_400.net.xml -r test_8x8_400.rou.xml --fringe-factor 10
```

Step 3. Prepare ``*.sumocfg`` file accordingly.
Can refer to:

https://github.com/namnatulco/sumo-complete/blob/master/sumo/data/xsd/sumoConfiguration.xsd
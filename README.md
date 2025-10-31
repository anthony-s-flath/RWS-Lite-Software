# RWS Lite Software

Driver software and documentation for the RWS Lite project.

RWSLite, or Radiation Weather Station Lite, is affordable but comprehensive set of sensors mounted on a Raspberry Pi.

## Setup
For Raspberry Pi:
- `git clone https://github.com/anthony-s-flath/RWS-Lite-Software`
- `cd RWS-Lite-Software`
- `sudo chmod +x bin/setup.sh`
- `sudo ./bin/setup.sh`
- `sudo raspi-config` > Interfacing Options > I2C > Enable
- `source env/bin/activate`

For debug (Using apt on non Raspberry Pi OS):
- Update system
- `sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget dropbox`
- Install/update python and pip
- `python -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`
- `pip install -e .`


## How to use
Once set up, use `rws --help` for command line options.
See the [docs/option_example.txt](doc) for an example of an options file.

If using after a cold reboot of the Raspberry Pi, run
- `sudo pigpiod`
- `source env/bin/activate`


## Documentation

All documentation is in the `docs` directory. Here are a list of their uses.

- [ ] [RWS Software Documentation](docs/RWS_Software_Documentation.md): Software setup and execution
- [ ] [RWS Hardware Documentation](docs/RWS_Hardware_Documentation.csv): Hardware component specs
- [ ] [Dropbox Setup](docs/Dropbox_Setup.md): Data transfer tutorial


## Notes

- [ ] On an outdated Raspberry Pi OS (version < 13), you may need to run `./bin/full_setup.sh`
- [ ] There may be discrepancies between time with time.time() in UTC (?)
- [ ] On non-DEBUG: something to do with w1thermsensor lib boot file -  https://github.com/timofurrer/w1thermsensor/issues/42
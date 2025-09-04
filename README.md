# RWS Lite Software

Driver software and documentation for the RWS Lite project.

RWSLite, or Radiation Weather Station Lite, is affordable but comprehensive set of sensors mounted on a Raspberry Pi.

# Setup
- `sudo pigpiod`
- `pip install -r requirements.txt`
- `pip install -e .`
- `sudo systemctl enable dropbox.service & sudo systemctl start dropbox.service `
- `rws [STATION_NAME] [PUBLIC_KEY] [PRIVATE_SECRET]`
- On non-DEBUG: something to do with w1thermsensor lib boot file -  https://github.com/timofurrer/w1thermsensor/issues/42

## Documentation

All documentation is in the `docs` directory. Here are a list of their uses.

- [ ] [RWS Software Documentation](docs/RWS_Software_Documentation.md): Software setup and execution
- [ ] [RWS Hardware Documentation](docs/RWS_Hardware_Documentation.csv): Hardware component specs
- [ ] [Dropbox Setup](docs/Dropbox_Setup.md): Data transfer tutorial

/etc/systemd/system

## Notes

- [ ] Many scripts and station files are not needed
- [ ] There may be discrepancies between time with time.time() in UTC (?)
# RWS Lite Software

Driver software and documentation for the RWS Lite project.

RWSLite, or Radiation Weather Station Lite, is affordable but comprehensive set of sensors mounted on a Raspberry Pi.

## Documentation

All documentation is in the `docs` directory. Here are a list of their uses.

- [ ] [RWS Software Documentation](docs/RWS_Software_Documentation.md): Software setup and execution
- [ ] [RWS Hardware Documentation](docs/RWS_Hardware_Documentation.csv): Hardware component specs
- [ ] [Dropbox Setup](docs/Dropbox_Setup.md): Data transfer tutorial

/etc/systemd/system 

sudo systemctl enable dropbox.service && sudo systemctl start dropbox.service 
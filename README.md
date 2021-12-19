# SIPp scripts generator

The main purpose of the project is authomation of the writing SIPp scripts.
The project must generate SIPp scripts using .pcap file.

# Using

The UI of program is quite intuitive:

<img src="https://user-images.githubusercontent.com/52322772/146679739-1601c7ca-41e4-4319-90d3-96ce627348f0.png" width="50%" height="50%">

The results are generated .XML and .CSV files for each side of call (CLI and CLD). Schema of using the .CSVs:
<img src="https://user-images.githubusercontent.com/52322772/146680410-4d6e3be4-63d5-46d5-86a2-892f7f50c438.png" width="40%" height="40%">


### Requirements
- Python 3.10
- tShark (included in PyShark)
- PyShark
- Tkinter
The libs installing:
```
pip install pyshark
pip install python-tk
```

### Workflow diagram
<img src="https://user-images.githubusercontent.com/52322772/146680576-de21b2af-d42e-4be2-b111-f20b58e45e62.png" width="50%" height="50%">



### Issues
[Strange getting SDP](https://github.com/KimiNewt/pyshark/issues/508)

### Known limitations (future improvements)
- UDP only;
- doesn't support BLF;
- requires lots of time when large .pcap file is loaded.
- doesn't generate media files.

### License
[GNU GPLv3](ttps://en.wikipedia.org/wiki/GNU_General_Public_License)

![image](https://user-images.githubusercontent.com/52322772/146680496-33c573a9-ceb4-4a2c-ada4-fa6929827e58.png)

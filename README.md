# pyfuzz_can

Dependencies:
- Python 2.7.X
  https://www.python.org/downloads/
  
- Mercurial (to get Python-CAN)
  https://www.mercurial-scm.org/wiki/Download
  
- Python-CAN 
  https://bitbucket.org/hardbyte/python-can
  
Setup:

1. Clone Python-CAN to your local machine:
  
  `$> hg clone https://bitbucket.org/hardbyte/python-can`
  
2. Install Python-CAN normally with:
  ```
  $> cd python-can
  $> python setup.py install
  ```
  
3. Create interface config file for Python-CAN at ~/can.conf:
  ```
  [default]
  interface = pcan
  channel = PCAN_USBBUS1
  ```
  The interface and channel given are for PEAK PCAN-USB. These will change depending on your CAN interface. Refer to the Python-CAN documentation for your device's configuration : http://python-can.readthedocs.io/en/latest/configuration.html.
  
4. Clone pyfuzz_can to your local machine:

  `$> git clone https://github.com/bhass1/pyfuzz_can.git`
  
5. You are ready to fuzz. Try:
  ```
  $> cd pyfuzz_can
  $> python fuzzer.py
  ```

For help use:

`$> python fuzzer.py --help`

Common Issues
  1. `OSError: libpcanbasic.so: cannot open shared object file: No such file or directory`
    Don't forget to install device drivers for your platform. On Linux, you need to download and install the peak-linux-driver (http://www.peak-system.com/fileadmin/media/linux/index.htm) and PCAN-Basic API (http://www.peak-system.com/produktcd/Develop/PC%20interfaces/Linux/PCAN-Basic_API_for_Linux/PCAN_Basic_Linux-4.2.0.tar.gz)

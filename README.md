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
  The interface and channel given are for PEAK PCAN-USB. These will change depending on your CAN interface.
  
4. Clone pyfuzz_can to your local machine:

  `$> git clone https://github.com/bhass1/pyfuzz_can.git`
  
5. You are ready to fuzz. Try:
  ```
  $> cd pyfuzz_can
  $> python fuzzer.py --help
  ```

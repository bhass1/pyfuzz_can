# pyfuzz_can

### Dependencies:
- Python 2.7.X
  https://www.python.org/downloads/
  
- Python-CAN 
  https://bitbucket.org/hardbyte/python-can
  
- (Optional to build Python-CAN from source) Mercurial
  https://www.mercurial-scm.org/wiki/Download
  
### Setup:

**1. Install the Python-CAN dependency.**

   * Using PiP:
     ```
     $> pip install python-can
     ```
     
   * From source: 
   
     Clone Python-CAN to your local machine:
  
     `$> hg clone https://bitbucket.org/hardbyte/python-can`
  
     Install Python-CAN normally with:
     ```
     $> cd python-can
     $> python setup.py install
     ```
     
  **2. Create interface config file for Python-CAN at ~/can.conf:**
  ```
  [default]
  interface = pcan
  channel = PCAN_USBBUS1
  ```
  The interface and channel given are for PEAK PCAN-USB. These will change depending on your CAN interface. Refer to the Python-CAN documentation for your device's configuration : http://python-can.readthedocs.io/en/latest/configuration.html.
  
  **3. Clone pyfuzz_can to your local machine:**

  `$> git clone https://github.com/bhass1/pyfuzz_can.git`
  
  **4. You are ready to fuzz. Try:**
  ```
  $> cd pyfuzz_can
  $> python fuzzer.py
  ```

  For help use:

  `$> python fuzzer.py --help`

### Common Issues
**1. Cannot open a required shared object file. (e.g. `OSError: libpcanbasic.so: cannot open shared object file: No such file or directory`)**

   Don't forget to install device drivers for your CAN interface device on your platform. For this particular issue on Linux (missing libpcanbasic.so), you need to download and install the peak-linux-driver (http://www.peak-system.com/fileadmin/media/linux/index.htm) and PCAN-Basic API (http://www.peak-system.com/produktcd/Develop/PC%20interfaces/Linux/PCAN-Basic_API_for_Linux/PCAN_Basic_Linux-4.2.0.tar.gz).
   
   However, there are many other interface devices supported by Python-CAN: http://python-can.readthedocs.io/en/latest/interfaces.html. Ensure your CAN interface drivers are installed properly.
   
**2. Import can problem. `ModuleNotFoundError: No module named 'can'`**

  Ensure Python-CAN is installed. Try `pip install python-can`
  
**3. Something else?**

  Send me an email: `billhass@umich.edu` or open an issue!
  

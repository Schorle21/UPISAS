# UPISAS
Unified Python interface for self-adaptive system exemplars.


### Prerequisites 
Tested with Python 3.9.12, should work with >=3.7.

### How to run Our Strategy - Switch

Download the images from docker hub manually
  - Download schorle21/switch-4-frontend
  - https://hub.docker.com/r/schorle21/switch-4-frontend
    
  - Download schorle21/switch-4-backend
  - https://hub.docker.com/r/schorle21/switch-4-backend
    
  - If these images are not downloaded manually UPISAS will fail to download them on its own and will crash !
    
Alternatively you can attempt to pull these images using the following docker command, if this fails download them manually:
    - docker pull schorle21/switch-4-backend
    - docker pull schorle21/switch-4-frontend


Once the images have been downloaded you can continue by going into the UPISAS directory
  - In the UPISAS directory run: ./run.sh
  - If run.sh does not work be sure to run sudo chmod +x run.sh
  - Then run ./run.sh
```



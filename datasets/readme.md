# Obtaining Datasets

* Get hold of a dataset converted to NILMTK format or convert your dataset and place it into this directory.

    * Check if your dataset has supported converter [link](https://github.com/nilmtk/nilmtk/blob/master/docs/source/nilmtk.dataset_converters.rst), if not you can write your own dataset converter by following instructions [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/development_guide/writing_a_dataset_converter.md).

    * Convert your dataset by following notebook [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/user_guide/data.ipynb).

* Works with all datasets supported by NILMTK. Tested on:

    * REFIT
    * UKDALE
    * iAWE
    * REDD
    * ECO  

* You can try running this command to download few converted datasets:

   * Change directory to datasets:
   ```bash
      cd datasets
   ```
   * Download source folder:
   ```bash
      gdown --folder --id 1oHzjdKdm0jliuYfHu0IOzNtqOPU6a41f
   ```
   * Move elements from source folder to datasets folder:
   ```bash
      cd source && mv * ../ && cd ..
   ```
 

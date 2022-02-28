# Time Series to Image Converter for Energy Data

Notebook uses [pyts](https://pyts.readthedocs.io) to transform time series image data to:

* Gramian angular summation fields
* Gramian angular difference fields
* recurrence plots 

For easier data handling [NILMTK](https://github.com/nilmtk/nilmtk) was used. 

The converter offers a variety of parameters to set such as:

* input time series window size
* output image size
* resample period
* stacking n images as a video
* adding brightness to the GAF images
* choosing between Gramian angular fields or recurrence plots
* using only a selected building
* manually selecting the appliances
* saving the source time series

environment 

Works with all datasets supported by NILMTK. Tested on:

* REFIT
* UKDALE
* iAWE
* REDD
* ECO   

# Example Output 

Examples below are Gramian angle summation filed images transformed using UKDALE dataset over a 60-minute window.

Computer monitor and washing machine examples:
<p float="center">
    <img src="/imgs/iawe-computer-gasf.png" width="250" />
    <img src="/imgs/iawe-washm-gaf.png" width="250" />
</p>

Examples for selected appliances:
<p float="center">
    <img src="/imgs/gaf_matrix.png" width="600" />
</p>

# Install Instructions  
  
❗️ If possible, install on a Linux machine.

1.  Install [Anaconda](https://anaconda.org) by following instructions [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html).

2.  Clone this repository and change directory to conda:
  
    ```bash
        git clone https://github.com/jenkoj/ts2img && cd ts2img/conda
    ```

3.  Create a new environment by running:

    ```bash
        conda env create --name ts2img --file=ts2img.yml 
    ```
4.  Activate the newly created environment:

    ```bash
        conda activate ts2img
    ```

5.  Get hold of a dataset converted to NILMTK format or convert your dataset.

    * Check if your dataset has supported converter [link](https://github.com/nilmtk/nilmtk/blob/master/docs/source/nilmtk.dataset_converters.rst), if not you can write your own dataset converter by following instructions [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/development_guide/writing_a_dataset_converter.md).

    * Convert your dataset by following notebook [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/user_guide/data.ipynb).

6.  Place converted dataset in datasets directory.

7.  Set parameters.

8.  Finally, run:
    ```bash
        ipython -c "%run converter.ipynb"
    ```
When adjusting the parameters start with iAWE. Since it is small, it is easy to handle. 


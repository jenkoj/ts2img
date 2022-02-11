# Timeseries to image converter 

Notebook uses [pyts](pyts.readthedocs.io) to trasform timeseries image data to either:

* Gramian angluar summation fields
* Gramian angluar difference fileds
* Reccurence plots 

For easier data handling [NILMTK](https://github.com/nilmtk/nilmtk) was used. 

The converter offers a variety of parameters to set such as:

* input timeseries window size,
* output image size,
* stacking n images (video),
* adding brightness to GAF images,
* trasfomation type,
* using only one building,
* manualty selecting appliances,
* saving source time series.

# Example output 

Examples bellow are gramian angle summation filed images trasfomered using UK-DALE dataset and 60-minute window.

Computer monitor and washing machine examples
<p float="center">
    <img src="/imgs/iawe-computer-gasf.png" width="250" />
    <img src="/imgs/iawe-washm-gaf.png" width="250" />
</p>

Trasfomation examples for selected appliances
<p float="center">
    <img src="/imgs/gaf_matrix.png" width="700" />
</p>

# Install instructions  

* Install [NILMTK](https://github.com/nilmtk/nilmtk) by following instructions [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/user_guide/install_user.md) .

    *  ❗️ You may need to downgrade Matplotlib to an older version due to dependency-related issues.

* Install [pyts](pyts.readthedocs.io) by running:

    ```bash
        pip install pyts
    ```

*  Get hold of a converted dataset or convert your dataset.

    * Check if your dataset has supported converter [link](https://github.com/nilmtk/nilmtk/blob/master/docs/source/nilmtk.dataset_converters.rst), if not you can write your own dataset converter by following instructions [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/development_guide/writing_a_dataset_converter.md).

    * Convert your dataset by following notebook [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/user_guide/data.ipynb).

* Place converted dataset in same directory as notebook.

* Set parameters and run the script.
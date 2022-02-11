# Timeseries to image generator

# Example output 

Gramian angle summation field output for a computer monitor.
<p float="center">
    <img src="/imgs/iawe-computer-gasf.png" width="250" />
</p>

Gramian angle summation filed timeseries output of an washing machine. 
<p float="center">
    <img src="/imgs/iawe-washm-gaf.png" width="250" />
</p>

Trasfomation examples for many appliances 
<p float="center">
    <img src="/imgs/gaf_matrix.png" width="500" />

</p>

# Usage 

* 1. Install [NILMTK](https://github.com/nilmtk/nilmtk) by following instructions [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/user_guide/install_user.md)

* * ❗️ you may need to downgrade matplotlib dependency to an older version due to depenedcy related issues 

* 2. Install [pyts](pyts.readthedocs.io) by running

```bash
	pip install pyts
```

* 3. Get hold of conveted dataset or convert your dataset

** 3.1 Check if your dataset has supported converter [link](https://github.com/nilmtk/nilmtk/blob/master/docs/source/nilmtk.dataset_converters.rst), if not you can write your own dataset converter by following instructions [here](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/development_guide/writing_a_dataset_converter.md).

** 3.2 Convert your dataset by following [notebook](https://github.com/nilmtk/nilmtk/blob/master/docs/manual/user_guide/data.ipynb).

* 4. Place dataset in same directory as notebook 

* 5. Set parameters and run the script 
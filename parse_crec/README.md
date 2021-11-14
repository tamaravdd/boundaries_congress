# Code for newer CREC congressional record data

This contains Jupyter Notebooks for downloading, parsing, and comparing newer CREC congressional record data.

It requires the following libraries: `edlib`, `pandas`, `tables`, `urllib3`, `pyOpenSSL`, and the `congressional-record` package from https://github.com/artemyk/congressional-record .

These requirements can be installed from the command line by running 
  ``pip3 install -r requirements.txt``
in this directory.

Contents:
* `DownloadCREC.ipynb` : download JSON files from the CREC website
* `ParseCREC.ipynb` : parse JSON files from the CREC website, create a pandas dataframe
* `CompareCREC.ipynb` : compare new parsed speeches to older congressional data
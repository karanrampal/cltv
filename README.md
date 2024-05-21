## Calculating the Probability of Future Customer Engagement

In non-subscription retail models, customers come and go with no long-term commitments, making it very difficult to determine whether a customer will return in the future. In addition, customers frequently settle into a pattern of regular spend with retailers with whom they maintain a long-term relationship.  But occasionally, customers will spend at higher rates before returning back to their previous norm.  Both of these patterns make effective projections of customer spending very challenging for most retail organizations.

The *Buy 'til You Die* (BTYD) models popularized by Peter Fader and others leverage a few basic customer metrics, *i.e.* the recency of a customer's last engagement, the frequency of repeat transactions over a customer's lifetime, the average monetary spend associated with those transactions, and the length (term) of a customer's time engaged with a retailer to derive probabilistic estimations of both a customer's future spend and that customer's likelihood to remain engaged.  Using these values, we can project likely future spend, a value we frequently refer to as the customer's lifetime value (CLV).

The math behind this approach is fairly complex. The purpose of this repo is to examine how these models may be applied to customer transaction history to estimate CLV.

In this repo, we are going to create two models that are used to estimate lifetime value.  The first of these will be used to estimate the probability of customer retention through a certain point in time.  The second will be used to calculate the estimated monetary value through that same point in time.  Together, these estimates can be combined to calculate a customer's value through and extended period of time.

## Install

To install the python package for development the following commands can be run from the command line with `pymodels/cltv` as the root,

  - Install `make` (if not already installed)
    ```
    # If on linux
    sudo apt-get install buil-essential

    # If on windows
    choco install make
    ```
  - Install package

    ```
    # If using conda for package management, this will create virtual env as well
    make install
    conda activate cltv-env

    # If using pip for package management
    # First create virtual env if not already done so, else skip next line
    python -m venv /path/to/new/virtual/environment
    # Activate the virtual env
    /path/to/new/virtual/environment/Scripts/activate.bat
    # install package, this will use pip
    make install_ci
    ```

## Run

The models can be run via `main.ipynb` notebook or by the `main.py` script,

  - Run script (default arguments should be fine, but you can change as required)
    ```
    ./src/main.py
    ```

  - Run notebook
    ```
    # Create a kernel for the notebook corresponding to the virtual env
    python -m ipykernel install --user --name=cltv-env
    ```
    Open the main notebook, select the kernel and run the cells as required.
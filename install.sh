#!/bin/bash

# Install Homebrew if not already installed
if ! command -v brew &> /dev/null
then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Install asdf if not already installed
if ! command -v asdf &> /dev/null
then
    echo "asdf not found. Installing asdf..."
    git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0
    echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bash_profile
    echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bash_profile
    source ~/.bash_profile
else
    echo "asdf is already installed."
fi

# Add Python plugin to asdf
if ! asdf plugin-list | grep -q 'python'; then
    asdf plugin-add python
fi

# Install Tcl/Tk via Homebrew
brew install tcl-tk

export LDFLAGS="-L/usr/local/opt/tcl-tk/lib"
export CPPFLAGS="-I/usr/local/opt/tcl-tk/include"
export PKG_CONFIG_PATH="/usr/local/opt/tcl-tk/lib/pkgconfig"
asdf uninstall python 3.11.6
asdf install python 3.11.6

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Installation complete. To activate the virtual environment, run 'source venv/bin/activate'."
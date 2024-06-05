# if you want to wipe your old wsl instance
# wsl -l
# wsl --unregister <distribution>

wsl
cd ~

# make changes to .bashrc that I like
# comment out hist commands so they don't ruin our eternal history on startup
sed -i -E "s/^\s*HIST/# HIST/" ~/.bashrc
{ cat <<EOF
export PATH="\$PATH:/usr/local/cuda/bin/"
export ECM_PATH=~/ecm
export PATH="\$PATH:/mnt/c/GitProjects/t-level/dist"
export PYTHONPATH="\$PYTHONPATH:/mnt/c/GitProjects/oeis"
alias t-level="python3 /mnt/c/GitProjects/t-level/t_level.py"
alias yafu="~/yafu/yafu"
shopt -s histappend
HISTCONTROL=ignoredups:erasedups:ignorespace
export HISTSIZE=
export HISTFILESIZE=
export HISTFILE=~/.bash_eternal_history
PROMPT_COMMAND="history -a; \$PROMPT_COMMAND"
EOF
} >> ~/.bashrc
source ~/.bashrc

sudo apt-get update
sudo apt-get install build-essential libtool autoconf libprimesieve-dev libgsl-dev
# for ggnfs
sudo apt-get install g++ m4 zlib1g-dev make p7zip
# for downloading NFS rels
sudo apt-get install aria2
# for lucas.sh
sudo apt-get install moreutils python-is-python3

# install cuda
# from https://docs.nvidia.com/cuda/wsl-user-guide/index.html
sudo apt-key del 7fa2af80
# from https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_network
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
# this maybe necessary on ubuntu 24 https://askubuntu.com/a/1493087
sudo apt-get update
sudo apt-get -y install cuda
rm -rf cuda-keyring_1.1-1_all.deb
# necessary for msieve
echo 'export PATH="$PATH:/usr/local/cuda/bin/"' >> ~/.bashrc
source ~/.bashrc

#gmp version should be fine without reinstalling, otherwise try reinstalling different version from
#https://gmplib.org/#DOWNLOAD
# alternatively, this seems fine
sudo apt-get install libgmp3-dev

# get CGBN (for GPU ECM)
git clone https://github.com/NVlabs/CGBN.git

# get ecm source
git clone https://gitlab.inria.fr/zimmerma/ecm.git
cd ecm
# comment out check that isn't needed in WSL2
sed -i -E "s/AC_CHECK_LIB\(\[cuda\], \[cuInit\]/#AC_CHECK_LIB\(\[cuda\], \[cuInit\]/" acinclude.m4
# force version to be non-dev, so we get the good kernels
sed -i "1 s/-dev//" configure.ac
autoreconf -i
./configure --enable-gpu --with-cuda=/usr/local/cuda --with-cgbn-include=$HOME/CGBN/include/cgbn
make
make check
sudo make install
cd ~
echo 'export ECM_PATH=~/ecm' >> ~/.bashrc
source ~/.bashrc

# install cado-nfs
sudo apt-get install g++ m4 zlib1g-dev make cmake python3 git
git clone https://gitlab.inria.fr/cado-nfs/cado-nfs.git
cd cado-nfs
make

# gpu msieve
git clone https://github.com/gchilders/msieve_nfsathome.git -b msieve-lacuda-nfsathome
cd msieve_nfsathome
make clean
# the below sed line makes this change: https://www.mersenneforum.org/showpost.php?p=625660&postcount=122
# which fixes `identifier "CUB_IS_DEVICE_CODE" is undefined`
sed -i -E 's/INC = -I\"\$\(CUDA_ROOT\)\/include\" -I\./INC = -I\. -I\"\$\(CUDA_ROOT\)\/include\"/' cub/Makefile
# if below breaks, set GENCODE (e.g. CUDA=89) to your GPU's gencode https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/
GENCODE=$(nvidia-smi --query-gpu=compute_cap --format=csv | awk -F"." 'END{print $1$2}')
make all VBITS=256 CUDA=$GENCODE #ECM=1 NO_ZLIB=1 #maybe need these for yafu?
# VBITS can be changed in certain situations for more optimal performance, though I forget exactly when.
cd ~

# now for yafu
# https://www.mersenneforum.org/showpost.php?p=622435&postcount=7


# cpu msieve
cd ~
sudo apt-get install subversion
svn co https://svn.code.sf.net/p/msieve/code/trunk msieve
cd msieve
make all


# gmp for yafu (not necessary as long as the apt-get version works)
#GMPVERSION="6.2.1"
#wget https://gmplib.org/download/gmp/gmp-$GMPVERSION.tar.lz
#tar --lzip -xf gmp-$GMPVERSION.tar.lz
#rm gmp-$GMPVERSION.tar.lz
#cd gmp-$GMPVERSION
#autoreconf -i
#./configure --prefix=$HOME/gmp-install/$GMPVERSION/
#make
#sudo make install

# cpu ecm (for yafu)
git clone https://gitlab.inria.fr/zimmerma/ecm.git cpu_ecm
cd cpu_ecm
sed -i "1 s/-dev//" configure.ac
autoreconf -i
./configure --prefix=$HOME/ecm-install/7.0.6/
make
sudo make install
cd ~

# ytools (yafu)
git clone https://github.com/bbuhrow/ytools.git
cd  ytools
make COMPILER=gcc USE_BMI2=1 USE_AVX2=1
cd ~

# ysieve (yafu)
git clone https://github.com/bbuhrow/ysieve.git
cd ysieve
make COMPILER=gcc USE_BMI2=1 USE_AVX2=1
cd ~

# yafu
git clone https://github.com/bbuhrow/yafu.git
# known working commit
git checkout 93a23e5
cd yafu
make COMPILER=gcc NFS=1 USE_AVX2=1 USE_BMI2=1
cd ~



# pari/gp
sudo apt-get install -y libreadline6-dev


PARIVERSION="2.15.5"
wget https://pari.math.u-bordeaux.fr/pub/pari/unix/pari-$PARIVERSION.tar.gz
tar -xzf pari-$PARIVERSION.tar.gz
rm pari-$PARIVERSION.tar.gz
cd pari-$PARIVERSION
./Configure --with-gmp --with-readline
sudo make install
cp misc/gprc.dft ~/.gprc
sed -i -E 's/\\\\   #ifnot EMACS colors = \"darkbg\"/   #ifnot EMACS colors = \"darkbg\"/' ~/.gprc
cd ~

# if you want to wipe your old wsl instance
# wsl -l
# wsl --unregister <distribution>

wsl
cd ~
sudo apt-get update
sudo apt-get install build-essential libtool autoconf libprimesieve-dev libprimesieve libgsl-dev

# install cuda
# from https://docs.nvidia.com/cuda/wsl-user-guide/index.html
sudo apt-key del 7fa2af80
# from https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_network
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
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

# get CGBN
git clone https://github.com/NVlabs/CGBN.git

# get ecm source
git clone https://gitlab.inria.fr/zimmerma/ecm.git
cd ecm
# comment out check that isn't needed in WSL2
sed -i -E "s/AC_CHECK_LIB\(\[cuda\], \[cuInit\]/#AC_CHECK_LIB\(\[cuda\], \[cuInit\]/" acinclude.m4
# force version to be non-dev, so we get the good kernels
sed -i "1 s/-dev//" configure.ac
autoreconf -i
./configure --enable-gpu --with-cuda=/usr/local/cuda --with-cgbn-include=~/CGBN/include/cgbn
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

# now for yafu
# https://www.mersenneforum.org/showpost.php?p=622435&postcount=7
# install msieve
# cpu version
#sudo apt-get install subversion
#svn co https://svn.code.sf.net/p/msieve/code/trunk msieve
#cd msieve
#make all

# gpu msieve
git clone https://github.com/gchilders/msieve_nfsathome.git -b msieve-lacuda-nfsathome
cd msieve_nfsathome
make clean
# below sed makes this change: https://www.mersenneforum.org/showpost.php?p=625660&postcount=122
# which fixes `identifier "CUB_IS_DEVICE_CODE" is undefined`
sed -i -E 's/INC = -I\"\$\(CUDA_ROOT\)\/include\" -I\./INC = -I\. -I\"\$\(CUDA_ROOT\)\/include\"/' cub/Makefile
make all VBITS=256 CUDA=89 #ECM=1 NO_ZLIB=1 #maybe need these for yafu?
# maybe more optimal to change these for your gpu
cd ~

# cpu ecm (for yafu)
git clone https://gitlab.inria.fr/zimmerma/ecm.git
cd ecm

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
cd yafu
make NFS=1 USE_AVX2=1 USE_BMI2=1

cd ~

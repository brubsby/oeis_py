sudo apt-get install g++ make libgmp3-dev zlib1g-dev autoconf libtool

# cpu msieve
cd ~
sudo apt-get install subversion
svn co https://svn.code.sf.net/p/msieve/code/trunk msieve
cd msieve
make all NO_ZLIB=1 VBITS=128

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
make
cd ~

# ysieve (yafu)
git clone https://github.com/bbuhrow/ysieve.git
cd ysieve
make COMPILER=gcc SKYLAKEX=1
cd ~

# yafu
git clone https://github.com/bbuhrow/yafu.git
cd yafu
make COMPILER=gcc NFS=1 SKYLAKEX=1
cd ~
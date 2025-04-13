
先创建python环境

conda create -n yubaoCtrader python==3.10

下载后解压，命令行进入setup.py所在目录

pip install -r requirements.txt

pip install .

然后安装TA-Lib

window系统的话执行

pip install .\TA_Lib-0.4.24-cp310-cp310-win_amd64.whl

Linux的话执行

wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz

tar -xzvf ta-lib-0.4.0-src.tar.gz

cd ta-lib/

./configure --prefix=/usr

make

sudo make install

pip install TA-Lib

也可以使用Anaconda来安装TA-Lib：

conda install -c conda-forge ta-lib

如果想用jupyter notebook：

安装jupyter notebook

pip install ipython

pip install jupyter

把安装产生的临时文件build和yubaotrader.egg-info两个临时文件删掉

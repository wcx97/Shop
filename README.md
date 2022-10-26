# Shop
部署
sudo apt install -y wget git tmux
# 下载minidocnda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# 安装miniconda
bash ./Miniconda3-latest-Linux-x86_64.sh

# 按下 enter
# 翻页到最下面
# 按下 yes
# 回车默认安装就可以

# 初始化conda
./miniconda3/bin/conda init
#重启终端

# 创建conda环境
conda create -n discord

# 开启一个tmux
tmux new -s discord
git clone https://github.com/yololccg/dsbot
cd ./dsbot

# 安装依赖
pip install -r ./requirements.txt

# 修改环境变量
cp example.env .env
vim .env
# vim 之后按 i 进入编辑，按 esc，:x或者:wq修改
# 填入上面的设置
以后的运行

# 进入终端
tmux a -t discord
python main.py

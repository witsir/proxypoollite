# proxypoollite
使用 python 标准库的开发的代理池模块，不依赖任何第三方库。  
新手友好，欢迎与作为新手的我相互交流学习，本包在 3.11.1 环境下编写，应该在一些地方使用了 python3.8 的新特性。  
使用了 协程，进程间通信，锁，单例模式，带参数装饰器，命令行参数解析 等python常用技术。  
## 如何工作
proxypoollite 由 getter，tester，server 三个模块组成，getter 负责获取代理，tester 负责测试代理，server 负责提供代理服务。  
getter，tester，server 可以独立运行，  
getter，tester，server 可以通过三个进程同时运行，可以通过配置 pk_config.ini 文件来配置禁用其中的一个和多个。  
getter 通过 init_urls.py 中的字典一个键值项 url: (处理器函数, pattern获取next url) 配置每个代理源网站的代理获取  
如果需要新增代理源网站，只需要在 init_urls.py 中新增一个键值项即可。  
使用 json 本地存储数据，程序中断自动保存数据，程序启动自动读取数据恢复程序上次运行  
目前仅检测 https 和 匿名代理，有效性检测使用的是 weibo.com  
程序的工作方式是，首先建立一个分值字典，获取的代理分值首先设置个默认值，测试成功则将代理放到 MAX 分值列表，测试失败则将代理分值减 1，
当代理分值为 0 时，将代理从代理池中删除。
## 获取模块
```bash
# 如果你的电脑或服务器配置了 ssh
git clone --depth=1 git@github.com:witsir/proxypoollite.git
# 如果你的电脑或服务器没有配置 ssh，则使用HTTPS
git clone --depth=1 https://github.com/witsir/proxypoollite.git
```
## 配置模块环境变量
pk_config.ini 文件是模块的配置文件，可以配置模块的运行环境，如开发模式，日志，模块的开关等  
命令行同时提供了一个环境变量配置 -dev 指明环境变量为开发模式（更详细的日志输出）  
环境变量优先级为 命令行 > 配置文件 > proxypoollite/settings.py  

## 数据文件
程序将自动在包根目录的上级目录创建 data/proxy.json 用于储存代理数据，每次程序启动将先读取此数据  

## 安装模块
#### 第一种 快速使用
进入 proxypoollite 目录
```bash
# 若使用开发模式，增加选项 -dev
# 单独运行 getter - 代理获取模块，tester - 代理测试模块，server - 代理服务模块
python -m proxypoollite -p server
python -m proxypoollite -p getter
python -m proxypoollite -p tester
# 多进程运行
python -m proxypoollite
```
#### 第二种 以可编辑模式安装到开发环境，推荐
进入 pyproject.toml 所在目录
```bash
# 若使用开发模式，增加选项 -dev
# 如果你想新建虚拟环境运行，不要忘记以下两步
python -m venv venv
source venv/bin/activate
# 如果你想在你已有的项目虚拟环境运行，则推荐以 editable 形式安装包，以便你自己调试
pip install -e .
# 在这种情况下，第一种模式照常工作
# 单独运行 getter - 代理获取模块，tester - 代理测试模块，server - 代理服务模块
proxypoollite -p getter
proxypoollite -p tester
proxypoollite -p server
# 多进程运行
proxypoollite
```
#### 第三种 安装包
pip install [包地址](https://github.com/witsir/proxypoollite/releases/download/0.1.0/proxypoollite-0.1.0-py3-none-any.whl)  
和第二步运行方式相同  

## 使用
如果你部署在本地  
获取单个代理 text 文本 ip:port  
http://127.0.0.1:5555/random  
获取有效代理个数  
http://127.0.0.1:5555/count  
如果你部署在服务器，将 127.0.0.1 换成你的服务器 ip  

## 待改进
- 数据去重
- 增加匿名检测网址
- 增加不同网址的有效性判断
- 环境变量和数据文件配置优化

## 例外
同时提供一个使用 redis 的版本，见 [proxypoolminimum](https://github.com/witsir/proxy_pool_minimum)  


### 使用指南：

- 本地启动：./app.py 
- web访问：127.0.0.1:8000

- 容器启动：docker build -t label:1.0 .
- web访问：IP:8000

- 环境：python3.X
- 依赖：requirements.txt
- 安装依赖：pip install -r requirements.txt
- 框架：Flask

### 特点
- 提供api的swagger文件放至指定目录，在页面上点击自动生成，会自动生成api测试信息
- 未提供参数时，程序会自动填充指定的异常参数进行测试
- 可以进行并发测试
- 根据提供的参数个数，做阶乘运算
- 鉴权统一处理

##### 说明：
- API自动化测试基本功能均无问题
- WeChat: liuhuocjx 有问题可以联系，备注自动化测试
- 后续会提供Django版本，引入数据库，功能会更完善，代码也会更健壮

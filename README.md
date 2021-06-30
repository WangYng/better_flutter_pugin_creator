# better_flutter_pugin_creator

### 功能: 
- [x] 通过模板快速创建flutter插件
- [x] 自动生成Dart代码
- [x] 自动生成Java代码
- [x] 自动生成Objective-C代码

### 用法: 
 1. 创建 env.py, 填入必须的参数
```python3
import os.path

# 插件名称
plugin_name = 'better_plugin'

# 插件作者
plugin_author = '汪洋'

# 插件描述
plugin_description = 'A better plugin.'

# 插件标识
plugin_org = 'io.github.wangyng'

# 插件包名
plugin_package = plugin_org + '.' + plugin_name

# 根地址
root_dir = '/Users/wangyang/Desktop'

# 项目地址
project_dir = os.path.join(root_dir, plugin_name)

# flutter命令地址
flutter = ''
```

 2. 修改 template.py, 替换成需要生成的dart函数
```python3
dart_template = \
'''
Stream resultStream;

Future<void> test1();

Future<String> test2(String p1);

Future<int> test3(String p1, int p2);

Future<bool> test4(String p1, int p2, bool p3);

Future<double> test5(String p1, int p2, bool p3, double p4);
'''

```

 3. 使用pip添加必须的第三方库依赖
```terminal
pip3 install GitPython gitdb setuptools smmap
```
    
 4. 运行脚本, 几秒后生成新的Flutter插件
```terminal
python3 main.py
```
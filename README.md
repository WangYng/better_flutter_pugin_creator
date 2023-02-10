# better_flutter_plugin_creator 
创建 flutter plugin 时, 同时创建 flutter plugin 的Flutter端函数, Android端函数 与 iOS端函数

### 功能: 
- [x] 自动生成`template.py`中定义的Flutter端`Dart函数`
- [x] 自动生成`Dart函数`对应的Android端`Java函数`
- [x] 自动生成`Dart函数`对应的iOS端`Objective-C函数`

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
flutter = '/Users/wangyang/library/flutter2/bin/flutter'

# 覆盖 plugin.dart Plugin.java Plugin.h.m 的代码
cover_plugin_file_code = True
```

 2. 修改 template.py, 替换成需要生成的dart函数
```python3
dart_template = \
'''
Stream test1ResultStream;

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

5. 填入`Android端`和`iOS端`模板函数中的需要实现的代码
- 需要填入代码的位置已经加入了以下注释
```python
// TODO
```

6. 更新模板函数
- 修改`template.py`文件
- 修改`env.py`文件，设置是否覆盖 plugin 文件
- 重新执行本脚本，会自动覆盖 api 文件，并根据设置自动覆盖 plugin 文件


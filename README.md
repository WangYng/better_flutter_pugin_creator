# better_flutter_pugin_creator

### 功能: 
- [x] 通过模板快速创建flutter插件
- [x] 自动生成Dart代码
- [x] 自动生成Java代码
- [x] 自动生成Objective-C代码

### 用法: 
 1. 创建 env.py, 填入必须的参数
```python3
# 插件名称
plugin_name = ''

# 插件作者
plugin_author = ''

# 插件描述
plugin_description = ''

# 插件包名
plugin_package = ''

# 项目本地地址
project_dir = ''

# 项目github地址
github_project = ''

# flutter命令地址
flutter = ''
```

 2. 修改 template.py, 替换成需要生成的dart函数

 3. 使用pip3添加必须的第三方库依赖
    
 4. 运行脚本, 几秒后生成新的Flutter插件
```python3
python3 main.py
```
import os
import time
from typing import Text

import git

from template import dart_template
from env import project_dir, flutter, plugin_name, plugin_author, plugin_description, github_project, plugin_package

# 下划线转驼峰
def down_line_to_hump(text):
    arr = filter(None, text.lower().split('_'))
    res = ''
    j = 0
    for i in arr:
        if j == 0:
            res = i[0].upper() + i[1:]
        else:
            res = res + i[0].upper() + i[1:]
        j += 1
    return res


# 检查flutter环境
def check_flutter2():
    global is_flutter2
    output = os.popen(flutter + ' --version')
    version = output.readline().split(' • ')[0].split(' ')[1]
    if version.startswith('2'):
        is_flutter2 = True
    else:
        is_flutter2 = False


# 解析原始的dart函数
def parse_field_and_func():
    # 解析的字段
    global fields
    fields = []

    # 解析的函数
    global funcs
    funcs = []

    # 开始解析
    for dart_field_func in dart_template.split('\n'):
        dart_field_func = dart_field_func.strip()
        if dart_field_func != '':
            if dart_field_func.startswith('Future<') and dart_field_func.endswith(');'):
                # 解析函数名
                return_type = dart_field_func.split(' ')[0][7:-1]
                dart_field_func = dart_field_func[dart_field_func.index(' ')+1: -1]
                func_name = dart_field_func[:dart_field_func.index('(')]
                func_params = dart_field_func[dart_field_func.index('(')+1: -1].strip()

                # 进一步解析参数
                all_params = []
                option_params = []
                if func_params != '' and func_params.endswith('}'):
                    params = func_params[func_params.index('{')+1: -1]
                    for param in params.split(','):
                        param_list = param.split()
                        if len(param_list) == 2:
                            option_params.append((param_list[0], param_list[1]))
                        elif len(param_list) == 3:
                            option_params.append((param_list[1], param_list[2]))
                    func_params = func_params[:func_params.index('{')].strip()
                    if func_params.endswith(','):
                        func_params = func_params[:-1]
                if func_params != '':
                    for param in func_params.split(','):
                        param_list = param.split()
                        if len(param_list) == 2:
                            all_params.append((param_list[0], param_list[1]))
                all_params.extend(option_params)
                funcs.append((return_type, func_name, all_params))

            elif dart_field_func.startswith('Stream') and dart_field_func.endswith(';'):
                # Stream变量
                stream = dart_field_func.split(' ')[1][:-1]
                fields.append(stream)


# dart类型 转 java类型
def dart_type_to_java_type(text: Text):
    if text == 'bool':
        return 'boolean'
    else:
        return text


# dart类型 转 oc类型
def dart_type_to_oc_type(text: Text):
    if text == 'bool':
        return 'BOOL'
    elif text == 'int':
        return 'NSInteger'
    elif text == 'String':
        return 'NSString *'
    else:
        return text

# 创建文本文件
def create_file(path, text):
    if not os.path.exists(path[:path.rindex('/')]):
        os.makedirs(path[:path.rindex('/')])
    if not os.path.exists(path):
        file = open(path, 'w')
        file.write(text)
        file.close()


def create_git_ignore():
    path = project_dir + "/.gitignore"
    text = '''.DS_Store
.dart_tool/

.packages
.pub/

build/
'''

    create_file(path, text)


def create_mate_data():
    git_head = git.Repo(flutter + '/../..').head
    hexsha = git_head.commit.hexsha
    ref = git_head.ref

    path = project_dir + "/.matedata"
    text = '''# This file tracks properties of this Flutter project.
# Used by Flutter tool to assess capabilities and perform upgrades etc.
#
# This file should be version controlled and should not be manually edited.

version:
  revision: %s
  channel: %s

project_type: plugin
''' % (hexsha, ref)

    create_file(path, text)


def create_change_log():
    path = project_dir + "/CHANGELOG.md"
    text = '''## 0.0.1
initial release.
'''

    create_file(path, text)


def create_license():
    localtime = time.localtime(time.time())
    year = localtime.tm_year
    path = project_dir + "/LICENSE"
    text = '''BSD 3-Clause License

Copyright (c) %s, %s
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
''' % (year, plugin_author)

    create_file(path, text)


def create_read_me():
    path = project_dir + "/README.md"
    text = '''# %s

%s

## Install Started

1. Add this to your **pubspec.yaml** file:

```yaml
dependencies:
  %s: ^0.0.1
```

2. Install it

```bash
$ flutter packages get
```

## Normal usage

```dart
// TODO
```

## Feature
- [x] TODO.
''' % (plugin_name, plugin_description, plugin_name)

    create_file(path, text)


def create_project_iml():
    path = project_dir + "/%s.iml" % plugin_name
    text = '''<?xml version="1.0" encoding="UTF-8"?>
<module type="JAVA_MODULE" version="4">
  <component name="NewModuleRootManager" inherit-compiler-output="true">
    <exclude-output />
    <content url="file://$MODULE_DIR$">
      <sourceFolder url="file://$MODULE_DIR$/lib" isTestSource="false" />
      <excludeFolder url="file://$MODULE_DIR$/.dart_tool" />
      <excludeFolder url="file://$MODULE_DIR$/.idea" />
      <excludeFolder url="file://$MODULE_DIR$/.pub" />
      <excludeFolder url="file://$MODULE_DIR$/build" />
      <excludeFolder url="file://$MODULE_DIR$/example/.dart_tool" />
      <excludeFolder url="file://$MODULE_DIR$/example/.pub" />
      <excludeFolder url="file://$MODULE_DIR$/example/build" />
    </content>
    <orderEntry type="sourceFolder" forTests="false" />
    <orderEntry type="library" name="Dart SDK" level="project" />
    <orderEntry type="library" name="Flutter Plugins" level="project" />
  </component>
</module>
'''

    create_file(path, text)


def create_pubspec_yml():
    path = project_dir + "/pubspec.yaml"
    text = '''name: %s
description: %s
version: 0.0.1
homepage: %s
repository: %s

environment:
  sdk: "%s"
  flutter: "%s"

dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_test:
    sdk: flutter

# The following section is specific to Flutter.
flutter:
  plugin:
    platforms:
      android:
        package: %s
        pluginClass: %sPlugin
      ios:
        pluginClass: %sPlugin
'''

    if not os.path.exists(path):

        github_homepage = github_project[:github_project.rindex('/')]

        if is_flutter2:
            sdk_env = '>=2.12.0 <3.0.0'
            flutter_env = '>=2.0.0'
        else:
            sdk_env = '>=2.7.0 <3.0.0'
            flutter_env = '>=1.20.0'

        file = open(path, 'w')
        file.write(text % (plugin_name,
                           plugin_description,
                           github_homepage,
                           github_project,
                           sdk_env,
                           flutter_env,
                           plugin_package,
                           down_line_to_hump(plugin_name),
                           down_line_to_hump(plugin_name)))
        file.close()


def create_api_dart_field(field):
    return '''
  static Stream %s = EventChannel("%s/%s").receiveBroadcastStream();
''' % (field, plugin_package, field)


def create_dart_field(field):
    return '''
  static Stream %s = %sApi.%s;
''' % (field, down_line_to_hump(plugin_name), field)


def create_api_dart_func(func):
    func_param = None
    request_param = None
    if len(func[2]) > 0:
        func_param = '{'
        request_param = ''
        for param in func[2]:
            func_param = func_param + \
                         ('required ' if is_flutter2 else '@required ')\
                         + param[0] \
                         + ' ' \
                         + param[1] \
                         + ', '
            request_param = request_param + '    requestMap["%s"] = %s;\n' % (param[1], param[1])
        func_param = func_param[:-2]
        func_param = func_param + '}'

    if func[0].startswith('int'):
        default_result = '''return 0;'''
        func_result = '''return replyMap["result"];'''
    elif func[0].startswith('String'):
        default_result = '''return '';'''
        func_result = '''return replyMap["result"];'''
    elif func[0].startswith('double'):
        default_result = '''return 0;'''
        func_result = '''return replyMap["result"];'''
    elif func[0].startswith('bool'):
        default_result = '''return false;'''
        func_result = '''return replyMap["result"];'''
    else:
        default_result = ''
        func_result = '''// noop'''

    return '''
  static Future<%s> %s(%s) async {
    const channel = BasicMessageChannel<dynamic>('%s.%s', StandardMessageCodec());

    final Map<String, dynamic> requestMap = {};
%s    final reply = await channel.send(requestMap);

    if (!(reply is Map)) {
      _throwChannelException();
    }

    final replyMap = Map<String, dynamic>.from(reply);
    if (replyMap['error'] != null) {
      final error = Map<String, dynamic>.from(replyMap['error']);
      _throwException(error);
      %s
    } else {
      %s
    }
  }
''' % (func[0],
       func[1],
       '' if func_param is None else func_param,
       plugin_package,
       func[1],
       '' if request_param is None else request_param,
       default_result,
       func_result)


def create_dart_func(func):
    func_param = None
    request_param = None
    if len(func[2]) > 0:
        func_param = '{'
        request_param = ''
        for param in func[2]:
            func_param = func_param + \
                         ('required ' if is_flutter2 else '@required ')\
                         + param[0] \
                         + ' ' \
                         + param[1] \
                         + ', '
            request_param = request_param + '%s: %s, ' % (param[1], param[1])
        func_param = func_param[:-2]
        request_param = request_param[:-2]
        func_param = func_param + '}'

    return '''
  static Future<%s> %s(%s) async {
    return %sApi.%s(%s);
  }
''' % (func[0],
       func[1],
       '' if func_param is None else func_param,
       down_line_to_hump(plugin_name),
       func[1],
       '' if request_param is None else request_param)


def create_plugin_dart():
    # 创建目录
    if not os.path.exists(project_dir + '/lib'):
        os.mkdir(project_dir + '/lib')

    api_path = project_dir + '/lib/' + plugin_name + '_api.dart'
    path = project_dir + '/lib/' + plugin_name + '.dart'

    api_text = \
'''
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

class %sApi {
''' % down_line_to_hump(plugin_name)
    text = \
'''
import 'package:flutter/services.dart';
import 'package:%s/%s';

class %s {
''' % (plugin_name, plugin_name + '_api.dart', down_line_to_hump(plugin_name))

    # 生成相应的字段
    for field in fields:
        api_text = api_text + create_api_dart_field(field)
        text = text + create_dart_field(field)

    # 生成相应的函数
    for func in funcs:
        api_text = api_text + create_api_dart_func(func)
        text = text + create_dart_func(func)

    # 结束部分
    api_text = api_text + \
'''
}

_throwChannelException() {
  throw PlatformException(code: 'channel-error', message: 'Unable to establish connection on channel.', details: null);
}

_throwException(Map<String, dynamic> error) {
  throw PlatformException(code: "${error['code']}", message: "${error['message']}", details: "${error['details']}");
}
'''
    text = text + \
'''
}

'''

    create_file(api_path, api_text)
    create_file(path, text)


def create_android_gradle_wrapper():
    path = project_dir + "/android/gradle/wrapper/gradle-wrapper.properties"
    text = \
'''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-5.6.2-all.zip
'''

    create_file(path, text)


def create_android_ignore():
    path = project_dir + "/android/.gitignore"
    text = \
'''*.iml
.gradle
/local.properties
/.idea/workspace.xml
/.idea/libraries
.DS_Store
/build
/captures
'''

    create_file(path, text)


def create_android_build_gradle():
    path = project_dir + "/android/build.gradle"
    text = \
'''group '%s'
version '1.0'

buildscript {
    repositories {
        google()
        jcenter()
        mavenCentral()
    }

    dependencies {
        classpath 'com.android.tools.build:gradle:3.5.0'
    }
}

rootProject.allprojects {
    repositories {
        google()
        jcenter()
        mavenCentral()
    }
}

apply plugin: 'com.android.library'

android {
    compileSdkVersion 29

    defaultConfig {
        minSdkVersion 16
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}
''' % plugin_package

    create_file(path, text)


def create_android_gradle_properties():
    path = project_dir + "/android/gradle.properties"
    text = \
'''org.gradle.jvmargs=-Xmx1536M
android.useAndroidX=true
android.enableJetifier=true
'''

    create_file(path, text)


def create_android_settings_gradle():
    path = project_dir + "/android/settings.gradle"
    text = \
'''rootProject.name = '%s'
''' % plugin_name

    create_file(path, text)


def create_android_manifest():
    path = project_dir + '/android/src/main/AndroidManifest.xml'
    text = \
'''<manifest xmlns:android="http://schemas.android.com/apk/res/android"
  package="%s">
</manifest>
''' % plugin_package

    create_file(path, text)


def create_android_interface_field(field):
    return \
'''
    void set%s(Context context, %sEventSink %s);
''' % (field[0].upper() + field[1:], down_line_to_hump(plugin_name), field)


def create_android_interface_function(func):
    func_result = dart_type_to_java_type(func[0])
    func_param = 'Context context, '
    if len(func[2]) > 0:
        for param in func[2]:
            func_param = func_param + dart_type_to_java_type(param[0]) + ' ' + param[1] + ', '
    func_param = func_param[:-2]
    return \
'''
    %s %s(%s);
''' % (func_result, func[1], func_param)


def create_android_setup_field_block(field):
    return \
'''
        {
            EventChannel eventChannel = new EventChannel(binaryMessenger, "%s/%s");
            %sEventSink eventSink = new %sEventSink();
            if (api != null) {
                eventChannel.setStreamHandler(new EventChannel.StreamHandler() {
                    @Override
                    public void onListen(Object arguments, EventChannel.EventSink events) {
                        eventSink.event = events;
                    }

                    @Override
                    public void onCancel(Object arguments) {
                        eventSink.event = null;
                    }
                });
                api.set%s(context, eventSink);
            } else {
                eventChannel.setStreamHandler(null);
            }
        }
''' % (plugin_package,
       field,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       field[0].upper() + field[1:])


def create_android_setup_function_block(func):
    request_param = ''
    if len(func[2]) > 0:
        request_param = \
'''
                        HashMap<String, Object> params = (HashMap<String, Object>) message;'''
        for param in func[2]:
            request_param = request_param + \
'''
                        %s %s = (%s)params.get("%s");''' % (dart_type_to_java_type(param[0]),
                                                           param[1],
                                                           dart_type_to_java_type(param[0]),
                                                           param[1])
    func_param = 'context, '
    if len(func[2]) > 0:
        for param in func[2]:
            func_param = func_param + param[1] + ', '
    func_param = func_param[:-2]
    return \
'''
        {
            BasicMessageChannel<Object> channel = new BasicMessageChannel<>(binaryMessenger, "%s.%s", new StandardMessageCodec());
            if (api != null) {
                channel.setMessageHandler((message, reply) -> {
                    Map<String, Object> wrapped = new HashMap<>();
                    try {%s
                        %sapi.%s(%s);
                        wrapped.put("result", %s);
                    } catch (Exception exception) {
                        wrapped.put("error", wrapError(exception));
                    }
                    reply.reply(wrapped);
                });
            } else {
                channel.setMessageHandler(null);
            }
        }
''' % (plugin_package,
       func[1],
       request_param,
       '' if func[0] == 'void' else '%s result = ' % dart_type_to_java_type(func[0]),
       func[1],
       func_param,
       'null' if func[0] == 'void' else 'result')


def create_android_plugin_api():
    path = project_dir + '/android/src/main/java/%s/%sApi.java' \
           % \
           (plugin_package.replace('.', '/'), down_line_to_hump(plugin_name))
    text = \
'''package %s;

import android.content.Context;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.flutter.plugin.common.BasicMessageChannel;
import io.flutter.plugin.common.BinaryMessenger;
import io.flutter.plugin.common.EventChannel;
import io.flutter.plugin.common.StandardMessageCodec;

public interface %sApi {
''' % (plugin_package, down_line_to_hump(plugin_name))

    # 创建接口函数
    for field in fields:
        text = text + create_android_interface_field(field)
    for func in funcs:
        text = text + create_android_interface_function(func)

    # 创建setup函数
    text = text + \
'''
    static void setup(BinaryMessenger binaryMessenger, %sApi api, Context context) {
''' % down_line_to_hump(plugin_name)

    for field in fields:
        text = text + create_android_setup_field_block(field)
    for func in funcs:
        text = text + create_android_setup_function_block(func)

    text = text + \
'''
   }
'''

    text = text + \
'''
    static HashMap<String, Object> wrapError(Exception exception) {
        HashMap<String, Object> errorMap = new HashMap<>();
        errorMap.put("message", exception.toString());
        errorMap.put("code", null);
        errorMap.put("details", null);
        return errorMap;
    }
}
'''

    create_file(path, text)


def create_android_plugin_event_sink():
    path = project_dir + '/android/src/main/java/%s/%sEventSink.java' \
           %\
           (plugin_package.replace('.', '/'), down_line_to_hump(plugin_name))
    text = \
'''package %s;

import io.flutter.plugin.common.EventChannel;

public class %sEventSink {
    EventChannel.EventSink event;
}
''' % (plugin_package, down_line_to_hump(plugin_name))

    create_file(path, text)


def create_android_implement_field(field):
    return \
'''
    @Override
    public void set%s(Context context, %sEventSink %s) {
        // TODO
    }
''' % (field[0].upper() + field[1:], down_line_to_hump(plugin_name), field)


def create_android_implement_function(func):
    func_result = dart_type_to_java_type(func[0])
    func_param = 'Context context, '
    if len(func[2]) > 0:
        for param in func[2]:
            func_param = func_param + dart_type_to_java_type(param[0]) + ' ' + param[1] + ', '
    func_param = func_param[:-2]
    func_default_result = ''
    func_default_result = 'return "";' if func[0] == 'String' else func_default_result
    func_default_result = 'return 0;' if func[0] == 'int' else func_default_result
    func_default_result = 'return false;' if func[0] == 'bool' else func_default_result
    func_default_result = 'return 0.0;' if func[0] == 'double' else func_default_result
    return \
'''
    @Override
    public %s %s(%s) {
        // TODO
        %s
    }
''' % (func_result, func[1], func_param, func_default_result)


def create_android_plugin():
    path = project_dir + '/android/src/main/java/%s/%sPlugin.java' \
           % \
           (plugin_package.replace('.', '/'), down_line_to_hump(plugin_name))
    text = \
'''package %s;

import android.content.Context;

import androidx.annotation.NonNull;

import java.util.HashMap;
import java.util.List;

import io.flutter.embedding.engine.plugins.FlutterPlugin;

public class %sPlugin implements FlutterPlugin, %sApi {

    @Override
    public void onAttachedToEngine(@NonNull FlutterPluginBinding binding) {
        %sApi.setup(binding.getBinaryMessenger(), this, binding.getApplicationContext());
    }

    @Override
    public void onDetachedFromEngine(@NonNull FlutterPluginBinding binding) {
        %sApi.setup(binding.getBinaryMessenger(), null, null);
    }
    
''' % (plugin_package,
      down_line_to_hump(plugin_name),
      down_line_to_hump(plugin_name),
      down_line_to_hump(plugin_name),
      down_line_to_hump(plugin_name))

    # 创建接口函数
    for field in fields:
        text = text + create_android_implement_field(field)
    for func in funcs:
        text = text + create_android_implement_function(func)

    text = text + \
'''
   }
'''

    create_file(path, text)


def create_ios_ignore():
    path = project_dir + '/ios/.gitignore'
    text = \
'''.idea/
.vagrant/
.sconsign.dblite
.svn/

.DS_Store
*.swp
profile

DerivedData/
build/
GeneratedPluginRegistrant.h
GeneratedPluginRegistrant.m

.generated/

*.pbxuser
*.mode1v3
*.mode2v3
*.perspectivev3

!default.pbxuser
!default.mode1v3
!default.mode2v3
!default.perspectivev3

xcuserdata

*.moved-aside

*.pyc
*sync/
Icon?
.tags*

/Flutter/Generated.xcconfig
/Flutter/flutter_export_environment.sh
'''

    create_file(path, text)


def create_ios_podspec():
    path = project_dir + '/ios/%s.podspec' % plugin_name
    text = \
'''#
# To learn more about a Podspec see http://guides.cocoapods.org/syntax/podspec.html.
# Run `pod lib lint better_wifi_manager.podspec' to validate before publishing.
#
Pod::Spec.new do |s|
  s.name             = '%s'
  s.version          = '0.0.1'
  s.summary          = '%s'
  s.description      = <<-DESC
%s
                       DESC
  s.homepage         = 'http://example.com'
  s.license          = { :file => '../LICENSE' }
  s.author           = { 'Your Company' => 'email@example.com' }
  s.source           = { :path => '.' }
  s.source_files = 'Classes/**/*'
  s.public_header_files = 'Classes/**/*.h'
  s.dependency 'Flutter'
  s.platform = :ios, '8.0'

  # Flutter.framework does not contain a i386 slice.
  s.pod_target_xcconfig = { 'DEFINES_MODULE' => 'YES', 'EXCLUDED_ARCHS[sdk=iphonesimulator*]' => 'i386' }
end
''' % (plugin_name, plugin_description, plugin_description)

    create_file(path, text)


def create_ios_interface_field(field):
    return \
'''
- (void)set%s:(%sEventSink *)%s;
''' % (field[0].upper() + field[1:], down_line_to_hump(plugin_name), field)


def create_ios_interface_function(func):
    func_result = dart_type_to_oc_type(func[0])
    func_param = ''
    if len(func[2]) > 0:
        for param in func[2]:
            func_param = func_param + ' ' + param[1] + ':(' + dart_type_to_oc_type(param[0]) + ')' + param[1]
        func_param = func_param[1:]
        func_param = 'With' + func_param[0].upper() + func_param[1:]
    return \
'''
- (%s)%s%s;
''' % (func_result, func[1], func_param)


def create_ios_setup_field_block(field):
    return \
'''
    {
        FlutterEventChannel *eventChannel = [FlutterEventChannel eventChannelWithName:@"%s/%s" binaryMessenger:messenger];
        %sEventSink *eventSink = [[%sEventSink alloc] init];
        if (api != nil) {
            [eventChannel setStreamHandler:eventSink];
            [api set%s:eventSink];
        }
    }
''' % (plugin_package,
       field,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       field[0].upper() + field[1:])


def create_ios_setup_function_block(func):
    request_param = ''
    if len(func[2]) > 0:
        request_param = \
'''
                    NSDictionary *params = message;'''
        for param in func[2]:
            if param[0] == 'String':
                request_param = request_param + \
    '''
                        NSString *%s = params[@"%s"];''' % \
                                (param[1],
                                 param[1])
            elif param[0] == 'bool':
                request_param = request_param + \
    '''
                        BOOL %s = [params[@"%s"] boolValue];''' % \
                                (param[1],
                                 param[1])
            elif param[0] == 'int':
                request_param = request_param + \
    '''
                        NSInteger %s = [params[@"%s"] integerValue];''' % \
                                (param[1],
                                 param[1])
            elif param[0] == 'double':
                request_param = request_param + \
    '''
                        double %s = [params[@"%s"] doubleValue];''' % \
                                (param[1],
                                 param[1])

    func_param = ''
    if len(func[2]) > 0:
        for param in func[2]:
            func_param = func_param + ' ' + param[1] + ':' + param[1]
        func_param = func_param[1:]
        func_param = 'With' + func_param[0].upper() + func_param[1:]
    return \
'''
    {
        FlutterBasicMessageChannel *channel =[FlutterBasicMessageChannel messageChannelWithName:@"%s.%s" binaryMessenger:messenger];
        if (api != nil) {
            [channel setMessageHandler:^(id  message, FlutterReply reply) {
                NSMutableDictionary<NSString *, NSObject *> *wrapped = [NSMutableDictionary new];
                if ([message isKindOfClass:[NSDictionary class]]) {%s
                    %s[api %s%s];
                    wrapped[@"result"] = %s;
                } else {
                    wrapped[@"error"] = @{@"message": @"parse message error"};
                }
                reply(wrapped);
            }];
        } else {
            [channel setMessageHandler:nil];
        }
    }
''' % (plugin_package,
       func[1],
       request_param,
       '' if func[0] == 'void' else '%s result = ' % dart_type_to_oc_type(func[0]),
       func[1],
       func_param,
       'nil' if func[0] == 'void' else ('result' if func[0] == 'String' else '@(result)'))


def create_ios_plugin_api():
    localtime = time.localtime(time.time())
    year = localtime.tm_year
    mon = localtime.tm_mon
    day = localtime.tm_mday
    h_path = project_dir + '/ios/Classes/%sApi.h' % down_line_to_hump(plugin_name)
    h_text = \
'''//
//  %sApi.h
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import <Foundation/Foundation.h>
#import <Flutter/Flutter.h>
#import "%sEventSink.h"

@protocol %sApiDelegate <NSObject>
''' % (down_line_to_hump(plugin_name),
       plugin_author,
       year, mon, day,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name))

    # 创建接口函数
    for field in fields:
        h_text = h_text + create_ios_interface_field(field)
    for func in funcs:
        h_text = h_text + create_ios_interface_function(func)

    h_text = h_text + \
'''
@end

@interface %sApi : NSObject

+ (void)setup:(NSObject<FlutterBinaryMessenger> *)messenger api:(id<%sApiDelegate>)api;

@end

''' % (down_line_to_hump(plugin_name), down_line_to_hump(plugin_name))

    create_file(h_path, h_text)

    m_path = project_dir + '/ios/Classes/%sApi.m' % down_line_to_hump(plugin_name)
    m_text = \
'''//
//  %sApi.m
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import "%sApi.h"

@implementation %sApi

+ (void)setup:(NSObject<FlutterBinaryMessenger> *)messenger api:(id<%sApiDelegate>)api {
''' % (down_line_to_hump(plugin_name),
       plugin_author,
       year, mon, day,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name))

    for field in fields:
        m_text = m_text + create_ios_setup_field_block(field)
    for func in funcs:
        m_text = m_text + create_ios_setup_function_block(func)

    m_text = m_text + '''
}

@end
'''

    create_file(m_path, m_text)


def create_ios_plugin_event_sink():
    localtime = time.localtime(time.time())
    year = localtime.tm_year
    mon = localtime.tm_mon
    day = localtime.tm_mday
    h_path = project_dir + '/ios/Classes/%sEventSink.h' % down_line_to_hump(plugin_name)
    h_text = \
'''//
//  %sEventSink.h
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import <Foundation/Foundation.h>
#import <Flutter/Flutter.h>

@interface %sEventSink : NSObject <FlutterStreamHandler>

@property (nonatomic, copy) FlutterEventSink event;

@end
''' % (down_line_to_hump(plugin_name),
       plugin_author,
       year, mon, day,
       down_line_to_hump(plugin_name))

    create_file(h_path, h_text)

    m_path = project_dir + '/ios/Classes/%sEventSink.m' % down_line_to_hump(plugin_name)
    m_text = \
'''//
//  %sEventSink.m
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import "%sEventSink.h"

@implementation %sEventSink

- (FlutterError * _Nullable)onCancelWithArguments:(id _Nullable)arguments {
    self.event = NULL;
    return nil;
}

- (FlutterError * _Nullable)onListenWithArguments:(id _Nullable)arguments eventSink:(nonnull FlutterEventSink)events {
    self.event = events;
    return nil;
}

@end
''' % (down_line_to_hump(plugin_name),
       plugin_author,
       year, mon, day,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name))

    create_file(m_path, m_text)


def create_ios_implement_field(field):
    return \
'''
- (void)set%s:(%sEventSink *)%s {
    // TODO
}
''' % (field[0].upper() + field[1:], down_line_to_hump(plugin_name), field)


def create_ios_implement_function(func):
    func_result = dart_type_to_oc_type(func[0])
    func_param = ''
    if len(func[2]) > 0:
        for param in func[2]:
            func_param = func_param + ' ' + param[1] + ':(' + dart_type_to_oc_type(param[0]) + ')' + param[1]
        func_param = func_param[1:]
        func_param = 'With' + func_param[0].upper() + func_param[1:]
    func_default_result = ''
    func_default_result = 'return @"";' if func[0] == 'String' else func_default_result
    func_default_result = 'return 0;' if func[0] == 'int' else func_default_result
    func_default_result = 'return NO;' if func[0] == 'bool' else func_default_result
    func_default_result = 'return 0.0;' if func[0] == 'double' else func_default_result
    return \
'''
- (%s)%s%s {
    // TODO
    %s
}
''' % (func_result, func[1], func_param, func_default_result)


def create_ios_plugin():
    localtime = time.localtime(time.time())
    year = localtime.tm_year
    mon = localtime.tm_mon
    day = localtime.tm_mday
    h_path = project_dir + '/ios/Classes/%sPlugin.h' % down_line_to_hump(plugin_name)
    h_text = \
'''//
//  %sPlugin.h
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import <Flutter/Flutter.h>
#import "%sApi.h"

@interface %sPlugin : NSObject<%sApiDelegate>

+ (void)registerWithRegistrar:(NSObject<FlutterPluginRegistrar>*)registrar;

@end
''' % (down_line_to_hump(plugin_name),
       plugin_author,
       year, mon, day,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name))

    create_file(h_path, h_text)

    m_path = project_dir + '/ios/Classes/%sPlugin.m' % down_line_to_hump(plugin_name)
    m_text = \
'''//
//  %sPlugin.m
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import "%sPlugin.h"
#import "%sEventSink.h"

@implementation %sPlugin

+ (void)registerWithRegistrar:(NSObject<FlutterPluginRegistrar>*)registrar {
    %sPlugin* instance = [[%sPlugin alloc] init];
    [%sApi setup:[registrar messenger] api:instance];
}
''' % (down_line_to_hump(plugin_name),
       plugin_author,
       year, mon, day,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name))

    for field in fields:
        m_text = m_text + create_ios_implement_field(field)
    for func in funcs:
        m_text = m_text + create_ios_implement_function(func)

    m_text = m_text + '''
@end
'''

    create_file(m_path, m_text)


if __name__ == '__main__':
    check_flutter2()

    parse_field_and_func()

    # 创建项目目录
    if not os.path.exists(project_dir):
        os.mkdir(project_dir)

    # 创建 .gitignore
    create_git_ignore()

    # 创建 .metadata
    create_mate_data()

    # 创建 .CHANGELOG.md
    create_change_log()

    # 创建 License
    create_license()

    # 创建 README.md
    create_read_me()

    # 创建 project.iml
    create_project_iml()

    # 创建 pubspec.yaml
    create_pubspec_yml()

    # 创建 lib/plugin.dart
    create_plugin_dart()

    # 创建 android/gradle/wrapper/gradle-wrapper.properties
    create_android_gradle_wrapper()

    # 创建 android/.gitignore
    create_android_ignore()

    # 创建 android/build.gradle
    create_android_build_gradle()

    # 创建 android/gradle.properties
    create_android_gradle_properties()

    # 创建 android/settings.gradle
    create_android_settings_gradle()

    # 创建 android/src/main/AndroidManifest.xml
    create_android_manifest()

    # 创建 android/src/main/java/包名/PluginApi.java
    create_android_plugin_api()

    # 创建 android/src/main/java/包名/PluginEventSink.java
    create_android_plugin_event_sink()

    # 创建 android/src/main/java/包名/Plugin.java
    create_android_plugin()

    # 创建 ios/.gitignore
    create_ios_ignore()

    # 创建 ios/plugin.podspec
    create_ios_podspec()

    # 创建 ios/PluginApi.h.m
    create_ios_plugin_api()

    # 创建 ios/PluginEventSink.h.m
    create_ios_plugin_event_sink()

    # 创建 ios/Plugin.h.m
    create_ios_plugin()

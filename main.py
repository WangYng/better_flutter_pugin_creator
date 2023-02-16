import os
import shutil
import time
from typing import Text

from env import project_dir, flutter, plugin_name, plugin_author, plugin_description, plugin_package, root_dir, \
    plugin_org, cover_plugin_file_code
from template import dart_template


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
def parse_template():
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
    elif text == 'Map':
        return 'NSDictionary *'
    elif text == 'List':
        return 'NSArray *'
    else:
        return text


# 创建文本文件
def create_file(path, text, force=False):
    if not os.path.exists(path[:path.rindex('/')]):
        os.makedirs(path[:path.rindex('/')])
    if force or not os.path.exists(path):
        file = open(path, 'w')
        file.write(text)
        file.close()


def create_default_dart_plugin():
    if not os.path.exists(project_dir):
        if not os.path.exists(root_dir):
            os.mkdir(root_dir)
        os.chdir(root_dir)

        # 创建默认插件
        os.system('%s create --org %s --no-pub --template=plugin --platforms=android,ios -i objc -a java %s '
                  % (flutter, plugin_org, plugin_name))

        # 删除 License
        os.remove(os.path.join(project_dir, 'LICENSE'))

        # 删除 pubspec.yaml
        os.remove(os.path.join(project_dir, 'pubspec.yaml'))

        # 删除 lib/plugin.dart
        os.remove(os.path.join(project_dir, 'lib', plugin_name + '.dart'))

        # 删除 lib/plugin_method_channel.dart
        os.remove(os.path.join(project_dir, 'lib', plugin_name + '_method_channel.dart'))

        # 删除 lib/plugin_platform_interface.dart
        os.remove(os.path.join(project_dir, 'lib', plugin_name + '_platform_interface.dart'))

        # 删除 test
        shutil.rmtree(os.path.join(project_dir, 'test'))

        # 删除 android/build.gradle
        os.remove(os.path.join(project_dir, 'android', 'build.gradle'))

        # 删除 android/src/main/java
        shutil.rmtree(os.path.join(project_dir, 'android', 'src', 'main', 'java'))

        # 删除 ios/Classes
        shutil.rmtree(os.path.join(project_dir, 'ios', 'Classes'))

        # 删除 example/pubspec.yaml
        os.remove(os.path.join(project_dir, 'example', 'pubspec.yaml'))

        # 删除 example/lib
        shutil.rmtree(os.path.join(project_dir, 'example', 'lib'))

        # 删除 example/test
        shutil.rmtree(os.path.join(project_dir, 'example', 'test'))


def create_pubspec_yml():
    if is_flutter2:
        sdk_env = '>=2.12.0 <3.0.0'
        flutter_env = '>=2.0.0'
    else:
        sdk_env = '>=2.7.0 <3.0.0'
        flutter_env = '>=1.20.0'

    path = project_dir + "/pubspec.yaml"
    text = '''name: %s
description: %s
version: 0.0.1
publish_to: 'none' # Remove this line if you wish to publish to pub.dev. This is preferred for private packages.

# Uncomment this code block if you wish to publish to pub.dev.
# homepage: https://github.com/WangYng 
# repository: https://github.com/WangYng/better_plugin

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
''' % (plugin_name,
       plugin_description,
       sdk_env,
       flutter_env,
       plugin_package,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name))

    create_file(path, text)


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

    func_result = '''return replyMap["result"];'''
    if func[0].startswith('int'):
        default_result = 'return 0;'
    elif func[0].startswith('String'):
        default_result = 'return \'\';'
    elif func[0].startswith('double'):
        default_result = 'return 0.0;'
    elif func[0].startswith('bool'):
        default_result = 'return false;'
    elif func[0].startswith('Map'):
        default_result = 'return {};'
    elif func[0].startswith('List'):
        default_result = 'return [];'
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


def create_dart_plugin():
    # 创建目录
    if not os.path.exists(project_dir + '/lib'):
        os.mkdir(project_dir + '/lib')

    path = project_dir + '/lib/' + plugin_name + '.dart'

    text = \
'''import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:%s/%s';

class %s {
''' % (plugin_name, plugin_name + '_api.dart', down_line_to_hump(plugin_name))

    # 生成相应的字段
    for field in fields:
        text = text + create_dart_field(field)

    # 生成相应的函数
    for func in funcs:
        text = text + create_dart_func(func)

    # 结束部分
    text = text + \
'''
}

'''

    create_file(path, text, force=cover_plugin_file_code)


def create_dart_plugin_api():
    # 创建目录
    if not os.path.exists(project_dir + '/lib'):
        os.mkdir(project_dir + '/lib')

    api_path = project_dir + '/lib/' + plugin_name + '_api.dart'

    api_text = \
'''
// This file is automatically generated. DO NOT EDIT, all your changes would be lost.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

class %sApi {
''' % down_line_to_hump(plugin_name)

    # 生成相应的字段
    for field in fields:
        api_text = api_text + create_api_dart_field(field)

    # 生成相应的函数
    for func in funcs:
        api_text = api_text + create_api_dart_func(func)

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

    create_file(api_path, api_text, force=True)


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
'''
// This file is automatically generated. DO NOT EDIT, all your changes would be lost.

package %s;

import android.content.Context;

import java.util.HashMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.flutter.embedding.engine.plugins.FlutterPlugin;
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
    static void setup(FlutterPlugin.FlutterPluginBinding binding, %sApi api, Context context) {
        BinaryMessenger binaryMessenger = binding.getBinaryMessenger();
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

    create_file(path, text, force=True)


def create_android_plugin_event_sink():
    path = project_dir + '/android/src/main/java/%s/%sEventSink.java' \
           %\
           (plugin_package.replace('.', '/'), down_line_to_hump(plugin_name))
    text = \
'''
// This file is automatically generated. DO NOT EDIT, all your changes would be lost.

package %s;

import io.flutter.plugin.common.EventChannel;

public class %sEventSink {
    EventChannel.EventSink event;
}
''' % (plugin_package, down_line_to_hump(plugin_name))

    create_file(path, text, force=True)


def create_android_implement_field_declaration(field):
    return \
'''
    private %sEventSink %s;
''' % (down_line_to_hump(plugin_name), field)


def create_android_implement_field(field):
    return \
'''
    @Override
    public void set%s(Context context, %sEventSink %s) {
        this.%s = %s;
    }
''' % (field[0].upper() + field[1:], down_line_to_hump(plugin_name), field, field, field)


def create_android_implement_function(func):
    func_result = dart_type_to_java_type(func[0])
    func_param = 'Context context, '
    if len(func[2]) > 0:
        for param in func[2]:
            func_param = func_param + dart_type_to_java_type(param[0]) + ' ' + param[1] + ', '
    func_param = func_param[:-2]
    func_default_result = ''
    func_default_result = 'return "";' if func[0] == 'String' else func_default_result
    func_default_result = 'return new HashMap();' if func[0] == 'Map' else func_default_result
    func_default_result = 'return new ArrayList();' if func[0] == 'List' else func_default_result
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

    m_field_text = ''
    for field in fields:
        m_field_text = m_field_text + create_android_implement_field_declaration(field)

    text = \
'''package %s;

import android.content.Context;

import androidx.annotation.NonNull;

import java.util.HashMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.flutter.embedding.engine.plugins.FlutterPlugin;

public class %sPlugin implements FlutterPlugin, %sApi {
%s
    @Override
    public void onAttachedToEngine(@NonNull FlutterPluginBinding binding) {
        %sApi.setup(binding, this, binding.getApplicationContext());
    }

    @Override
    public void onDetachedFromEngine(@NonNull FlutterPluginBinding binding) {
        %sApi.setup(binding, null, null);
    }
''' % (plugin_package,
      down_line_to_hump(plugin_name),
      down_line_to_hump(plugin_name),
      m_field_text,
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

    create_file(path, text, force=cover_plugin_file_code)


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
            elif param[0] == 'Map':
                request_param = request_param + \
'''
                    NSDictionary *%s = params[@"%s"];''' % \
                                (param[1],
                                 param[1])
            elif param[0] == 'List':
                request_param = request_param + \
'''
                    NSArray *%s = params[@"%s"];''' % \
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

    func_result = '@(result)'
    if func[0] == 'void':
        func_result = 'nil'
    elif func[0] == 'String':
        func_result = 'result'
    elif func[0] == 'Map':
        func_result = 'result'
    elif func[0] == 'List':
        func_result = 'result'

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
       func_result)


def create_ios_plugin_api():
    localtime = time.localtime(time.time())
    year = localtime.tm_year
    mon = localtime.tm_mon
    day = localtime.tm_mday
    h_path = project_dir + '/ios/Classes/%sApi.h' % down_line_to_hump(plugin_name)
    h_text = \
'''
// This file is automatically generated. DO NOT EDIT, all your changes would be lost.

//
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

+ (void)setup:(NSObject<FlutterPluginRegistrar> *)registrar api:(id<%sApiDelegate>)api;

@end

''' % (down_line_to_hump(plugin_name), down_line_to_hump(plugin_name))

    create_file(h_path, h_text, force=True)

    m_path = project_dir + '/ios/Classes/%sApi.m' % down_line_to_hump(plugin_name)
    m_text = \
'''
// This file is automatically generated. DO NOT EDIT, all your changes would be lost.

//
//  %sApi.m
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import "%sApi.h"

@implementation %sApi

+ (void)setup:(NSObject<FlutterPluginRegistrar> *)registrar api:(id<%sApiDelegate>)api {
    NSObject<FlutterBinaryMessenger> *messenger = [registrar messenger];
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

    create_file(m_path, m_text, force=True)


def create_ios_plugin_event_sink():
    localtime = time.localtime(time.time())
    year = localtime.tm_year
    mon = localtime.tm_mon
    day = localtime.tm_mday
    h_path = project_dir + '/ios/Classes/%sEventSink.h' % down_line_to_hump(plugin_name)
    h_text = \
'''
// This file is automatically generated. DO NOT EDIT, all your changes would be lost.

//
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

    create_file(h_path, h_text, force=True)

    m_path = project_dir + '/ios/Classes/%sEventSink.m' % down_line_to_hump(plugin_name)
    m_text = \
'''
// This file is automatically generated. DO NOT EDIT, all your changes would be lost.

//
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

    create_file(m_path, m_text, force=True)


def create_ios_implement_field(field):
    return \
'''
@property (nonatomic, strong) %sEventSink *%s;
''' % (down_line_to_hump(plugin_name), field)


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
    func_default_result = 'return @{};' if func[0] == 'Map' else func_default_result
    func_default_result = 'return @[];' if func[0] == 'List' else func_default_result
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

    create_file(h_path, h_text, force=cover_plugin_file_code)

    m_path = project_dir + '/ios/Classes/%sPlugin.m' % down_line_to_hump(plugin_name)

    m_field_text = ''
    for field in fields:
        m_field_text = m_field_text + create_ios_implement_field(field)

    m_text = \
'''//
//  %sPlugin.m
//  Pods
//
//  Created by %s on %s/%s/%s.
//

#import "%sPlugin.h"
#import "%sEventSink.h"

@interface %sPlugin()
%s
@end

@implementation %sPlugin

+ (void)registerWithRegistrar:(NSObject<FlutterPluginRegistrar>*)registrar {
    %sPlugin* instance = [[%sPlugin alloc] init];
    [%sApi setup:registrar api:instance];
}
''' % (down_line_to_hump(plugin_name),
       plugin_author,
       year, mon, day,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       m_field_text,
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name),
       down_line_to_hump(plugin_name))

    for func in funcs:
        m_text = m_text + create_ios_implement_function(func)

    m_text = m_text + '''
@end
'''

    create_file(m_path, m_text, force=cover_plugin_file_code)


def create_example_pubspec_yml():
    if is_flutter2:
        sdk_env = '>=2.12.0 <3.0.0'
        flutter_env = '>=2.0.0'
    else:
        sdk_env = '>=2.7.0 <3.0.0'
        flutter_env = '>=1.20.0'

    path = os.path.join(project_dir, 'example', 'pubspec.yaml')
    text = \
'''name: %s_example
description: Demonstrates how to use the better_test plugin.

# The following line prevents the package from being accidentally published to
# pub.dev using `pub publish`. This is preferred for private packages.
publish_to: 'none' # Remove this line if you wish to publish to pub.dev

environment:
  sdk: "%s"
  flutter: "%s"

dependencies:
  flutter:
    sdk: flutter

  %s:
    # When depending on this package from a real application you should use:
    #   better_test: ^x.y.z
    # See https://dart.dev/tools/pub/dependencies#version-constraints
    # The example app is bundled with the plugin so we use a path dependency on
    # the parent directory to use the current plugin's version.
    path: ../

dev_dependencies:
  flutter_test:
    sdk: flutter

# For information on the generic Dart part of this file, see the
# following page: https://dart.dev/tools/pub/pubspec

# The following section is specific to Flutter.
flutter:

  # The following line ensures that the Material Icons font is
  # included with your application, so that you can use the icons in
  # the material Icons class.
  uses-material-design: true

  # To add assets to your application, add an assets section, like this:
  # assets:
  #   - images/a_dot_burr.jpeg
  #   - images/a_dot_ham.jpeg

  # An image asset can refer to one or more resolution-specific "variants", see
  # https://flutter.dev/assets-and-images/#resolution-aware.

  # For details regarding adding assets from package dependencies, see
  # https://flutter.dev/assets-and-images/#from-packages

  # To add custom fonts to your application, add a fonts section here,
  # in this "flutter" section. Each entry in this list should have a
  # "family" key with the font family name, and a "fonts" key with a
  # list giving the asset and other descriptors for the font. For
  # example:
  # fonts:
  #   - family: Schyler
  #     fonts:
  #       - asset: fonts/Schyler-Regular.ttf
  #       - asset: fonts/Schyler-Italic.ttf
  #         style: italic
  #   - family: Trajan Pro
  #     fonts:
  #       - asset: fonts/TrajanPro.ttf
  #       - asset: fonts/TrajanPro_Bold.ttf
  #         weight: 700
  #
  # For details regarding fonts from package dependencies,
  # see https://flutter.dev/custom-fonts/#from-packages

''' % (plugin_name, sdk_env, flutter_env, plugin_name)

    create_file(path, text)


def create_example_main_dart():
    path = os.path.join(project_dir, 'example', 'lib', 'main.dart')
    text = \
'''import 'package:flutter/material.dart';
import 'dart:async';

import 'package:flutter/services.dart';
import 'package:%s/%s.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: const Text('Plugin example app'),
        ),
        body: Center(
          child: Text('Running'),
        ),
      ),
    );
  }
}

''' % (plugin_name, plugin_name)

    create_file(path, text)


if __name__ == '__main__':

    # 判断当前的flutter环境
    check_flutter2()

    # 解析模板
    parse_template()

    # 创建默认插件
    create_default_dart_plugin()

    # 创建 pubspec.yaml
    create_pubspec_yml()

    # 创建 lib/plugin.dart
    create_dart_plugin()

    # 创建 lib/plugin_api.dart
    create_dart_plugin_api()

    # 创建 android/build.gradle
    create_android_build_gradle()

    # 创建 android/src/main/java/包名/PluginApi.java
    create_android_plugin_api()

    # 创建 android/src/main/java/包名/PluginEventSink.java
    create_android_plugin_event_sink()

    # 创建 android/src/main/java/包名/Plugin.java
    create_android_plugin()

    # 创建 ios/PluginApi.h.m
    create_ios_plugin_api()

    # 创建 ios/PluginEventSink.h.m
    create_ios_plugin_event_sink()

    # 创建 ios/Plugin.h.m
    create_ios_plugin()

    # 创建 example/pubspec.yaml
    create_example_pubspec_yml()

    # 创建 example/lib/main.dart
    create_example_main_dart()

    print("创建Flutter插件完成")

> * 学习前的准备
> * 最常用的输出
> * 必学会的输入


### 1. 学习前的准备
关于Python的**安装**以及**环境配置**可以先参考以下文章

### [Python的环境搭建](https://www.u3v3.com/ar/1246)
### [windows python 环境安装和配置](https://www.u3v3.com/ar/1361)
### [wMac pycharm环境配置](https://www.u3v3.com/ar/1320)

> 此课程所有讲解到的语法知识都是基于Python3的，Python3在设计的时候没有考虑向下兼容，所以遇到任何问题可以在QQ群（278529278）或者文章底部评论留言，我们会一一解答，谢谢大家配合。

------

### 2. 最常用的输出

标签： 先高亮一段代码
```
# 变量的定义
x="Hello"
y="Word"

# 换行输出
print( x )
print( y )

print('---------')

# 不换行输出
print( x, end=" " )
print( y, end=" " )
print()
```

------

## 关于变量的定义
Python是一种动态类型语言，在赋值的执行中可以绑定不同类型的值，这个过程叫做变量(variable)赋值操作，赋值同时确定了变量类型。

变量定义方法很简单：
```
x="Hello"
y="Word"
```
这个操作过程就是赋值，意思把字符串Hello和Word分别赋值给了变量x和y，用等号来连接变量名和值。之后就可以在表达式中使用这个新变量了。

<i class="icon-pencil"></i>注意：在赋值时，值是什么数据类型，就决定了这个变量是什么类型，变量名引用了字符串的同时也引用了它的类型。

- [x] 变量命名规范
1、变量名可以包括字母、数字、下划线，但是数字不能做为开头。例如：Hello1是合法变量名，而1World就不可以。
2、系统关键字不能做变量名使用，例如：print。
3、除了下划线之个，其它符号不能做为变量名使用，例如：（）！@#￥%。
4、Python的变量名是对大小写敏感的，例如：Hello和hello就是两个变量名，而非相同变量的(⊙o⊙)哦。

## 关于输出
通常情况下想查看变量结果或是内容时，在代码中会用到最常用的print输出。

- [x] print语句操作方法：
```flow
st=>start: 定义变量
op=>operation: 输出print
cond=>condition: 使用python命令执行是否通过
e=>end

st->op->cond
cond(yes)->e
cond(no)->op
```

```
# 变量的定义
x="Hello"
y="Word"

# 换行输出
print(x)
print(y)
```

- [x] print语句不换行操作：
```
# 变量的定义
x="Hello"
y="Word"

# 不换行输出
print(x, end=" ")
print(y, end=" ")
print()
```
print默认输出是换行的，如果要实现不换行需要在变量末尾加上 end=""。


### 3. 必学会的输入
```
str = input ("请您输入：")
print("您输入的内容是：",str,"，谢谢。")
```
Python中默认的编码格式是ASCII格式，在没修改编码格式时无法正确打印汉字，所以在读取中文时会报错。解决方法为只要在文件开头加入 # -*- coding: UTF-8 -*- 或者 #coding=utf-8 就行了。
```
# -*- coding: UTF-8 -*-
str = input ("请您输入：")
print("您输入的内容是：",str,"，谢谢。")
```

# 本程序只做学习用途，请勿非法用途
# verifyemail Python3.6.5

Python在线验证邮箱真实性，支持批量验证

## Tips
1.目前不支持企业邮箱验证
2.批量验证请增加timeout时间 以及增大间隔时间 避免被封

## 对比原版变化
更新内容重构邮箱验证脚本，新增格式校验和错误处理
1. 新增邮箱格式正则校验函数
2. 替换旧的dns.resolver.query为resolve并添加异常捕获
3. 重构代码结构，提取配置常量
4. 优化输入处理和日志输出
5. 使用with语句管理SMTP连接，添加请求间隔控制

---

## Credit & License

This project is a fork of **[verifyemail](https://github.com/Tzeross/verifyemail)** 
by [Tzeross]

if you like this fork, please also star and credit the original.
